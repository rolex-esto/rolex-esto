#!/usr/bin/env python3
"""Generate real-data GitHub graphics (dark + light SVG) for the profile README:
the activity and languages cards, and the "Developer Overview" panel (account
totals, 12-month activity, isometric 3D contribution graph, contribution calendar).

Runs in the "Generate profile graphics" workflow with the built-in GITHUB_TOKEN,
so no third-party stats service is needed. Language totals use only PUBLIC,
non-fork repositories owned by the user.

Safety: the script never writes partial output. It retries transient API errors,
sanity-checks the data, renders every SVG in memory, validates it as XML, and
only then writes the files. On any failure it exits non-zero, so the workflow
stops before publishing and the previously published images stay in place.

Usage:  GITHUB_TOKEN=... python3 scripts/generate-github-stats.py <login> <out_dir>
"""
import base64
import datetime as dt
import json
import math
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.dom.minidom
from html import escape

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    login
    name
    createdAt
    avatarUrl(size: 128)
    followers { totalCount }
    publicRepos: repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date weekday contributionCount contributionLevel } } }
    }
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
  }
}"""
MAX_REPO_PAGES = 10

THEMES = {
    "dark": dict(bg="#0D1117", panel="#161B22", border="#30363D", title="#70F5A3", text="#E6EDF3", muted="#9DA7B3", accent="#B7A2FF", track="#21262D"),
    "light": dict(bg="#FFFFFF", panel="#F6F8FA", border="#D0D7DE", title="#0E7A45", text="#1F2328", muted="#57606A", accent="#6D4ED8", track="#EAEEF2"),
}
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


class StatsError(Exception):
    pass


def fetch(login, token, attempts=3, after=None):
    body = json.dumps({"query": QUERY, "variables": {"login": login, "after": after}}).encode()
    last = None
    for i in range(attempts):
        req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
            "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats-generator"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                payload = json.load(r)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (401, 403, 404):  # not transient
                break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last = repr(e)
        else:
            if payload.get("errors"):
                raise StatsError(f"GraphQL error: {payload['errors']}")
            user = (payload.get("data") or {}).get("user")
            if not user:
                raise StatsError("GraphQL returned no user")
            return user
        time.sleep(2 * (i + 1))
    raise StatsError(f"GitHub API request failed after retries: {last}")


def fetch_all(login, token, fetch_page=None):
    """First page plus any further pages of owned public repositories (for stars and languages)."""
    fetch_page = fetch_page or fetch
    user = fetch_page(login, token)
    repos = user["repositories"]
    for _ in range(MAX_REPO_PAGES - 1):
        if not repos["pageInfo"]["hasNextPage"]:
            break
        nxt = fetch_page(login, token, after=repos["pageInfo"]["endCursor"])["repositories"]
        repos["nodes"].extend(nxt["nodes"])
        repos["pageInfo"] = nxt["pageInfo"]
    if repos["pageInfo"]["hasNextPage"]:
        raise StatsError("Too many repositories to page through")
    return user


def fetch_avatar(url, limit=200_000):
    """Avatar as a data: URI (an <img>-embedded SVG cannot load external images). None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "profile-stats-generator"})
        with urllib.request.urlopen(req, timeout=20) as r:
            ctype = r.headers.get_content_type()
            data = r.read(limit + 1)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None
    if ctype not in ("image/png", "image/jpeg", "image/gif", "image/webp") or not data or len(data) > limit:
        return None
    return f"data:{ctype};base64,{base64.b64encode(data).decode()}"


def streaks(days):
    """Current streak (today may still be 0) and longest streak in the window."""
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    current = 0
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1  # today (UTC) is not over yet
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1
    return current, longest


def summarize(u):
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    if len(days) < 300:
        raise StatsError(f"Contribution calendar looks incomplete ({len(days)} days)")
    cur, longest = streaks(days)
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, {"size": 0, "color": e["node"]["color"] or "#8B949E"})
            langs[n]["size"] += e["size"]
    total = sum(v["size"] for v in langs.values())
    top = sorted(langs.items(), key=lambda kv: -kv[1]["size"])[:6]
    stars = sum(r.get("stargazerCount") or 0 for r in u["repositories"]["nodes"])
    s = {
        "login": u.get("login") or "",
        "name": u.get("name") or u.get("login") or "",
        "created": (u.get("createdAt") or "")[:10],
        "avatar_url": u.get("avatarUrl") or "",
        "followers": (u.get("followers") or {}).get("totalCount"),
        "public_repos": (u.get("publicRepos") or {}).get("totalCount"),
        "stars": stars,
        "issues": cc.get("totalIssueContributions"),
        "days": [{"date": d["date"], "weekday": d.get("weekday", 0), "count": d["contributionCount"],
                  "level": d.get("contributionLevel") or ("NONE" if d["contributionCount"] == 0 else "FIRST_QUARTILE")}
                 for d in days],
        "start": days[0]["date"],
        "end": days[-1]["date"],
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "private_counts": cc["restrictedContributionsCount"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "repos_committed": cc["totalRepositoriesWithContributedCommits"],
        "current_streak": cur,
        "longest_streak": longest,
        "languages": [(n, v["color"], v["size"] / total) for n, v in top] if total else [],
        "window": f"{days[0]['date']} to {days[-1]['date']}",
    }
    for k in ("contributions", "commits", "prs", "repos_committed", "current_streak", "longest_streak",
              "followers", "public_repos", "stars", "issues"):
        if not isinstance(s[k], int) or s[k] < 0:
            raise StatsError(f"Unexpected value for {k}: {s[k]!r}")
    return s


def corner(x, y, c):
    return f'<path fill="{c}" d="M{x} {y}h14v4h-10v10h-4z"/>'


# Cards are 400 units wide so that at a 254 px README column (320 px phone)
# labels stay >= ~9 px and values >= ~17 px; at 390 px phones labels are ~12 px.
def activity_card(s, t):
    W, H = 400, 300
    items = [
        (f'{s["contributions"]:,}', "Contributions*"), (f'{s["commits"]:,}', "Public commits"),
        (f'{s["current_streak"]} days', "Current streak*"), (f'{s["longest_streak"]} days', "Longest streak*"),
        (f'{s["prs"]:,}', "Public pull requests"), (f'{s["repos_committed"]:,}', "Public repos committed to"),
    ]
    desc = ", ".join(f"{label.rstrip('*')}: {val}" for val, label in items)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">GitHub activity, last 12 months</title>',
         f'<desc id="d">{escape(desc)}. Starred values include private contribution counts shown on the profile ({s["private_counts"]:,} private). Window {escape(s["window"])} (UTC).</desc>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>',
         corner(16, 16, t["title"]),
         f'<text x="38" y="34" font-family="{FONT}" font-size="18" font-weight="700" fill="{t["title"]}">Activity · last 12 months</text>']
    for i, (val, label) in enumerate(items):
        col, row = i % 2, i // 2
        x, y = 16 + col * 188, 50 + row * 72
        o.append(f'<rect x="{x}" y="{y}" width="180" height="64" rx="8" fill="{t["panel"]}"/>')
        o.append(f'<text x="{x + 12}" y="{y + 30}" font-family="{FONT}" font-size="26" font-weight="700" fill="{t["text"]}">{escape(val)}</text>')
        o.append(f'<text x="{x + 12}" y="{y + 52}" font-family="{FONT}" font-size="14" fill="{t["muted"]}">{escape(label)}</text>')
    o.append(f'<text x="16" y="{H - 14}" font-family="{FONT}" font-size="13" fill="{t["muted"]}">* includes private contribution counts · updated daily</text>')
    o.append("</svg>")
    return "\n".join(o)


def languages_card(s, t):
    W, H = 400, 300
    langs = s["languages"]
    desc = ", ".join(f"{n} {p * 100:.1f}%" for n, _, p in langs) or "No language data"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">Most used languages in public repositories</title>',
         f'<desc id="d">{escape(desc)}. By code size across public, non-fork repositories.</desc>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>',
         corner(16, 16, t["accent"]),
         f'<text x="38" y="34" font-family="{FONT}" font-size="18" font-weight="700" fill="{t["accent"]}">Languages · public repos</text>',
         f'<rect x="16" y="54" width="{W - 32}" height="12" rx="6" fill="{t["track"]}"/>']
    x = 16.0
    for n, c, p in langs:
        w = (W - 32) * p
        o.append(f'<rect x="{x:.1f}" y="54" width="{w:.1f}" height="12" fill="{c}"/>')
        x += w
    for i, (n, c, p) in enumerate(langs):
        y = 100 + i * 28
        o.append(f'<rect x="20" y="{y - 12}" width="12" height="12" fill="{c}"/>')
        o.append(f'<text x="42" y="{y}" font-family="{FONT}" font-size="16" fill="{t["text"]}">{escape(n)}</text>')
        o.append(f'<text x="{W - 20}" y="{y}" text-anchor="end" font-family="{FONT}" font-size="16" fill="{t["muted"]}">{p * 100:.1f}%</text>')
    if not langs:
        o.append(f'<text x="20" y="110" font-family="{FONT}" font-size="16" fill="{t["muted"]}">No language data yet</text>')
    o.append(f'<text x="16" y="{H - 14}" font-family="{FONT}" font-size="13" fill="{t["muted"]}">By code size · forks excluded · updated daily</text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------------------
# Developer Overview panel (left half of the README dashboard).
# 410 units wide, shown at width="410": side by side with the static portfolio
# panel on desktop, wrapping to one full-width column on phones.
# Smallest text is 13 units (~9 px on a 320 px phone, ~12 px on desktop).
# ---------------------------------------------------------------------------
DASH = {
    "dark": dict(bg="#0D1117", surface="#161B22", border="#30363D", teal="#00C389", sky="#0EA5E9", purple="#A78BFA",
                 text="#C9D1D9", strong="#F0F6FC", muted="#8B949E", shadow="#010409",
                 levels={"NONE": "#21262D", "FIRST_QUARTILE": "#0E4429", "SECOND_QUARTILE": "#006D4A",
                         "THIRD_QUARTILE": "#14A37F", "FOURTH_QUARTILE": "#00C389"}),
    "light": dict(bg="#FFFFFF", surface="#F6F8FA", border="#D0D7DE", teal="#00875F", sky="#0369A1", purple="#6D28D9",
                  text="#1F2328", strong="#1F2328", muted="#57606A", shadow="#D0D7DE",
                  levels={"NONE": "#EBEDF0", "FIRST_QUARTILE": "#A7F0CF", "SECOND_QUARTILE": "#4FD6A6",
                          "THIRD_QUARTILE": "#14A37F", "FOURTH_QUARTILE": "#00875F"}),
}
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
OVERVIEW_W, OVERVIEW_H = 410, 772


def shade(hex_color, f):
    """Darken (f < 1) or lighten (f > 1) a #RRGGBB colour."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if f <= 1:
        r, g, b = (round(c * f) for c in (r, g, b))
    else:
        r, g, b = (round(c + (255 - c) * (f - 1)) for c in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def fmt_date(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def week_grid(days):
    """Group days into Sunday-first weeks: list of (week_index, weekday, day)."""
    out, w = [], 0
    for i, d in enumerate(days):
        if i and d["weekday"] == 0:
            w += 1
        out.append((w, d["weekday"], d))
    return out


def isometric(days, t, ox, oy, a=6.2, b=3.1, max_h=60.0):
    """Isometric 3D contribution graph. Week axis runs right-down, weekday axis left-down.
    Block height follows the real daily count (sqrt scale, so busy days do not flatten the rest)."""
    cells = week_grid(days)
    peak = max((d["count"] for _, _, d in cells), default=0)
    o = [f'<polygon points="{ox:.1f},{oy - 4:.1f} {ox + 54 * a + 6:.1f},{oy + 54 * b - 1:.1f} '
         f'{ox + 47 * a:.1f},{oy + 61 * b + 6:.1f} {ox - 7 * a - 6:.1f},{oy + 7 * b - 1:.1f}" '
         f'fill="{t["shadow"]}" opacity="0.55"/>']
    s = 0.86  # tile inset: keeps a hairline gap between blocks
    for w, wd, d in sorted(cells, key=lambda c: (c[0] + c[1], c[0])):
        x, y = ox + (w - wd) * a, oy + (w + wd) * b
        cx, cy = x, y + b  # centre of the top face at ground level
        h = 1.2 if d["count"] == 0 or peak == 0 else 3 + (max_h - 3) * math.sqrt(d["count"] / peak)
        top = t["levels"].get(d["level"], t["levels"]["NONE"])
        hi = shade(top, 1.18)
        T = (cx, cy - b * s - h); R = (cx + a * s, cy - h); B = (cx, cy + b * s - h); L = (cx - a * s, cy - h)
        pts = lambda *ps: " ".join(f"{px:.1f},{py:.1f}" for px, py in ps)
        o.append(f'<polygon points="{pts(L, B, (B[0], B[1] + h), (L[0], L[1] + h))}" fill="{shade(top, 0.72)}"/>')
        o.append(f'<polygon points="{pts(B, R, (R[0], R[1] + h), (B[0], B[1] + h))}" fill="{shade(top, 0.52)}"/>')
        o.append(f'<polygon points="{pts(T, R, B, L)}" fill="{top}"/>')
        if d["count"] and h > 20:  # light edge on tall towers
            o.append(f'<polyline points="{pts(L, T, R)}" fill="none" stroke="{hi}" stroke-width="0.6"/>')
    return "\n".join(o), peak


def calendar(days, t, x0, y0, cell=6, gap=1):
    o = []
    for w, wd, d in week_grid(days):
        o.append(f'<rect x="{x0 + w * (cell + gap)}" y="{y0 + wd * (cell + gap)}" width="{cell}" height="{cell}" '
                 f'rx="1" fill="{t["levels"].get(d["level"], t["levels"]["NONE"])}"/>')
    return "\n".join(o)


def avatar(uri, t, cx, cy, r, initials):
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r + 3}" fill="none" stroke="{t["teal"]}" stroke-width="2"/>']
    if uri:
        o.append(f'<clipPath id="av"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
        o.append(f'<image href="{uri}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#av)"/>')
    else:  # avatar download failed: initials instead of a broken image
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{t["surface"]}"/>')
        o.append(f'<text x="{cx}" y="{cy + 7}" text-anchor="middle" font-family="{FONT}" font-size="20" '
                 f'font-weight="700" fill="{t["teal"]}">{escape(initials)}</text>')
    return "\n".join(o)


def overview_card(s, t, avatar_uri=None):
    W, H = OVERVIEW_W, OVERVIEW_H
    txt = lambda x, y, v, size=13, fill=None, weight="400", anchor="start": (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill or t["muted"]}">{escape(str(v))}</text>')
    joined = fmt_date(s["created"]) if s["created"] else "unavailable"
    period = f'{fmt_date(s["start"])} – {fmt_date(s["end"])}'
    account = [(f'{s["public_repos"]:,}', "Public repos"), (f'{s["followers"]:,}', "Followers"),
               (f'{s["stars"]:,}', "Stars earned")]
    yearly = [(f'{s["commits"]:,}', "Public commits"), (f'{s["prs"]:,}', "Public PRs"), (f'{s["issues"]:,}', "Public issues"),
              (f'{s["repos_committed"]:,} repos', "Committed to"), (f'{s["current_streak"]}d', "Current streak*"),
              (f'{s["longest_streak"]}d', "Longest streak*")]
    desc = (f'{s["name"]} (@{s["login"]}), on GitHub since {joined}. Account: '
            + ", ".join(f"{l} {v}" for v, l in account)
            + f'. {period} (UTC): {s["contributions"]:,} contributions (incl. {s["private_counts"]:,} private), '
            + ", ".join(f"{l.rstrip('*')} {v}" for v, l in yearly) + ".")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">GitHub activity and contributions</title>', f'<desc id="d">{escape(desc)}</desc>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>',
         avatar(avatar_uri, t, 48, 52, 28, "".join(p[0] for p in s["name"].split()[:2]).upper() or "?"),
         txt(92, 46, s["name"], 20, t["strong"], "700"),
         txt(92, 70, f'@{s["login"]} · on GitHub since {joined}', 14)]

    def grid(items, y):
        for i, (val, label) in enumerate(items):
            x, yy = 16 + (i % 3) * 128, y + (i // 3) * 64
            o.append(f'<rect x="{x}" y="{yy}" width="122" height="58" rx="8" fill="{t["surface"]}" stroke="{t["border"]}"/>')
            o.append(txt(x + 10, yy + 27, val, 22, t["strong"], "700"))
            o.append(txt(x + 10, yy + 47, label, 13))

    o.append(txt(16, 114, "ACCOUNT TOTALS", 13, t["sky"], "700"))
    grid(account, 124)
    o.append(txt(16, 214, "LAST 12 MONTHS", 13, t["teal"], "700"))
    o.append(txt(W - 16, 214, period, 13, anchor="end"))
    grid(yearly, 224)
    o.append(txt(16, 378, "3D CONTRIBUTIONS", 13, t["purple"], "700"))
    iso, peak = isometric(s["days"], t, ox=16 + 7 * 6.2 + 4, oy=438)
    o.append(iso)
    best = max(s["days"], key=lambda d: d["count"]) if s["days"] else None
    o.append(txt(W - 16, 378, f'busiest day*: {peak} on {fmt_date(best["date"])}' if peak else "no contributions yet",
                 13, anchor="end"))
    o.append(calendar(s["days"], t, x0=19, y0=656))
    o.append(txt(16, 732, f'{s["contributions"]:,} contributions* in the last year', 13, t["text"], "600"))
    lx = W - 16 - 5 * 12 - 34
    o.append(txt(lx - 6, 732, "Less", 13, anchor="end"))
    for i, lv in enumerate(LEVELS):
        o.append(f'<rect x="{lx + i * 12}" y="722" width="10" height="10" rx="2" fill="{t["levels"][lv]}"/>')
    o.append(txt(W - 16, 732, "More", 13, anchor="end"))
    o.append(txt(16, 756, "* includes private contribution counts · updated daily", 13))
    o.append("</svg>")
    return "\n".join(o)


def main():
    login = sys.argv[1] if len(sys.argv) > 1 else "rolex-esto"
    out = sys.argv[2] if len(sys.argv) > 2 else "dist"
    token = os.environ.get("GITHUB_TOKEN")
    try:
        if not token:
            raise StatsError("GITHUB_TOKEN is required")
        s = summarize(fetch_all(login, token))
        avatar_uri = fetch_avatar(s["avatar_url"]) if s["avatar_url"] else None
        if not avatar_uri:
            print("::warning::avatar download failed; overview uses initials", file=sys.stderr)
        rendered = {}
        for name, t in THEMES.items():
            rendered[f"stats-activity-{name}.svg"] = activity_card(s, t)
            rendered[f"stats-languages-{name}.svg"] = languages_card(s, t)
            rendered[f"overview-activity-{name}.svg"] = overview_card(s, DASH[name], avatar_uri)
        for fname, svg in rendered.items():
            xml.dom.minidom.parseString(svg)  # raises on malformed output
    except Exception as e:  # noqa: BLE001 - any failure must stop the publish
        print(f"::error::stats generation failed, nothing written: {e}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(out, exist_ok=True)
    for fname, svg in rendered.items():
        fd, tmp = tempfile.mkstemp(dir=out, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            f.write(svg + "\n")
        os.replace(tmp, os.path.join(out, fname))  # atomic per file
    print(json.dumps({k: v for k, v in s.items() if k not in ("languages", "days")}, indent=2))
    print("languages:", [(n, round(p * 100, 1)) for n, _, p in s["languages"]])


if __name__ == "__main__":
    main()
