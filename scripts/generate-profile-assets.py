#!/usr/bin/env python3
"""Generate the profile README's original SVGs (modern layout, subtle pixel accents).

Reuses the bitmap font and pixel sprites from generate-pixel-assets.py so the
profile and the ROLEX.EXE arcade share one visual identity.
Run from the repository root:  python3 scripts/generate-profile-assets.py
Output: assets/profile/*.svg
"""
import importlib.util
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pixel", HERE / "generate-pixel-assets.py")
pixel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pixel)
ptext, sprite, DEV, ICONS, BUG, TOKEN = pixel.text, pixel.sprite, pixel.DEV, pixel.ICONS, pixel.BUG, pixel.TOKEN

OUT = HERE.parent / "assets" / "profile"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

T = {
    "dark": dict(bg="#0D1117", panel="#161B22", panel2="#1C2330", border="#30363D", text="#E6EDF3", muted="#8B949E",
                 green="#70F5A3", purple="#A78BFA", gold="#FFD166", pink="#FF6B9E", chip="#21262D", grid="#1C2330"),
    "light": dict(bg="#FFFFFF", panel="#F6F8FA", panel2="#EEF2F6", border="#D0D7DE", text="#1F2328", muted="#57606A",
                  green="#0E8A4E", purple="#6D4ED8", gold="#9A6700", pink="#BF3989", chip="#EAEEF2", grid="#F0F3F6"),
}

REDUCE = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def svg_open(w, h, title, desc, extra_css=""):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">',
            f'<title id="t">{escape(title)}</title>', f'<desc id="d">{escape(desc)}</desc>',
            f"<style>{extra_css}{REDUCE}</style>"]


def wrap(s, size, max_w):
    """Greedy word wrap using an average sans glyph width estimate."""
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if len(trial) * size * 0.54 > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def chip_w(label, size=12):
    return int(len(label) * size * 0.58) + 20


# ---------------------------------------------------------------- hero
PHRASES = [
    "Founder of BizPilot — operations hub for Filipino online sellers",
    "Microsoft Certified: Fabric Data Engineer Associate",
    "4× hackathon top finishes in 2026",
    "Data Innovation Fellow · Eskwelabs Cohort 11",
]


def hero(theme):
    t = T[theme]
    W, H = 1200, 300
    n = len(PHRASES)
    cycle = n * 4
    css = (f"@keyframes show{{0%{{opacity:1}}22%{{opacity:1}}25%{{opacity:0}}100%{{opacity:0}}}}"
           f"@keyframes typeit{{0%{{transform:translateX(0)}}14%{{transform:translateX(720px)}}100%{{transform:translateX(720px)}}}}"
           f"@keyframes blink{{50%{{opacity:0}}}}@keyframes code{{0%{{transform:scaleX(0)}}60%,100%{{transform:scaleX(1)}}}}"
           f".ph{{opacity:0;animation:show {cycle}s linear infinite}}"
           f".cover{{animation:typeit {cycle}s steps(28) infinite}}"
           f".cur{{animation:blink 1s steps(1) infinite}}"
           f".code{{transform-box:fill-box;transform-origin:left;animation:code 3s steps(10) infinite}}"
           f".code2{{transform-box:fill-box;transform-origin:left;animation:code 3s steps(10) 1s infinite}}"
           "@media (prefers-reduced-motion:reduce){.ph0{opacity:1}}")
    o = svg_open(W, H, "Rolex J. Esto — Software Developer, AI Builder, Data & Cloud Enthusiast",
                 "Profile banner with a small pixel-art developer coding at a desk. Rotating highlights: " + "; ".join(PHRASES) + ".", css)
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>')
    # subtle pixel dot grid on the right
    dots = "".join(f"M{x} {y}h3v3h-3z" for x in range(760, 1180, 24) for y in range(24, 280, 24))
    o.append(f'<path fill="{t["grid"]}" d="{dots}"/>')
    o.append(f'<text x="64" y="76" font-family="{MONO}" font-size="16" fill="{t["green"]}">~/rolex-esto $ whoami</text>')
    o.append(f'<text x="62" y="140" font-family="{SANS}" font-size="56" font-weight="700" fill="{t["text"]}" letter-spacing="-1">Rolex J. Esto</text>')
    o.append(f'<text x="64" y="182" font-family="{SANS}" font-size="22" fill="{t["muted"]}">Software Developer <tspan fill="{t["border"]}">|</tspan> AI Builder <tspan fill="{t["border"]}">|</tspan> Data &amp; Cloud Enthusiast</text>')
    # rotating typed highlight
    o.append(f'<text x="64" y="236" font-family="{MONO}" font-size="17" fill="{t["purple"]}">&gt;</text>')
    for i, ph in enumerate(PHRASES):
        delay = f"animation-delay:{i * 4}s"
        w = int(len(ph) * 17 * 0.61) + 8
        # Mask slides right (clipped to the text box); static state = fully revealed.
        o.append(f'<clipPath id="c{i}"><rect x="82" y="216" width="720" height="30"/></clipPath>')
        o.append(f'<g class="ph ph{i}" style="{delay}"><text x="84" y="236" font-family="{MONO}" font-size="17" fill="{t["text"]}">{escape(ph)}</text>'
                 f'<g clip-path="url(#c{i})"><rect class="cover" style="{delay};transform:translateX(720px)" x="82" y="216" width="720" height="30" fill="{t["bg"]}"/></g></g>')
    o.append(f'<rect class="cur" x="64" y="250" width="10" height="3" fill="{t["green"]}"/>')
    # pixel desk scene
    dx, dy = 880, 120
    o.append(f'<rect x="{dx - 10}" y="{dy + 110}" width="250" height="10" fill="{t["purple"]}"/>')
    o.append(f'<rect x="{dx}" y="{dy + 120}" width="10" height="40" fill="{t["purple"]}"/><rect x="{dx + 220}" y="{dy + 120}" width="10" height="40" fill="{t["purple"]}"/>')
    o.append(f'<rect x="{dx + 100}" y="{dy + 10}" width="130" height="92" fill="#2b3a5c"/>')
    o.append(f'<rect x="{dx + 108}" y="{dy + 18}" width="114" height="68" fill="#0B1020"/>')
    o.append(f'<rect class="code" x="{dx + 116}" y="{dy + 28}" width="70" height="6" fill="#70F5A3"/>')
    o.append(f'<rect class="code2" x="{dx + 124}" y="{dy + 42}" width="84" height="6" fill="#A78BFA"/>')
    o.append(f'<rect class="code" x="{dx + 124}" y="{dy + 56}" width="52" height="6" fill="#FFD166"/>')
    o.append(f'<rect class="cur" x="{dx + 116}" y="{dy + 70}" width="10" height="8" fill="#E6EDF3"/>')
    o.append(f'<rect x="{dx + 155}" y="{dy + 102}" width="22" height="8" fill="#2b3a5c"/>')
    pal = {"H": "#2b1d14", "S": "#f1c27d", "E": "#0B1020", "M": "#b5651d", "C": "#70F5A3", "L": "#E8F2FF", "P": "#3b4a7a", "B": "#141D31"}
    o.append(sprite(DEV, pal, dx + 10, dy + 38, 6))
    plant = ["..GG..", ".GGGG.", "GG.GG.", ".GGG..", "..PP..", ".PPPP.", ".PPPP."]
    o.append(sprite(plant, {"G": "#70F5A3", "P": "#A78BFA"}, dx + 250, dy + 70, 6))
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- link pills
def pill(label, color, icon_rows):
    W, H = int(len(label) * 15 * 0.6) + 64, 40
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)}">',
         f'<title>{escape(label)}</title>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="#161B22" stroke="{color}" stroke-width="2"/>',
         sprite(icon_rows, {"X": color}, 14, 12, 2),
         f'<text x="40" y="26" font-family="{SANS}" font-size="15" font-weight="600" fill="#E6EDF3">{escape(label)}</text>', "</svg>"]
    return "\n".join(o)


PILL_ICONS = {
    "globe": [".XXXXX.", "X..X..X", "XXXXXXX", "X..X..X", "XXXXXXX", "X..X..X", ".XXXXX.", "......."],
    "in": ["XXXXXXX", "X.X...X", "X...XXX", "X.X.X.X", "X.X.X.X", "X.X.X.X", "XXXXXXX", "......."],
    "mail": ["XXXXXXX", "XX...XX", "X.X.X.X", "X..X..X", "X.....X", "X.....X", "XXXXXXX", "......."],
    "badge": [".XXXXX.", "XX...XX", "X..X..X", "X.XXX.X", "XX...XX", ".XX.XX.", ".X...X.", "......."],
    "folder": ["XXX....", "XXXXXXX", "X.....X", "X.....X", "X.....X", "X.....X", "XXXXXXX", "......."],
    "play": ["X......", "XXX....", "XXXXX..", "XXXXXXX", "XXXXX..", "XXX....", "X......", "......."],
    "code": ["..X.X..", ".X...X.", "X..X..X", "X..X..X", "X..X..X", ".X...X.", "..X.X..", "......."],
}


# ---------------------------------------------------------------- project cards
PROJECTS = [
    ("bizpilot", "merchant", "BizPilot", "Founder · Active development",
     "Operations hub for Filipino online sellers: one inbox, chat ordering, stock, and an AI sales assistant.",
     "Founder & Developer", "HIGHLIGHTS", ["Unified inbox", "AI sales assistant", "Ops calendar"]),
    ("smartwatts", "energy", "SmartWatts", "Top 10 Finalist · Meralco IDOL Hackathon",
     "Helps households understand electricity use: bill scanning, appliance tracking, and an English/Tagalog AI advisor.",
     "Lead Developer · Team KuryenTech", "HIGHLIGHTS", ["Bill scanning", "Appliance tracking", "AI advisor"]),
    ("opspilot", "incident", "OpsPilot", "Top 2 Winner · DevKada × ClankerCloud",
     "AI incident investigator that finds the cause of outages from evidence — and says when it isn't confirmed.",
     "Solo Developer", "STACK", ["AI agents", "Incident response", "Observability"]),
    ("baharoute", "flood", "BahaRoute", "Top 10 Climate Track · KiroxHackaton",
     "Flood-aware routing for Metro Manila using Project NOAH flood history, rain forecasts, and voice alerts.",
     "Lead Developer", "HIGHLIGHTS", ["Project NOAH data", "Rain forecasts", "Voice alerts"]),
    ("wwl", "weather", "Weather Weather Lang", "3rd Place · KiroVerse Hack Sprint",
     "Chat-style weather companion that gives friendly, conversational weather updates.",
     "AI Orchestrator · Team project", "STACK", ["React", "TypeScript", "DuckDB-WASM", "Open-Meteo"]),
    ("ulanba", "observatory", "Ulan Ba?", "Solo project",
     "Philippine rain forecast dashboard: hourly rain and severity for 17 regions and 150+ cities.",
     "Creator & Frontend Developer", "STACK", ["React", "TypeScript", "Vite", "Recharts"]),
]


def card(p, theme):
    pid, icon, title, badge, summary, role, kind, chips = p
    t = T[theme]
    W, H = 480, 270
    o = svg_open(W, H, f"{title} — {badge}", f"{summary} Role: {role}. {kind.title()}: {', '.join(chips)}.")
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="2"/>')
    rows, pal = ICONS[icon]
    o.append(f'<rect x="22" y="22" width="56" height="48" rx="8" fill="#141D31"/>')
    o.append(sprite(rows, pal, 26, 30, 4))
    o.append(f'<text x="94" y="45" font-family="{SANS}" font-size="24" font-weight="700" fill="{t["text"]}">{escape(title)}</text>')
    bw = chip_w(badge, 13)
    accent = t["gold"] if badge[0].isdigit() or badge.startswith("Top") else t["purple"]
    o.append(f'<rect x="94" y="54" width="{bw}" height="24" rx="12" fill="none" stroke="{accent}" stroke-width="1.5"/>')
    o.append(f'<text x="{94 + bw / 2}" y="70" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="600" fill="{accent}">{escape(badge)}</text>')
    for i, line in enumerate(wrap(summary, 17, W - 48)[:3]):
        o.append(f'<text x="24" y="{112 + i * 24}" font-family="{SANS}" font-size="17" fill="{t["text"]}">{escape(line)}</text>')
    o.append(f'<text x="24" y="206" font-family="{SANS}" font-size="14" fill="{t["muted"]}"><tspan font-weight="700">ROLE</tspan>  {escape(role)}</text>')
    x = 24
    for c in chips:
        w = chip_w(c, 14)
        o.append(f'<rect x="{x}" y="222" width="{w}" height="28" rx="7" fill="{t["chip"]}"/>')
        o.append(f'<text x="{x + w / 2}" y="241" text-anchor="middle" font-family="{SANS}" font-size="14" fill="{t["text"]}">{escape(c)}</text>')
        x += w + 8
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- tech stack
STACK = [
    ("Languages", [("TypeScript", "#3178C6"), ("JavaScript", "#F7DF1E"), ("Python", "#3776AB"), ("PHP", "#777BB4"), ("SQL", "#E38C00")]),
    ("Frontend", [("React", "#61DAFB"), ("Next.js", "#9BA3AF"), ("Vite", "#9467FF"), ("HTML", "#E34F26"), ("CSS", "#1572B6"), ("Recharts", "#22B5BF")]),
    ("Backend", [("Node.js", "#5FA04E"), ("FastAPI", "#009688"), ("OAuth", "#EB5424")]),
    ("Data Engineering", [("Microsoft Fabric", "#70F5A3"), ("Power BI", "#F2C811"), ("Pandas", "#7B6CF6"), ("NumPy", "#4DABCF"), ("DuckDB", "#FFF000"), ("Parquet", "#50ABF1"), ("Excel", "#217346")]),
    ("Databases", [("PostgreSQL", "#4169E1"), ("MySQL", "#4479A1")]),
    ("Cloud", [("AWS", "#FF9900"), ("Azure", "#0089D6"), ("Google Cloud", "#4285F4"), ("Vercel", "#9BA3AF")]),
    ("AI Tools", [("Claude Code", "#D97757"), ("Codex", "#9BA3AF"), ("Cursor", "#9BA3AF"), ("Kiro", "#A78BFA"), ("Antigravity", "#4285F4")]),
    ("DevOps & Security", [("Git", "#F05032"), ("GitHub Actions", "#2088FF"), ("Playwright", "#2EAD33"), ("IAM", "#FF6B9E")]),
]


def tech(theme):
    t = T[theme]
    W, row_h, top = 1000, 46, 24
    H = top * 2 + row_h * len(STACK) - 10
    desc = "; ".join(f"{k}: {', '.join(n for n, _ in v)}" for k, v in STACK)
    o = svg_open(W, H, "Tech stack", desc)
    o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="2"/>')
    for r, (cat, items) in enumerate(STACK):
        y = top + r * row_h
        o.append(f'<path fill="{t["green"]}" d="M24 {y + 11}h6v6h-6z"/>')
        o.append(f'<text x="40" y="{y + 19}" font-family="{SANS}" font-size="14" font-weight="700" fill="{t["text"]}">{escape(cat)}</text>')
        x = 210
        for name, col in items:
            w = chip_w(name, 13) + 12
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="7" fill="{t["bg"]}" stroke="{t["border"]}"/>')
            o.append(f'<rect x="{x + 10}" y="{y + 10}" width="8" height="8" fill="{col}"/>')
            o.append(f'<text x="{x + 24}" y="{y + 19}" font-family="{SANS}" font-size="13" fill="{t["text"]}">{escape(name)}</text>')
            x += w + 8
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- achievements
WINS = [
    ("Top 2", "Winner", "DevKada × ClankerCloud Build Challenge", "OpsPilot · Aug 2026", "gold"),
    ("3rd", "Place", "KiroVerse Hack Sprint (AWS & RevenueCat)", "Weather Weather Lang · 2026", "purple"),
    ("Top 10", "Finalist", "Meralco IDOL Hackathon", "SmartWatts · Nov 2026", "green"),
    ("Top 10", "Climate Change Track", "BuildOvernights KiroxHackaton · Top 36 team overall", "BahaRoute · Oct 2026", "pink"),
]
MEDAL = ["..XXXX..", ".XXXXXX.", "XXX..XXX", "XX.XX.XX", "XX.XX.XX", "XXX..XXX", ".XXXXXX.", "..XXXX.."]


def wins(theme):
    t = T[theme]
    W, H, gap = 1000, 184, 16
    tw = (W - gap * 3) / 4
    o = svg_open(W, H, "Hackathon results", "; ".join(f"{a} {b}, {c}, {d}" for a, b, c, d, _ in WINS))
    for i, (big, small, event, proj, col) in enumerate(WINS):
        x = i * (tw + gap)
        c = t[col]
        o.append(f'<rect x="{x + 1:.0f}" y="1" width="{tw - 2:.0f}" height="{H - 2}" rx="14" fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="2"/>')
        o.append(sprite(MEDAL, {"X": c}, int(x + 20), 22, 4))
        o.append(f'<text x="{x + 64:.0f}" y="44" font-family="{SANS}" font-size="26" font-weight="800" fill="{c}">{escape(big)}</text>')
        o.append(f'<text x="{x + 64:.0f}" y="62" font-family="{SANS}" font-size="13" font-weight="600" fill="{t["text"]}">{escape(small)}</text>')
        for j, line in enumerate(wrap(event, 13, tw - 40)[:3]):
            o.append(f'<text x="{x + 20:.0f}" y="{98 + j * 18}" font-family="{SANS}" font-size="13" fill="{t["text"]}">{escape(line)}</text>')
        o.append(f'<text x="{x + 20:.0f}" y="{H - 18}" font-family="{SANS}" font-size="12" fill="{t["muted"]}">{escape(proj)}</text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- arcade preview + divider
def arcade_preview():
    W, H = 720, 220
    css = ("@keyframes walk{0%,100%{transform:translateX(0)}50%{transform:translateX(120px)}}"
           "@keyframes bob{50%{transform:translateY(-6px)}}@keyframes blink{50%{opacity:0}}"
           ".walk{animation:walk 5s steps(20) infinite}.bob{animation:bob 1.4s steps(2) infinite}.blink{animation:blink 1.2s steps(1) infinite}")
    o = svg_open(W, H, "ROLEX.EXE arcade preview", "Pixel-art scene from BUG HUNTER: a developer, gold data tokens, a pink bug, and a glowing portal.", css)
    o.append(f'<rect width="{W}" height="{H}" rx="14" fill="#0B1020"/>')
    tiles = []
    for x in range(0, W, 24):
        for y in range(40, 196, 24):
            if (x // 24 + y // 24) % 2:
                tiles.append(f"M{x} {y}h24v24h-24z")
    o.append(f'<path fill="#141D31" d="{"".join(tiles)}"/>')
    o.append('<rect x="0" y="196" width="720" height="24" fill="#3a2f5c"/><rect x="0" y="196" width="720" height="3" fill="#A78BFA"/>')
    o.append('<rect x="0" y="16" width="720" height="24" fill="#3a2f5c"/><rect x="0" y="37" width="720" height="3" fill="#A78BFA"/>')
    o.append(ptext("BUG HUNTER", 24, 21, 2, "#FFD166"))
    o.append(ptext("TOKENS 3/12  XP 300", 696, 21, 2, "#70F5A3", anchor="end"))
    pal = {"H": "#2b1d14", "S": "#f1c27d", "E": "#0B1020", "M": "#b5651d", "C": "#70F5A3", "L": "#E8F2FF", "P": "#3b4a7a", "B": "#141D31"}
    o.append(sprite(DEV, pal, 70, 120, 5))
    tpal = {"Y": "#FFD166", "D": "#986617"}
    for i, (x, y) in enumerate([(200, 90), (280, 140), (360, 80)]):
        o.append(f'<g class="bob" style="animation-delay:{i * .3}s">{sprite(TOKEN, tpal, x, y, 4)}</g>')
    o.append(f'<g class="walk">{sprite(BUG, {"B": "#FF6B9E", "W": "#E8F2FF", "E": "#0B1020", "L": "#7a1f43", "A": "#7a1f43"}, 420, 130, 4)}</g>')
    o.append('<rect x="626" y="96" width="48" height="56" fill="#A78BFA"/><rect class="blink" x="634" y="104" width="32" height="40" fill="#70F5A3"/>')
    o.append("</svg>")
    return "\n".join(o)


def divider():
    W, H = 1000, 10
    d = "".join(f"M{x} 4h4v2h-4z" for x in range(0, W, 12))
    accents = "".join(f'<rect x="{x}" y="3" width="6" height="4" fill="{c}"/>' for x, c in [(0, "#70F5A3"), (12, "#A78BFA"), (24, "#FFD166")])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true"><path fill="#8B949E" opacity=".35" d="{d}"/>{accents}</svg>'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for th in ("dark", "light"):
        (OUT / f"hero-{th}.svg").write_text(hero(th) + "\n")
        (OUT / f"tech-stack-{th}.svg").write_text(tech(th) + "\n")
        (OUT / f"hackathons-{th}.svg").write_text(wins(th) + "\n")
        for p in PROJECTS:
            (OUT / f"card-{p[0]}-{th}.svg").write_text(card(p, th) + "\n")
    (OUT / "arcade-preview.svg").write_text(arcade_preview() + "\n")
    (OUT / "divider.svg").write_text(divider() + "\n")
    links = [("Portfolio", "#70F5A3", "globe", "portfolio"), ("LinkedIn", "#58A6FF", "in", "linkedin"), ("Email", "#FF6B9E", "mail", "email"),
             ("Certifications", "#FFD166", "badge", "certifications"), ("Projects", "#A78BFA", "folder", "projects"),
             ("Play the game", "#70F5A3", "play", "play"), ("Source code", "#A78BFA", "code", "source")]
    for label, col, icon, fname in links:
        (OUT / f"link-{fname}.svg").write_text(pill(label, col, PILL_ICONS[icon]) + "\n")
    total = 0
    for f in sorted(OUT.glob("*.svg")):
        total += f.stat().st_size
    print(f"{len(list(OUT.glob('*.svg')))} files, {total / 1024:.1f} KB total")


if __name__ == "__main__":
    main()
