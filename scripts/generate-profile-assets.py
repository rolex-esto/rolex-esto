#!/usr/bin/env python3
"""Generate the profile README's original SVGs (modern layout, subtle pixel accents).

Design rule (from the UX refinement audit): images carry identity, not information.
Anything a visitor needs to read lives in Markdown text, so it stays legible at
320 px. Images that do contain text use type large enough to survive a ~254 px
README column (GitHub's width at a 320 px viewport).

Reuses the pixel sprites from generate-pixel-assets.py so the profile and the
ROLEX.EXE arcade share one visual identity.
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
sprite, DEV, ICONS = pixel.sprite, pixel.DEV, pixel.ICONS

OUT = HERE.parent / "assets" / "profile"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

T = {
    "dark": dict(bg="#0D1117", border="#30363D", text="#E6EDF3", muted="#9DA7B3",
                 green="#70F5A3", purple="#B7A2FF", grid="#1C2330"),
    "light": dict(bg="#FFFFFF", border="#D0D7DE", text="#1F2328", muted="#57606A",
                  green="#0E7A45", purple="#6D4ED8", grid="#EEF1F4"),
}

REDUCE = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def svg_open(w, h, title, desc, extra_css=""):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">',
            f'<title id="t">{escape(title)}</title>', f'<desc id="d">{escape(desc)}</desc>',
            f"<style>{extra_css}{REDUCE}</style>"]


# ---------------------------------------------------------------- hero
# Short phrases so the typed line fits beside the desk scene at a large size.
PHRASES = ["Founder @ BizPilot", "Microsoft Certified · DP-700", "4× hackathon top finisher", "Eskwelabs Innovation Fellow"]


def hero(theme):
    t = T[theme]
    W, H = 1000, 380
    n = len(PHRASES)
    cycle = n * 4
    css = (f"@keyframes show{{0%{{opacity:1}}22%{{opacity:1}}25%{{opacity:0}}100%{{opacity:0}}}}"
           f"@keyframes typeit{{0%{{transform:translateX(0)}}14%{{transform:translateX(560px)}}100%{{transform:translateX(560px)}}}}"
           f"@keyframes blink{{50%{{opacity:0}}}}@keyframes code{{0%{{transform:scaleX(0)}}60%,100%{{transform:scaleX(1)}}}}"
           # No fill-mode: hidden phrases must keep base styles during their delay.
           f".ph{{opacity:0;animation:show {cycle}s linear infinite}}"
           f".cover{{animation:typeit {cycle}s steps(20) infinite}}"
           f".cur{{animation:blink 1s steps(1) infinite}}"
           f".code{{transform-box:fill-box;transform-origin:left;animation:code 3s steps(10) infinite}}"
           f".code2{{transform-box:fill-box;transform-origin:left;animation:code 3s steps(10) 1s infinite}}"
           "@media (prefers-reduced-motion:reduce){.ph0{opacity:1}}")
    o = svg_open(W, H, "Rolex J. Esto — Software Developer, AI Builder, Data & Cloud",
                 "Banner with a small pixel-art developer coding at a desk. Rotating highlights: " + "; ".join(PHRASES) + ".", css)
    o.append(f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="22" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="3"/>')
    dots = "".join(f"M{x} {y}h4v4h-4z" for x in range(640, 968, 28) for y in range(30, 360, 28))
    o.append(f'<path fill="{t["grid"]}" d="{dots}"/>')
    o.append(f'<text x="56" y="84" font-family="{MONO}" font-size="24" fill="{t["green"]}">~/rolex-esto $ whoami</text>')
    o.append(f'<text x="52" y="168" font-family="{SANS}" font-size="74" font-weight="700" fill="{t["text"]}" letter-spacing="-1.5">Rolex J. Esto</text>')
    o.append(f'<text x="56" y="218" font-family="{SANS}" font-size="30" fill="{t["muted"]}">Software Developer · AI Builder</text>')
    o.append(f'<text x="56" y="256" font-family="{SANS}" font-size="30" fill="{t["muted"]}">Data &amp; Cloud</text>')
    o.append(f'<text x="56" y="318" font-family="{MONO}" font-size="28" fill="{t["purple"]}">&gt;</text>')
    for i, ph in enumerate(PHRASES):
        delay = f"animation-delay:{i * 4}s"
        o.append(f'<clipPath id="c{i}"><rect x="82" y="290" width="560" height="40"/></clipPath>')
        o.append(f'<g class="ph ph{i}" style="{delay}"><text x="84" y="318" font-family="{MONO}" font-size="28" fill="{t["text"]}">{escape(ph)}</text>'
                 f'<g clip-path="url(#c{i})"><rect class="cover" style="{delay};transform:translateX(560px)" x="82" y="290" width="560" height="40" fill="{t["bg"]}"/></g></g>')
    o.append(f'<rect class="cur" x="56" y="334" width="16" height="4" fill="{t["green"]}"/>')
    # pixel desk scene
    dx, dy = 660, 150
    o.append(f'<rect x="{dx}" y="{dy + 110}" width="280" height="12" fill="#6D4ED8"/>')
    o.append(f'<rect x="{dx + 14}" y="{dy + 122}" width="12" height="70" fill="#6D4ED8"/><rect x="{dx + 252}" y="{dy + 122}" width="12" height="70" fill="#6D4ED8"/>')
    o.append(f'<rect x="{dx + 120}" y="{dy - 10}" width="150" height="108" fill="#2b3a5c"/>')
    o.append(f'<rect x="{dx + 130}" y="{dy}" width="130" height="80" fill="#0B1020"/>')
    o.append(f'<rect class="code" x="{dx + 140}" y="{dy + 12}" width="80" height="7" fill="#70F5A3"/>')
    o.append(f'<rect class="code2" x="{dx + 150}" y="{dy + 28}" width="96" height="7" fill="#A78BFA"/>')
    o.append(f'<rect class="code" x="{dx + 150}" y="{dy + 44}" width="60" height="7" fill="#FFD166"/>')
    o.append(f'<rect class="cur" x="{dx + 140}" y="{dy + 60}" width="12" height="9" fill="#E6EDF3"/>')
    o.append(f'<rect x="{dx + 184}" y="{dy + 98}" width="24" height="12" fill="#2b3a5c"/>')
    pal = {"H": "#2b1d14", "S": "#f1c27d", "E": "#0B1020", "M": "#b5651d", "C": "#70F5A3", "L": "#E8F2FF", "P": "#3b4a7a", "B": "#141D31"}
    o.append(sprite(DEV, pal, dx + 24, dy + 38, 6))
    plant = ["..GG..", ".GGGG.", "GG.GG.", ".GGG..", "..PP..", ".PPPP.", ".PPPP."]
    o.append(sprite(plant, {"G": "#70F5A3", "P": "#A78BFA"}, dx + 282, dy + 68, 6))
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- small pixel icons (theme-neutral dark tiles)
PROJECT_ICONS = {"bizpilot": "merchant", "smartwatts": "energy", "opspilot": "incident", "baharoute": "flood",
                 "wwl": "weather", "ulanba": "observatory", "classic": "commerce", "tapme": "guild"}


def icon(key):
    rows, pal = ICONS[key]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" aria-hidden="true">',
         '<rect width="64" height="64" rx="12" fill="#141D31"/>', sprite(rows, pal, 8, 16, 4), "</svg>"]
    return "\n".join(o)


MEDAL = ["..XXXX..", ".XXXXXX.", "XXX..XXX", "XX.XX.XX", "XX.XX.XX", "XXX..XXX", ".XXXXXX.", "..XXXX.."]
MEDALS = {"gold": "#FFD166", "purple": "#B7A2FF", "green": "#70F5A3", "pink": "#FF8DB5"}


def medal(color):
    return "\n".join([f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48" aria-hidden="true">',
                      '<rect width="48" height="48" rx="10" fill="#141D31"/>', sprite(MEDAL, {"X": color}, 8, 8, 4), "</svg>"])


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


def divider():
    W, H = 1000, 10
    d = "".join(f"M{x} 4h4v2h-4z" for x in range(0, W, 12))
    accents = "".join(f'<rect x="{x}" y="3" width="6" height="4" fill="{c}"/>' for x, c in [(0, "#70F5A3"), (12, "#A78BFA"), (24, "#FFD166")])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true"><path fill="#8B949E" opacity=".35" d="{d}"/>{accents}</svg>'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for th in ("dark", "light"):
        (OUT / f"hero-{th}.svg").write_text(hero(th) + "\n")
    for pid, key in PROJECT_ICONS.items():
        (OUT / f"icon-{pid}.svg").write_text(icon(key) + "\n")
    for name, col in MEDALS.items():
        (OUT / f"medal-{name}.svg").write_text(medal(col) + "\n")
    (OUT / "divider.svg").write_text(divider() + "\n")
    links = [("Portfolio", "#70F5A3", "globe", "portfolio"), ("LinkedIn", "#58A6FF", "in", "linkedin"), ("Email", "#FF6B9E", "mail", "email"),
             ("Certifications", "#FFD166", "badge", "certifications"), ("Projects", "#A78BFA", "folder", "projects"),
             ("Play ROLEX.EXE", "#70F5A3", "play", "play"), ("Source code", "#A78BFA", "code", "source")]
    for label, col, ic, fname in links:
        (OUT / f"link-{fname}.svg").write_text(pill(label, col, PILL_ICONS[ic]) + "\n")
    files = sorted(OUT.glob("*.svg"))
    print(f"{len(files)} SVGs, {sum(f.stat().st_size for f in files) / 1024:.1f} KB total")


if __name__ == "__main__":
    main()
