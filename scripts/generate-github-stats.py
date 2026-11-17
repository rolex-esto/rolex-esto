#!/usr/bin/env python3
"""Generate real-data GitHub stats cards (dark + light SVG) for the profile README.

Runs in the "Generate profile graphics" workflow with the built-in GITHUB_TOKEN,
so no third-party stats service is needed. Language totals use only PUBLIC,
non-fork repositories owned by the user.

Safety: the script never writes partial output. It retries transient API errors,
sanity-checks the data, renders every SVG in memory, validates it as XML, and
only then writes the files. On any failure it exits non-zero, so the workflow
stops before publishing and the previously published images stay in place.

Usage:  GITHUB_TOKEN=... python3 scripts/generate-github-stats.py <login> <out_dir>
"""
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.dom.minidom
from html import escape

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalRepositoriesWithContributedCommits
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }
    }
  }
}"""

THEMES = {
    "dark": dict(bg="#0D1117", panel="#161B22", border="#30363D", title="#70F5A3", text="#E6EDF3", muted="#9DA7B3", accent="#B7A2FF", track="#21262D"),
    "light": dict(bg="#FFFFFF", panel="#F6F8FA", border="#D0D7DE", title="#0E7A45", text="#1F2328", muted="#57606A", accent="#6D4ED8", track="#EAEEF2"),
}
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


class StatsError(Exception):
    pass


def fetch(login, token, attempts=3):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
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
    s = {
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
    for k in ("contributions", "commits", "prs", "repos_committed", "current_streak", "longest_streak"):
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


def main():
    login = sys.argv[1] if len(sys.argv) > 1 else "rolex-esto"
    out = sys.argv[2] if len(sys.argv) > 2 else "dist"
    token = os.environ.get("GITHUB_TOKEN")
    try:
        if not token:
            raise StatsError("GITHUB_TOKEN is required")
        s = summarize(fetch(login, token))
        rendered = {}
        for name, t in THEMES.items():
            rendered[f"stats-activity-{name}.svg"] = activity_card(s, t)
            rendered[f"stats-languages-{name}.svg"] = languages_card(s, t)
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
    print(json.dumps({k: v for k, v in s.items() if k != "languages"}, indent=2))
    print("languages:", [(n, round(p * 100, 1)) for n, _, p in s["languages"]])


if __name__ == "__main__":
    main()
