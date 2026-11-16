#!/usr/bin/env python3
"""Generate real-data GitHub stats cards (dark + light SVG) for the profile README.

Runs in the "Generate profile graphics" workflow with the built-in GITHUB_TOKEN,
so no third-party stats service is needed. Only PUBLIC, non-fork repositories
owned by the user are used for language totals.

Usage:  GITHUB_TOKEN=... python3 scripts/generate-github-stats.py <login> <out_dir>
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
  }
}"""

THEMES = {
    "dark": dict(bg="#0D1117", panel="#161B22", border="#30363D", title="#70F5A3", text="#E6EDF3", muted="#8B949E", accent="#A78BFA", track="#21262D"),
    "light": dict(bg="#FFFFFF", panel="#F6F8FA", border="#D0D7DE", title="#0E8A4E", text="#1F2328", muted="#57606A", accent="#6D4ED8", track="#EAEEF2"),
}
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats-generator"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


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
        i -= 1  # today not over yet
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1
    return current, longest


def summarize(u):
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur, longest = streaks(days)
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, {"size": 0, "color": e["node"]["color"] or "#8B949E"})
            langs[n]["size"] += e["size"]
    total = sum(v["size"] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1]["size"])[:6]
    return {
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "contributed_repos": cc["totalRepositoriesWithContributedCommits"],
        "public_repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "current_streak": cur,
        "longest_streak": longest,
        "languages": [(n, v["color"], v["size"] / total) for n, v in top],
        "window": f"{days[0]['date']} → {days[-1]['date']}" if days else "",
    }


def pixel_corner(x, y, c):
    return f'<path fill="{c}" d="M{x} {y}h12v3h-9v9h-3z"/>'


def activity_card(s, t):
    W, H = 495, 200
    items = [
        ("Contributions", s["contributions"]), ("Public commits", s["commits"]), ("Pull requests", s["prs"]),
        ("Current streak", f'{s["current_streak"]} days'), ("Longest streak", f'{s["longest_streak"]} days'), ("Repos contributed to", s["contributed_repos"]),
    ]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">GitHub activity, last 12 months</title>',
         f'<desc id="d">{escape(", ".join(f"{k}: {v}" for k, v in items))}. Window {escape(s["window"])}.</desc>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>',
         pixel_corner(14, 14, t["title"]),
         f'<text x="34" y="30" font-family="{FONT}" font-size="15" font-weight="600" fill="{t["title"]}">Activity · last 12 months</text>']
    for i, (label, val) in enumerate(items):
        col, row = i % 3, i // 3
        x, y = 24 + col * 156, 52 + row * 70
        o.append(f'<rect x="{x}" y="{y}" width="146" height="60" rx="6" fill="{t["panel"]}"/>')
        o.append(f'<text x="{x + 12}" y="{y + 30}" font-family="{FONT}" font-size="22" font-weight="700" fill="{t["text"]}">{escape(str(val))}</text>')
        o.append(f'<text x="{x + 12}" y="{y + 49}" font-family="{FONT}" font-size="12" fill="{t["muted"]}">{escape(label)}</text>')
    o.append(f'<text x="{W - 16}" y="{H - 8}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{t["muted"]}">Contribution calendar as shown on profile · updated daily</text>')
    o.append("</svg>")
    return "\n".join(o)


def languages_card(s, t):
    W, H = 495, 200
    langs = s["languages"]
    desc = ", ".join(f"{n} {p * 100:.1f}%" for n, _, p in langs) or "No language data"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">Most used languages in public repositories</title>',
         f'<desc id="d">{escape(desc)}</desc>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>',
         pixel_corner(14, 14, t["accent"]),
         f'<text x="34" y="30" font-family="{FONT}" font-size="15" font-weight="600" fill="{t["accent"]}">Languages · public repos</text>',
         f'<rect x="24" y="50" width="{W - 48}" height="10" rx="5" fill="{t["track"]}"/>']
    x = 24.0
    for n, c, p in langs:
        w = (W - 48) * p
        o.append(f'<rect x="{x:.1f}" y="50" width="{max(w, 0):.1f}" height="10" fill="{c}"/>')
        x += w
    for i, (n, c, p) in enumerate(langs):
        col, row = i % 2, i // 2
        lx, ly = 28 + col * 230, 92 + row * 32
        o.append(f'<rect x="{lx}" y="{ly - 10}" width="10" height="10" fill="{c}"/>')
        o.append(f'<text x="{lx + 18}" y="{ly}" font-family="{FONT}" font-size="13" fill="{t["text"]}">{escape(n)}</text>')
        o.append(f'<text x="{lx + 200}" y="{ly}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{t["muted"]}">{p * 100:.1f}%</text>')
    o.append(f'<text x="{W - 16}" y="{H - 8}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{t["muted"]}">By code size · forks excluded · updated daily</text>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    login = sys.argv[1] if len(sys.argv) > 1 else "rolex-esto"
    out = sys.argv[2] if len(sys.argv) > 2 else "dist"
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    s = summarize(fetch(login, token))
    os.makedirs(out, exist_ok=True)
    for name, t in THEMES.items():
        open(os.path.join(out, f"stats-activity-{name}.svg"), "w").write(activity_card(s, t) + "\n")
        open(os.path.join(out, f"stats-languages-{name}.svg"), "w").write(languages_card(s, t) + "\n")
    print(json.dumps({k: v for k, v in s.items() if k != "languages"}, indent=2))
    print("languages:", [(n, round(p * 100, 1)) for n, _, p in s["languages"]])


if __name__ == "__main__":
    main()
