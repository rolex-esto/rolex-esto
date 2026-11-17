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
    "dark": dict(bg="#0B0F19", panel="#171C2B", border="#394156", title="#A8D8B9", text="#F5EBD7", muted="#A6ADBB", accent="#B8A4FF", track="#232A3B"),
    "light": dict(bg="#FBF8F2", panel="#F3EEE4", border="#D6CCBA", title="#2E6E4A", text="#2B2638", muted="#5C5768", accent="#6B54D6", track="#E9E2D4"),
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
    o.append(f'<text x="16" y="{H - 14}" font-family="{FONT}" font-size="15" fill="{t["muted"]}">By code size · forks excluded · updated daily</text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------------------
# Developer Overview panel (left half of the README dashboard).
# Theme: Midnight Pixel (dark) / Pastel Dusk (light), shared with
# scripts/generate-dashboard-art.py. PANEL_W x PANEL_H matches that panel; both are
# shown at width="410": side by side on desktop, stacked full width on phones.
# No text is smaller than 16 units (about 10 px on a 320 px phone, 12+ px from 375 px).
# ---------------------------------------------------------------------------
DASH = {
    "dark": dict(bg="#0B0F19", surface="#171C2B", surface2="#232A3B", border="#394156", text="#F5EBD7",
                 muted="#A6ADBB", accent="#B8A4FF", accent2="#A8C7FA", success="#A8D8B9", highlight="#FFD6A5",
                 shadow="#05070D", edge="#E3F4E8",
                 levels={"NONE": "#232A3B", "FIRST_QUARTILE": "#3F5C4D", "SECOND_QUARTILE": "#5F8C72",
                         "THIRD_QUARTILE": "#84B497", "FOURTH_QUARTILE": "#A8D8B9"}),
    "light": dict(bg="#FBF8F2", surface="#F3EEE4", surface2="#E9E2D4", border="#D6CCBA", text="#2B2638",
                  muted="#5C5768", accent="#6B54D6", accent2="#345F9E", success="#2E6E4A", highlight="#9A4F12",
                  shadow="#D6CCBA", edge="#FFFFFF",
                  levels={"NONE": "#E9E2D4", "FIRST_QUARTILE": "#C9E6D3", "SECOND_QUARTILE": "#A8D8B9",
                          "THIRD_QUARTILE": "#72B08A", "FOURTH_QUARTILE": "#4A9068"}),
}
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
PANEL_W, PANEL_H = 410, 1012
MIN_TEXT = 16


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


def account_age(created, today):
    """Whole years and months between two ISO dates, e.g. '2 years' or '1 year, 3 months'."""
    a, b = dt.date.fromisoformat(created), dt.date.fromisoformat(today)
    months = (b.year - a.year) * 12 + b.month - a.month - (b.day < a.day)
    y, m = divmod(max(months, 0), 12)
    parts = ([f"{y} year{'s' * (y != 1)}"] if y else []) + ([f"{m} month{'s' * (m != 1)}"] if m else [])
    return ", ".join(parts) or "under a month"


def week_grid(days):
    """Group days into Sunday-first weeks: list of (week_index, weekday, day)."""
    out, w = [], 0
    for i, d in enumerate(days):
        if i and d["weekday"] == 0:
            w += 1
        out.append((w, d["weekday"], d))
    return out


def isometric(days, t, ox, oy, a=6.2, b=3.1, max_h=64.0):
    """Isometric 3D contribution graph. Week axis runs right-down, weekday axis left-down.
    Block height follows the real daily count (sqrt scale, so busy days do not flatten the rest)."""
    cells = week_grid(days)
    peak = max((d["count"] for _, _, d in cells), default=0)
    o = [f'<polygon points="{ox:.1f},{oy - 4:.1f} {ox + 54 * a + 6:.1f},{oy + 54 * b - 1:.1f} '
         f'{ox + 47 * a:.1f},{oy + 61 * b + 6:.1f} {ox - 7 * a - 6:.1f},{oy + 7 * b - 1:.1f}" '
         f'fill="{t["shadow"]}" opacity="0.6"/>']
    s = 0.86  # tile inset: keeps a hairline gap between blocks
    for w, wd, d in sorted(cells, key=lambda c: (c[0] + c[1], c[0])):
        x, y = ox + (w - wd) * a, oy + (w + wd) * b
        cx, cy = x, y + b  # centre of the top face at ground level
        h = 1.2 if d["count"] == 0 or peak == 0 else 3 + (max_h - 3) * math.sqrt(d["count"] / peak)
        top = t["levels"].get(d["level"], t["levels"]["NONE"])
        T = (cx, cy - b * s - h); R = (cx + a * s, cy - h); B = (cx, cy + b * s - h); L = (cx - a * s, cy - h)
        pts = lambda *ps: " ".join(f"{px:.1f},{py:.1f}" for px, py in ps)
        o.append(f'<polygon points="{pts(L, B, (B[0], B[1] + h), (L[0], L[1] + h))}" fill="{shade(top, 0.74)}"/>')
        o.append(f'<polygon points="{pts(B, R, (R[0], R[1] + h), (B[0], B[1] + h))}" fill="{shade(top, 0.56)}"/>')
        o.append(f'<polygon points="{pts(T, R, B, L)}" fill="{top}"/>')
        if d["count"] and h > 18:  # soft pastel rim light on tall towers
            o.append(f'<polyline points="{pts(L, T, R)}" fill="none" stroke="{t["edge"]}" stroke-opacity="0.55" stroke-width="0.7"/>')
    return "\n".join(o), peak


def calendar(days, t, x0, y0, cell=6, gap=1):
    o = []
    for w, wd, d in week_grid(days):
        o.append(f'<rect x="{x0 + w * (cell + gap)}" y="{y0 + wd * (cell + gap)}" width="{cell}" height="{cell}" '
                 f'rx="1" fill="{t["levels"].get(d["level"], t["levels"]["NONE"])}"/>')
    return "\n".join(o)


def avatar(uri, t, cx, cy, r, initials):
    o = [f'<rect x="{cx - r - 5}" y="{cy - r - 5}" width="{2 * r + 10}" height="{2 * r + 10}" rx="10" fill="{t["surface2"]}" '
         f'stroke="{t["accent"]}" stroke-width="2"/>']
    if uri:
        o.append(f'<clipPath id="av"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" rx="7"/></clipPath>')
        o.append(f'<image href="{uri}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#av)"/>')
    else:  # avatar download failed: initials instead of a broken image
        o.append(f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{FONT}" font-size="24" '
                 f'font-weight="700" fill="{t["accent"]}">{escape(initials)}</text>')
    return "\n".join(o)


def overview_card(s, t, avatar_uri=None):
    W, H = PANEL_W, PANEL_H
    txt = lambda x, y, v, size=MIN_TEXT, fill=None, weight="400", anchor="start": (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill or t["muted"]}">{escape(str(v))}</text>')
    joined = fmt_date(s["created"]) if s["created"] else "unavailable"
    age = account_age(s["created"], s["end"]) if s["created"] else "unavailable"
    period = f'{fmt_date(s["start"])} – {fmt_date(s["end"])}'
    account = [(f'{s["public_repos"]:,}', "Public repos"), (f'{s["followers"]:,}', "Followers"),
               (f'{s["stars"]:,}', "Stars earned")]
    yearly = [(f'{s["commits"]:,}', "Public commits"), (f'{s["prs"]:,}', "Public PRs"),
              (f'{s["issues"]:,}', "Public issues"), (f'{s["repos_committed"]:,}', "Repos committed to"),
              (f'{s["current_streak"]} days', "Current streak*"), (f'{s["longest_streak"]} days', "Longest streak*")]
    desc = (f'{s["name"]} (@{s["login"]}), on GitHub for {age} (since {joined}). Account: '
            + ", ".join(f"{l} {v}" for v, l in account)
            + f'. {period} (UTC): {s["contributions"]:,} contributions (incl. {s["private_counts"]:,} private), '
            + ", ".join(f"{l.rstrip('*')} {v}" for v, l in yearly) + ".")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">GitHub activity and contributions</title>', f'<desc id="d">{escape(desc)}</desc>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>',
         avatar(avatar_uri, t, 54, 58, 34, "".join(p[0] for p in s["name"].split()[:2]).upper() or "?"),
         txt(108, 48, s["name"], 26, t["text"], "700"),
         txt(108, 74, f'@{s["login"]}', 17, t["accent"], "600"),
         txt(108, 98, f'{age} on GitHub · since {joined}')]

    def section(y, label, color):
        o.append(f'<rect x="16" y="{y - 12}" width="10" height="10" rx="2" fill="{color}"/>')
        o.append(txt(32, y, label, MIN_TEXT, color, "700"))

    def cell(x, y, w, val, label, color):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="64" rx="10" fill="{t["surface"]}" stroke="{t["border"]}"/>')
        o.append(f'<rect x="{x + 1}" y="{y + 12}" width="3" height="40" rx="1.5" fill="{color}"/>')
        o.append(txt(x + 14, y + 30, val, 24, t["text"], "700"))
        o.append(txt(x + 14, y + 52, label))

    section(146, "ACCOUNT", t["accent2"])
    for i, (val, label) in enumerate(account):
        cell(16 + i * 128, 158, 122, val, label, t["accent2"])
    section(262, "CONTRIBUTIONS · LAST 12 MONTHS", t["success"])
    o.append(txt(16, 304, f'{s["contributions"]:,}', 36, t["text"], "700"))
    total = f'{s["contributions"]:,}'
    total_w = sum(10 if ch == "," else 20 for ch in total)  # bold 36-unit digits are ~0.556 em, commas ~0.278 em
    o.append(txt(16 + total_w + 10, 304, "contributions*", 18, t["success"], "600"))
    o.append(txt(16, 330, period))
    for i, (val, label) in enumerate(yearly):
        cell(16 + (i % 2) * 192, 346 + (i // 2) * 72, 186, val, label,
             [t["accent"], t["accent"], t["accent"], t["accent2"], t["highlight"], t["highlight"]][i])
    section(588, "3D CONTRIBUTIONS", t["accent"])
    iso, peak = isometric(s["days"], t, ox=16 + 7 * 6.2 + 4, oy=654)
    o.append(iso)
    best = max(s["days"], key=lambda d: d["count"]) if s["days"] else None
    o.append(txt(16, 870, f'Busiest day*: {peak} on {fmt_date(best["date"])}' if peak else "No contributions yet",
                 MIN_TEXT, t["text"], "600"))
    o.append(calendar(s["days"], t, x0=19, y0=888))
    lx = W - 16 - 5 * 14 - 42
    o.append(txt(lx - 8, 964, "Less", anchor="end"))
    for i, lv in enumerate(LEVELS):
        o.append(f'<rect x="{lx + i * 14}" y="952" width="12" height="12" rx="2" fill="{t["levels"][lv]}"/>')
    o.append(txt(W - 16, 964, "More", anchor="end"))
    o.append(txt(16, 992, "* includes private contribution counts"))
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
