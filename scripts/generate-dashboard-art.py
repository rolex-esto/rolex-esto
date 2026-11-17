#!/usr/bin/env python3
"""Generate the static right half of the README "Developer Overview" dashboard.

Output: assets/dashboard/portfolio-dark.svg and portfolio-light.svg
  * an original pixel-art scene (a developer coding outside a small house:
    night with stars and fireflies, or day with sun and butterflies)
  * personal-branding lines
  * technology chips, grouped as in the README's Tech Stack section

Animation is plain CSS inside the SVG (GitHub serves SVGs as <img>, so no script
runs). Everything is motionless under prefers-reduced-motion, and the static frame
is a complete picture. No text is smaller than 13 units.

The panel is 410 x 772, the same size as the generated activity panel
(scripts/generate-github-stats.py) so the two sit side by side as one dashboard.

Run from the repository root:  python3 scripts/generate-dashboard-art.py
"""
import xml.dom.minidom
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "dashboard"
W, H = 410, 772
P = 4                    # one art pixel = 4 units
SX, SY = 13, 12          # scene origin
GW, GH = 96, 66          # scene size in art pixels (384 x 264 units)
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

THEMES = {
    "dark": dict(
        bg="#0D1117", surface="#161B22", border="#30363D", teal="#00C389", sky_c="#0EA5E9", purple="#A78BFA",
        text="#C9D1D9", strong="#F0F6FC", muted="#8B949E",
        sky=["#0A0F1F", "#0E1530", "#131C3D", "#1A2650"], far_hill="#16304F", near_hill="#0F3D35",
        grass="#1F7A4A", grass_hi="#2FBF71", grass_lo="#145A3A", soil="#123F2C",
        cloud="#26325A", cloud_hi="#33406E", wall="#2B3245", wall_lo="#222838", roof="#7C5CC4", roof_hi="#A78BFA",
        window="#FFD166", door="#6B3F22", trunk="#5C3A21", leaf="#0F5A3F", leaf_hi="#14A37F",
        desk="#8B5A2B", desk_lo="#6B4420", case="#3A4150", case_hi="#4B5366", screen="#06110D",
        skin="#E0AC80", hair="#1B1B22", hoodie="#00C389", hoodie_lo="#00936A", pants="#2B3245", shoe="#0D1117",
        mug="#0EA5E9", lamp="#FFD166",
    ),
    "light": dict(
        bg="#FFFFFF", surface="#F6F8FA", border="#D0D7DE", teal="#00875F", sky_c="#0369A1", purple="#6D28D9",
        text="#1F2328", strong="#1F2328", muted="#57606A",
        sky=["#7DD3FC", "#93DBFD", "#A9E3FD", "#C2ECFE"], far_hill="#7FD8B6", near_hill="#4FD6A6",
        grass="#2FBF71", grass_hi="#5EE09A", grass_lo="#22A05A", soil="#1C8A4C",
        cloud="#FFFFFF", cloud_hi="#FFFFFF", wall="#F1E9DA", wall_lo="#DCCFB8", roof="#7C5CC4", roof_hi="#A78BFA",
        window="#BAE6FD", door="#8B5A2B", trunk="#7A4E2C", leaf="#14A37F", leaf_hi="#3FD39A",
        desk="#A8713A", desk_lo="#8B5A2B", case="#D0D7DE", case_hi="#EAEEF2", screen="#0D1117",
        skin="#E0AC80", hair="#1B1B22", hoodie="#00A06E", hoodie_lo="#00875F", pants="#3A4150", shoe="#1F2328",
        mug="#0EA5E9", lamp="#FFD166",
    ),
}

# Technologies exactly as listed by the profile owner (README Tech Stack + owner's list).
TECH = [
    ("Languages", [("JavaScript", "#F7DF1E"), ("TypeScript", "#3178C6"), ("Python", "#3776AB"), ("PHP", "#777BB4"),
                   ("SQL", "#00C389")]),
    ("Frameworks", [("React", "#61DAFB"), ("Next.js", None), ("Node.js", "#5FA04E"), ("Vite", "#646CFF"),
                    ("FastAPI", "#009688")]),
    ("Data", [("Microsoft Fabric", "#00C389"), ("Power BI", "#F2C811"), ("Pandas", "#E70488"), ("NumPy", "#4DABCF"),
              ("DuckDB", "#FFF000"), ("PostgreSQL", "#4169E1"), ("MySQL", "#4479A1")]),
    ("Cloud", [("AWS", "#FF9900"), ("Azure", "#0078D4"), ("Google Cloud", "#4285F4"), ("Vercel", None)]),
    ("Tools & AI", [("Git", "#F05032"), ("GitHub", None), ("GitHub Actions", "#2088FF"), ("Playwright", "#2EAD33"),
                    ("Claude Code", "#D97757"), ("Codex", "#10A37F"), ("Cursor", None), ("Kiro", "#9046FF"),
                    ("Antigravity", "#4285F4")]),
]

CSS = """
.cloud{animation:drift 22s ease-in-out infinite alternate}
.cloud.b{animation-duration:30s;animation-delay:-9s}
.tw{animation:tw 3.2s steps(1) infinite}
.tw.b{animation-delay:-1.1s}.tw.c{animation-delay:-2.2s}
.lid{opacity:0;animation:lid 5s steps(1) infinite}
.cur{animation:cur 1s steps(1) infinite}
.code{transform-box:fill-box;transform-origin:left center;animation:type 7s steps(8) infinite}
.code.b{animation-delay:-2.3s}.code.c{animation-delay:-4.6s}
.fly{animation:fly 4.5s ease-in-out infinite alternate}
.fly.b{animation-delay:-1.5s}.fly.c{animation-delay:-3s}
.sway{animation:sway 2.6s steps(2) infinite alternate}
.steam{animation:steam 3s steps(3) infinite}
@keyframes drift{from{transform:translateX(-14px)}to{transform:translateX(14px)}}
@keyframes tw{0%,60%{opacity:1}61%,100%{opacity:.25}}
@keyframes lid{0%,93%{opacity:0}94%,98%{opacity:1}99%,100%{opacity:0}}
@keyframes cur{0%,50%{opacity:1}51%,100%{opacity:0}}
@keyframes type{0%{transform:scaleX(.1)}70%,100%{transform:scaleX(1)}}
@keyframes fly{from{transform:translate(0,0);opacity:.35}to{transform:translate(3px,-8px);opacity:1}}
@keyframes sway{from{transform:translateX(0)}to{transform:translateX(1px)}}
@keyframes steam{0%{transform:translateY(0);opacity:.8}100%{transform:translateY(-6px);opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def mix(fg, bg, a):
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * a + y * (1 - a)):02X}" for x, y in zip(f, b))


class Art:
    def __init__(self):
        self.o = []

    def px(self, gx, gy, w=1, h=1, c="#000", cls=None, extra=""):
        cl = f' class="{cls}"' if cls else ""
        self.o.append(f'<rect{cl} x="{SX + gx * P}" y="{SY + gy * P}" width="{w * P}" height="{h * P}" fill="{c}"{extra}/>')

    def group(self, cls, fn):
        self.o.append(f'<g class="{cls}">')
        fn()
        self.o.append("</g>")


def scene(t, mode):
    a = Art()
    # sky in bands, with a one-row dither between bands
    bands = [(0, 12), (12, 24), (24, 36), (36, 50)]
    for (y0, y1), c in zip(bands, t["sky"]):
        a.px(0, y0, GW, y1 - y0, c)
    for i, (y0, _) in enumerate(bands[1:], 1):
        for gx in range(0, GW, 2):
            a.px(gx + (y0 % 2), y0, 1, 1, t["sky"][i - 1])

    if mode == "dark":
        stars = [(4, 3, "tw"), (11, 9, ""), (17, 2, "tw b"), (23, 14, ""), (29, 6, "tw c"), (35, 11, ""),
                 (41, 3, "tw"), (49, 8, ""), (55, 15, "tw b"), (61, 4, ""), (67, 12, "tw c"), (86, 3, "tw"),
                 (91, 13, ""), (8, 19, "tw b"), (45, 21, ""), (70, 22, "tw"), (93, 24, "")]
        cols = ["#F0F6FC", "#A78BFA", "#7DD3FC"]
        for i, (gx, gy, cls) in enumerate(stars):
            a.px(gx, gy, 1, 1, cols[i % 3], cls or None)
        for gx, gy in ((17, 2), (61, 4)):  # two bigger sparkles
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                a.px(gx + dx, gy + dy, 1, 1, "#C9D1D9", "tw b")
        # crescent moon
        moon = ["..###..", ".#####.", "####...", "###....", "####...", ".#####.", "..###.."]
        for dy, row in enumerate(moon):
            for dx, ch in enumerate(row):
                if ch == "#":
                    a.px(76 + dx, 5 + dy, 1, 1, "#F0F6FC" if dx < 3 else "#C9D1D9")
    else:
        # sun with stepped rays
        for dy, row in enumerate(["..####..", ".######.", "########", "########", "########", "########",
                                  ".######.", "..####.."]):
            for dx, ch in enumerate(row):
                if ch == "#":
                    a.px(76 + dx, 4 + dy, 1, 1, "#FFD166" if (dx + dy) % 5 else "#FFE29A")
        for gx, gy in ((79, 1), (80, 1), (79, 13), (80, 13), (73, 7), (73, 8), (86, 7), (86, 8),
                       (74, 2), (85, 2), (74, 13), (85, 13)):
            a.px(gx, gy, 1, 1, "#FFD166", "tw")

    def cloud(gx, gy, big=True):
        rows = ["....####......", "..########.###", ".##############", "################"] if big else \
               ["..####...", ".#######.", "#########"]
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch == "#":
                    a.px(gx + dx, gy + dy, 1, 1, t["cloud_hi"] if dy == 0 or row[dx - 1:dx] == "." else t["cloud"])
    a.group("cloud", lambda: (cloud(8, 9), cloud(58, 19, False)))
    a.group("cloud b", lambda: cloud(36, 4, False))

    # hills
    for gx in range(GW):
        h = 6 + round(3 * abs(((gx * 7) % 40) - 20) / 20)
        a.px(gx, 50 - h, 1, h, t["far_hill"])
    for gx in range(GW):
        h = 2 + (gx // 3 % 4 == 0) + (gx // 5 % 3 == 0)
        a.px(gx, 50 - h, 1, h, t["near_hill"])

    # ground
    a.px(0, 50, GW, 22, t["grass_lo"])
    a.px(0, 50, GW, 3, t["grass"])
    for gx in range(0, GW, 3):
        a.px(gx, 50, 1, 1, t["grass_hi"])
    for gx in range(1, GW, 7):
        a.px(gx, 57 + (gx % 9), 2, 1, t["soil"])
        a.px(gx + 3, 63 + (gx % 5), 1, 1, t["grass"])
    def tufts():
        for gx in (3, 28, 34, 67, 72, 94):
            a.px(gx, 48, 1, 2, t["grass_hi"]); a.px(gx + 1, 49, 1, 1, t["grass"])
    a.group("sway", tufts)
    # path from the door
    for i, gx in enumerate(range(14, 22)):
        a.px(gx - i // 2, 53 + i, 3, 1, mix(t["desk"], t["grass_lo"], 0.45))

    # house
    a.px(5, 37, 20, 13, t["wall"]); a.px(5, 47, 20, 3, t["wall_lo"])
    for i in range(7):
        a.px(3 + i, 36 - i, 24 - 2 * i, 1, t["roof"] if i % 2 else t["roof_hi"])
    a.px(20, 27, 3, 5, t["wall_lo"])          # chimney
    a.px(13, 42, 4, 8, t["door"]); a.px(16, 46, 1, 1, "#FFD166")
    a.px(7, 40, 4, 4, t["window"]); a.px(19, 40, 4, 4, t["window"])
    a.px(9, 40, 1, 4, t["wall"]); a.px(7, 42, 4, 1, t["wall"])
    a.px(21, 40, 1, 4, t["wall"]); a.px(19, 42, 4, 1, t["wall"])
    if mode == "dark":
        a.px(6, 44, 6, 1, mix("#FFD166", t["wall"], 0.35)); a.px(18, 44, 6, 1, mix("#FFD166", t["wall"], 0.35))

    # tree
    a.px(84, 33, 3, 17, t["trunk"]); a.px(83, 48, 5, 2, t["trunk"])
    for dy, (x0, w) in enumerate([(82, 7), (80, 11), (79, 13), (78, 15), (78, 15), (78, 15), (79, 13), (81, 9)]):
        a.px(x0, 25 + dy, w, 1, t["leaf"])
        a.px(x0 + 1, 25 + dy, max(1, w // 3), 1, t["leaf_hi"])
    a.px(80, 28, 1, 1, t["leaf_hi"]); a.px(88, 30, 1, 1, t["leaf"])

    # workstation: desk, retro monitor, mug, lamp
    a.px(44, 44, 24, 2, t["desk"]); a.px(45, 46, 2, 4, t["desk_lo"]); a.px(65, 46, 2, 4, t["desk_lo"])
    a.px(50, 31, 15, 12, t["case"]); a.px(50, 31, 15, 1, t["case_hi"])
    a.px(55, 43, 5, 1, t["case"])
    a.px(52, 33, 11, 8, t["screen"])
    for (y, w, c, cls) in ((34, 6, "#00C389", "code"), (36, 8, "#0EA5E9", "code b"), (38, 5, "#A78BFA", "code c")):
        a.px(53, y, w, 1, c, cls)
    a.px(59, 38, 1, 1, "#F0F6FC", "cur")
    a.px(64, 41, 3, 3, t["mug"]); a.px(67, 42, 1, 1, t["mug"])
    a.px(65, 39, 1, 1, "#C9D1D9", "steam")

    # developer on a stool, side view, facing the monitor
    a.px(39, 46, 6, 1, t["desk_lo"]); a.px(41, 47, 2, 3, t["desk_lo"])          # stool
    a.px(40, 30, 6, 2, t["hair"]); a.px(39, 31, 2, 4, t["hair"])                # hair
    a.px(41, 32, 5, 5, t["skin"]); a.px(46, 34, 1, 1, t["skin"])                # face + nose
    a.px(44, 33, 1, 1, t["hair"])                                              # eye
    a.px(44, 33, 1, 1, t["skin"], "lid")                                       # blink
    a.px(40, 37, 6, 7, t["hoodie"]); a.px(40, 37, 2, 7, t["hoodie_lo"])          # body
    a.px(45, 39, 5, 2, t["hoodie"]); a.px(50, 40, 2, 1, t["skin"])              # arm to keyboard
    a.px(51, 43, 7, 1, t["case_hi"])                                           # keyboard
    a.px(41, 44, 7, 2, t["pants"]); a.px(46, 46, 2, 3, t["pants"]); a.px(46, 49, 3, 1, t["shoe"])

    # fireflies by night, butterflies by day
    if mode == "dark":
        for gx, gy, cls in ((30, 41, "fly"), (36, 47, "fly b"), (71, 43, "fly c"), (75, 36, "fly"), (92, 44, "fly b")):
            a.px(gx, gy, 1, 1, "#FFD166", cls)
    else:
        for gx, gy, c, cls in ((31, 40, "#A78BFA", "fly"), (72, 41, "#F472B6", "fly b"), (91, 45, "#0EA5E9", "fly c")):
            a.o.append(f'<g class="{cls}">')
            a.px(gx, gy, 1, 1, c); a.px(gx + 2, gy, 1, 1, c); a.px(gx + 1, gy + 1, 1, 1, "#1F2328")
            a.o.append("</g>")
    return a.o


# Helvetica-Bold advance widths (1/1000 em). Viewers' system fonts differ a little,
# so chips get generous padding and the label is centred.
ADV = dict(zip("abcdefghijklmnopqrstuvwxyz", [556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889,
                                              611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500]))
ADV.update(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833,
                                              722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611]))
ADV.update({" ": 278, ".": 278, "&": 722})


def text_width(label, size=13):
    return sum(ADV.get(ch, 600) for ch in label) * size / 1000


def chip_width(label, size=13):
    return round(text_width(label, size)) + 32


def panel(mode):
    t = THEMES[mode]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">Creative portfolio: pixel-art scene and technology stack</title>',
         '<desc id="d">Original pixel art of a developer coding at a retro monitor outside a small house at '
         + ("night under stars" if mode == "dark" else "daytime under a blue sky")
         + ". Technologies: " + escape("; ".join(f"{g}: " + ", ".join(n for n, _ in items) for g, items in TECH)) + ".</desc>",
         f"<style>{CSS}</style>",
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>',
         f'<clipPath id="sc"><rect x="{SX}" y="{SY}" width="{GW * P}" height="{GH * P}" rx="10"/></clipPath>',
         '<g clip-path="url(#sc)" shape-rendering="crispEdges">', *scene(t, mode), "</g>",
         f'<rect x="{SX}" y="{SY}" width="{GW * P}" height="{GH * P}" rx="10" fill="none" stroke="{t["border"]}"/>']
    txt = lambda x, y, v, size, fill, weight="400": (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(v)}</text>')
    o.append(txt(16, 306, "Rolex J. Esto", 22, t["strong"], "700"))
    o.append(txt(16, 330, "Software · AI · Data · Cloud", 15, t["teal"], "600"))
    o.append(txt(16, 352, "Founder of BizPilot · Microsoft Certified DP-700", 13, t["muted"]))
    y = 384
    for group, items in TECH:
        o.append(txt(16, y, group.upper(), 13, t["purple"], "700"))
        y += 6
        x = 16
        for name, color in items:
            w = chip_width(name)
            if x + w > W - 16:
                x, y = 16, y + 27
            c = color or t["strong"]
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="6" fill="{mix(c, t["surface"], 0.16)}" '
                     f'stroke="{mix(c, t["bg"], 0.65)}"/>')
            o.append(f'<rect x="{x + 8}" y="{y + 7}" width="8" height="8" rx="1" fill="{c}"/>')
            o.append(f'<text x="{x + 20 + (w - 26) / 2:.1f}" y="{y + 16}" text-anchor="middle" font-family="{FONT}" '
                     f'font-size="13" font-weight="600" fill="{t["strong"]}">{escape(name)}</text>')
            x += w + 6
        y += 22 + 22
    if y - 22 > H - 12:
        raise SystemExit(f"tech chips overflow the panel (y={y})")
    o.append("</svg>")
    return "\n".join(o)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for mode in THEMES:
        svg = panel(mode)
        xml.dom.minidom.parseString(svg)
        (OUT / f"portfolio-{mode}.svg").write_text(svg + "\n")
        print(f"wrote assets/dashboard/portfolio-{mode}.svg ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
