#!/usr/bin/env python3
"""Generate the static right half of the README "Developer Overview" dashboard.

Theme: INK COLUMN, the design tokens of the portfolio site (rolex-esto/portfolio,
app/globals.css). Panel chrome and chips use the tokens exactly. Every scene role keeps
its own grey so objects stay distinct, and all scene pixels pass through neutral(),
which gives them INK COLUMN's zinc tint at the same brightness.

Output: assets/dashboard/portfolio-dark.svg and portfolio-light.svg
  * an original pixel-art scene: a developer in headphones coding at a retro
    monitor beside a cozy cottage on a lavender evening, with a cat, stars,
    pastel clouds and fireflies
  * personal-branding lines
  * technology chips in pastel colours, one colour per category

Animation is plain CSS inside the SVG (GitHub serves SVGs as <img>, so no script
runs). Everything is motionless under prefers-reduced-motion and the still frame
is a complete picture. No text is smaller than 16 units, so labels stay about
10 px on a 320 px phone and 12 px or more from 375 px up.

Both dashboard panels share PANEL_W x PANEL_H with scripts/generate-github-stats.py.
Run from the repository root:  python3 scripts/generate-dashboard-art.py
"""
import math
import xml.dom.minidom
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "dashboard"
PANEL_W, PANEL_H = 410, 1012
W, H = PANEL_W, PANEL_H
P = 4                    # one art pixel = 4 units
SX, SY = 13, 12          # scene origin
GW, GH = 96, 72          # scene size in art pixels (384 x 288 units)
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MIN_TEXT = 16

THEMES = {
    "dark": dict(
        bg="#0B0B0D", surface="#131316", surface2="#1B1B1F", border="#26262C",
        text="#F4F4F5", muted="#B1B1BA", accent="#F4F4F5", accent2="#A1A1AA",
        sky=["#0D1117", "#11161D", "#161B22", "#1B2129", "#21262D", "#282E36", "#30363D"],
        glow="#484F58", star=["#F0F6FC", "#C9D1D9", "#8B949E"],
        moon="#F0F6FC", moon_lo="#C9D1D9",
        cloud="#3D444D", cloud_hi="#545D68", cloud_lo="#30363D",
        far="#1C2128", mid="#262C34", near="#30363D",
        grass="#6E7681", grass_hi="#9CA3AF", grass_body="#3D444D", grass_lo="#30363D", path="#6E7681", path_hi="#8B949E",
        wall="#C9D1D9", wall_lo="#9CA3AF", beam="#484F58", roof="#6E7681", roof_hi="#8B949E", roof_lo="#484F58",
        window="#F0F6FC", window_lo="#D1D5DB", door="#484F58", lit=True,
        trunk="#484F58", leaf="#3D444D", leaf_mid="#545D68", leaf_hi="#8B949E",
        desk="#8B949E", desk_lo="#6E7681", case="#D1D5DB", case_lo="#9CA3AF", screen="#0D1117",
        skin="#E6EDF3", hair="#161B22", hair_hi="#30363D", phones="#B1BAC4",
        hoodie="#6E7681", hoodie_lo="#545D68", pants="#30363D", shoe="#161B22",
        cat="#D1D5DB", cat_lo="#9CA3AF", mug="#9CA3AF", plant="#6E7681", lamp="#F0F6FC",
        flower=["#F0F6FC", "#B1BAC4", "#9CA3AF", "#D1D5DB"], fly="#F0F6FC", mode="night",
    ),
    "light": dict(
        bg="#FFFFFF", surface="#FAFAFA", surface2="#F4F4F5", border="#E7E7E9",
        text="#0A0A0A", muted="#62626C", accent="#0A0A0A", accent2="#6B6B75",
        sky=["#D0D7DE", "#D8DEE4", "#DFE4E9", "#E6EAEF", "#EDF0F3", "#F3F5F7", "#F6F8FA"],
        glow="#FFFFFF", star=["#FFFFFF", "#F6F8FA", "#FFFFFF"],
        moon="#EAEEF2", moon_lo="#C9D1D9",
        cloud="#FFFFFF", cloud_hi="#FFFFFF", cloud_lo="#EAEEF2",
        far="#C9D1D9", mid="#AFB8C1", near="#9CA3AF",
        grass="#8C959F", grass_hi="#C9D1D9", grass_body="#AFB8C1", grass_lo="#9CA3AF", path="#D8DEE4", path_hi="#EAEEF2",
        wall="#F6F8FA", wall_lo="#D0D7DE", beam="#57606A", roof="#6E7781", roof_hi="#8C959F", roof_lo="#424A53",
        window="#D8DEE4", window_lo="#AFB8C1", door="#57606A", lit=False,
        trunk="#57606A", leaf="#6E7781", leaf_mid="#8C959F", leaf_hi="#C9D1D9",
        desk="#8C959F", desk_lo="#6E7781", case="#EAEEF2", case_lo="#AFB8C1", screen="#24292F",
        skin="#F0F3F6", hair="#24292F", hair_hi="#424A53", phones="#6E7781",
        hoodie="#8C959F", hoodie_lo="#6E7781", pants="#424A53", shoe="#24292F",
        cat="#FFFFFF", cat_lo="#D0D7DE", mug="#6E7781", plant="#6E7781", lamp="#F6F8FA",
        flower=["#FFFFFF", "#57606A", "#8C959F", "#D0D7DE"], fly="#57606A", mode="dusk",
    ),
}

# Technologies exactly as in the owner's list; colour = category (pastel, readable in both themes).
CATEGORY = {  # name: (dark-theme grey, light-theme grey); a distinct INK COLUMN token per category
    "Languages": ("#F4F4F5", "#0A0A0A"),
    "Frontend": ("#E7E7E9", "#26262C"),
    "Backend": ("#D4D4D8", "#34343C"),
    "Data Engineering": ("#C9C9CF", "#3D3D45"),
    "Cloud": ("#B1B1BA", "#62626C"),
    "Developer Tools & AI": ("#A1A1AA", "#6B6B75"),
}
TECH = [
    ("Languages", ["JavaScript", "TypeScript", "Python", "PHP", "SQL"]),
    ("Frontend", ["React", "Next.js", "Vite"]),
    ("Backend", ["Node.js", "FastAPI"]),
    ("Data Engineering", ["Microsoft Fabric", "Power BI", "Pandas", "NumPy", "DuckDB", "PostgreSQL", "MySQL"]),
    ("Cloud", ["AWS", "Azure", "Google Cloud", "Vercel"]),
    ("Developer Tools & AI", ["Git", "GitHub", "GitHub Actions", "Playwright", "Claude Code", "Codex", "Cursor",
                              "Kiro", "Antigravity"]),
]

CSS = """
.cloud{animation:drift 26s ease-in-out infinite alternate}
.cloud.b{animation-duration:34s;animation-delay:-11s}
.cloud.c{animation-duration:40s;animation-delay:-20s}
.tw{animation:tw 3.4s steps(1) infinite}
.tw.b{animation-delay:-1.2s}.tw.c{animation-delay:-2.3s}
.lid{opacity:0;animation:lid 5.5s steps(1) infinite}
.catlid{opacity:0;animation:lid 7s steps(1) infinite;animation-delay:-3s}
.cur{animation:cur 1.1s steps(1) infinite}
.code{transform-box:fill-box;transform-origin:left center;animation:type 8s steps(8) infinite}
.code.b{animation-delay:-2.6s}.code.c{animation-delay:-5.2s}.code.d{animation-delay:-6.5s}
.fly{animation:fly 5s ease-in-out infinite alternate}
.fly.b{animation-delay:-1.7s}.fly.c{animation-delay:-3.4s}
.sway{animation:sway 3s steps(2) infinite alternate}
.steam{animation:rise 3.2s steps(4) infinite}
.smoke{animation:rise 4.5s steps(5) infinite}.smoke.b{animation-delay:-2.2s}
.hands{animation:tap .9s steps(2) infinite}
.head{animation:bob 4s steps(2) infinite}
.tail{animation:wag 2.4s steps(2) infinite}
@keyframes drift{from{transform:translateX(-12px)}to{transform:translateX(12px)}}
@keyframes tw{0%,62%{opacity:1}63%,100%{opacity:.3}}
@keyframes lid{0%,93%{opacity:0}94%,98%{opacity:1}99%,100%{opacity:0}}
@keyframes cur{0%,50%{opacity:1}51%,100%{opacity:0}}
@keyframes type{0%{transform:scaleX(.12)}70%,100%{transform:scaleX(1)}}
@keyframes fly{from{transform:translate(0,0);opacity:.35}to{transform:translate(3px,-9px);opacity:1}}
@keyframes sway{from{transform:translateX(0)}to{transform:translateX(1px)}}
@keyframes rise{0%{transform:translateY(0);opacity:.8}100%{transform:translateY(-10px);opacity:0}}
@keyframes tap{from{transform:translateY(0)}to{transform:translateY(-1px)}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(1px)}}
@keyframes wag{from{transform:translateX(0)}to{transform:translateX(-4px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def mix(fg, bg, a):
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * a + y * (1 - a)):02X}" for x, y in zip(f, b))


def neutral(c):
    """Same perceived brightness in INK COLUMN's zinc grey: equal red and green, blue lifted most in the
    mid-tones (#0B0B0D +2, #3D3D45 +8, #62626C +10, #A1A1AA +9, #D4D4D8 +4, #F4F4F5 +1)."""
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    v = 0.2126 * r + 0.7152 * g + 0.0722 * b
    lift = 10 * math.sin(math.pi * min(max(v, 0), 255) / 255)
    return "#" + "".join(f"{max(0, min(255, round(v + d))):02X}" for d in (0, 0, lift))


class Art:
    def __init__(self):
        self.o = []

    def px(self, gx, gy, w=1, h=1, c="#000000", cls=None, op=None):
        cl = f' class="{cls}"' if cls else ""
        o = f' opacity="{op}"' if op is not None else ""
        self.o.append(f'<rect{cl} x="{SX + gx * P}" y="{SY + gy * P}" width="{w * P}" height="{h * P}" fill="{neutral(c)}"{o}/>')

    def sprite(self, gx, gy, rows, pal):
        """Draw a character map; each character found in pal is one art pixel."""
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch in pal:
                    self.px(gx + dx, gy + dy, 1, 1, pal[ch])

    def open(self, cls):
        self.o.append(f'<g class="{cls}">')

    def close(self):
        self.o.append("</g>")


def scene(t):
    a = Art()
    night = t["mode"] == "night"
    # --- sky: bands with a dithered seam, warm glow near the horizon ---
    edges = [0, 8, 15, 21, 27, 33, 38, 46]
    for i, c in enumerate(t["sky"]):
        a.px(0, edges[i], GW, edges[i + 1] - edges[i], c)
    for i in range(1, len(t["sky"])):
        for gx in range(edges[i] % 2, GW, 2):
            a.px(gx, edges[i], 1, 1, t["sky"][i - 1])
    a.px(0, 40, GW, 6, t["glow"], op=0.18 if night else 0.35)

    # --- stars ---
    stars = [(3, 2, "tw"), (9, 7, ""), (15, 3, "tw b"), (21, 10, ""), (26, 1, "tw c"), (31, 6, ""), (38, 12, "tw"),
             (44, 3, ""), (50, 9, "tw b"), (56, 2, ""), (60, 14, "tw c"), (66, 6, ""), (88, 9, "tw"), (93, 3, "tw b"),
             (6, 16, ""), (34, 18, "tw c"), (47, 20, ""), (85, 18, "tw"), (12, 24, "tw b"), (91, 25, "")]
    for i, (gx, gy, cls) in enumerate(stars if night else stars[:7]):
        a.px(gx, gy, 1, 1, t["star"][i % 3], cls or None, None if night else 0.8)
    for gx, gy in ((15, 3), (56, 2)) if night else ((26, 1),):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            a.px(gx + dx, gy + dy, 1, 1, t["star"][0], "tw b", 0.7)

    # --- moon (night) or low evening sun (dusk), with a soft halo ---
    if night:
        moon = ["..####..", ".######.", "#####...", "####....", "####....", "#####...", ".######.", "..####.."]
        a.sprite(75, 5, moon, {"#": t["moon"]})
        a.px(76, 7, 1, 1, t["moon_lo"]); a.px(77, 10, 1, 1, t["moon_lo"])
    else:
        a.px(64, 30, 16, 12, t["glow"], op=0.25)
        sun = ["...######...", ".##########.", "############", "############", "############", "############"]
        a.sprite(66, 33, sun, {"#": t["moon_lo"]})
        a.px(68, 34, 8, 1, t["moon"])

    # --- pastel clouds ---
    big = ["......####.......", "...#########.....", "..############.##", ".################", "#################",
           ".###############."]
    small = ["...####...", ".########.", "##########", ".########."]

    def cloud(gx, gy, rows):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch == "#":
                    top = dy == 0 or rows[dy - 1][dx:dx + 1] != "#"
                    bot = dy == len(rows) - 1 or rows[dy + 1][dx:dx + 1] != "#"
                    a.px(gx + dx, gy + dy, 1, 1, t["cloud_hi"] if top else t["cloud_lo"] if bot else t["cloud"])
    a.open("cloud"); cloud(6, 9, big); a.close()
    a.open("cloud b"); cloud(42, 4, small); a.close()
    a.open("cloud c"); cloud(58, 19, small); a.close()

    # --- layered hills ---
    for gx in range(GW):
        a.px(gx, 46 - (5 + round(4 * abs(((gx * 5) % 48) - 24) / 24)), 1, 9, t["far"])
    for gx in range(GW):
        h = 3 + round(2 * abs(((gx * 3 + 20) % 36) - 18) / 18)
        a.px(gx, 48 - h, 1, h + 2, t["mid"])
    for gx in range(GW):
        a.px(gx, 49 - (1 + (gx // 4) % 2), 1, 3, t["near"])

    # --- ground ---
    a.px(0, 50, GW, 22, t["grass_body"])
    a.px(0, 50, GW, 2, t["grass"])
    for gx in range(0, GW, 2):
        a.px(gx, 50, 1, 1, t["grass_hi"])
    for gx in range(2, GW, 6):
        a.px(gx, 56 + (gx * 7) % 13, 2, 1, t["grass_lo"])
        a.px(gx + 3, 60 + (gx * 3) % 9, 1, 1, t["grass"])
    for i, (gx, gy) in enumerate(((30, 53), (37, 57), (72, 54), (78, 59), (88, 55), (5, 58), (60, 63), (93, 62), (44, 66))):
        a.px(gx, gy, 1, 1, t["flower"][i % 4]); a.px(gx, gy + 1, 1, 1, t["grass_lo"])
    a.open("sway")
    for gx in (2, 27, 33, 70, 76, 95):
        a.px(gx, 48, 1, 2, t["grass_hi"]); a.px(gx + 1, 49, 1, 1, t["grass"])
    a.close()
    for i, (gx, gy) in enumerate(((12, 52), (10, 55), (12, 58), (9, 61), (11, 64), (8, 67), (10, 70))):  # stepping stones
        a.px(gx, gy, 3, 2, t["path"]); a.px(gx, gy, 2, 1, t["path_hi"])

    # --- cozy cottage ---
    a.px(4, 34, 22, 16, t["wall"]); a.px(4, 46, 22, 4, t["wall_lo"])
    for gx in (4, 15, 25):
        a.px(gx, 34, 1, 16, t["beam"])
    a.px(4, 41, 22, 1, t["beam"])
    for i in range(9):  # stepped roof with highlight rows
        a.px(2 + i, 33 - i, 26 - 2 * i, 1, t["roof_hi"] if i % 3 == 0 else t["roof"])
    a.px(1, 33, 28, 1, t["roof_lo"])
    a.px(20, 21, 3, 6, t["wall_lo"]); a.px(19, 20, 5, 1, t["beam"])
    a.open("smoke"); a.px(21, 17, 2, 2, t["cloud_hi"], op=0.6); a.close()
    a.open("smoke b"); a.px(20, 14, 2, 2, t["cloud_hi"], op=0.45); a.close()
    a.px(11, 42, 4, 8, t["door"]); a.px(12, 43, 2, 3, mix(t["window"], t["door"], 0.35)); a.px(14, 46, 1, 1, t["lamp"])
    for wx in (6, 18):
        if t["lit"]:
            a.px(wx - 1, 35, 6, 6, t["window"], op=0.12)
        a.px(wx, 36, 4, 4, t["window"]); a.px(wx, 39, 4, 1, t["window_lo"])
        a.px(wx + 2, 36, 1, 4, t["beam"]); a.px(wx, 38, 4, 1, t["beam"])
        a.px(wx - 1, 40, 6, 1, t["beam"])
        for k, c in enumerate(t["flower"][:3]):
            a.px(wx + k * 2 - 1 + (k > 0), 39, 1, 1, c)
    a.px(16, 43, 1, 2, t["beam"]); a.px(16, 42, 1, 1, t["lamp"])  # door lantern
    if t["lit"]:
        a.px(15, 41, 3, 3, t["lamp"], op=0.15)

    # --- tree ---
    a.px(85, 36, 3, 14, t["trunk"]); a.px(84, 48, 5, 2, t["trunk"]); a.px(86, 40, 1, 6, mix(t["trunk"], "#000000", 0.75))
    canopy = [(84, 5), (81, 11), (80, 13), (79, 15), (79, 15), (79, 15), (80, 13), (82, 9)]
    for dy, (x0, w) in enumerate(canopy):
        a.px(x0, 25 + dy, w, 1, t["leaf"])
        a.px(x0 + 1, 25 + dy, max(1, w // 2), 1, t["leaf_mid"])
        if dy < 4:
            a.px(x0 + 2, 25 + dy, max(1, w // 4), 1, t["leaf_hi"])

    # --- workstation ---
    if t["lit"]:  # lamp light pool
        a.o.append(f'<polygon points="{SX + 66 * P},{SY + 33 * P} {SX + 58 * P},{SY + 46 * P} {SX + 72 * P},{SY + 46 * P}" '
                   f'fill="{neutral(t["lamp"])}" opacity="0.10"/>')
    a.px(43, 45, 28, 2, t["desk"]); a.px(43, 47, 28, 1, t["desk_lo"])
    a.px(45, 48, 2, 3, t["desk_lo"]); a.px(67, 48, 2, 3, t["desk_lo"])
    # retro monitor
    a.px(49, 30, 17, 13, t["case"]); a.px(49, 41, 17, 2, t["case_lo"]); a.px(55, 43, 5, 2, t["case_lo"])
    a.px(51, 32, 13, 8, t["screen"])
    if t["lit"]:
        a.px(47, 30, 4, 12, "#A8C7FA", op=0.08)
    for y, w, c, cls in ((33, 6, "#B8A4FF", "code"), (35, 9, "#A8C7FA", "code b"), (37, 5, "#A8D8B9", "code c"),
                         (38, 7, "#FFD6A5", "code d")):
        a.px(52 + (y == 37), y, w, 1, c, cls)
    a.px(58, 37, 1, 1, "#F5EBD7", "cur")
    a.px(62, 41, 2, 1, "#A8D8B9")  # power LED
    # desk items: mug with steam, plant, lamp, keyboard
    a.px(68, 42, 3, 3, t["mug"]); a.px(71, 43, 1, 1, t["mug"])
    a.px(69, 40, 1, 1, "#F5EBD7", "steam", 0.8)
    a.px(44, 42, 3, 3, t["desk_lo"]); a.px(44, 40, 1, 2, t["plant"]); a.px(46, 39, 1, 3, t["plant"]); a.px(45, 41, 1, 1, t["leaf_hi"])
    a.px(66, 32, 1, 13, t["case_lo"]); a.px(64, 31, 4, 1, t["case_lo"]); a.px(65, 32, 2, 1, t["lamp"])
    a.px(50, 44, 9, 1, t["case_lo"])

    # --- developer with headphones, on a stool, facing the monitor ---
    a.px(38, 47, 7, 1, t["desk_lo"]); a.px(40, 48, 3, 3, t["desk_lo"]); a.px(39, 50, 5, 1, t["desk_lo"])
    a.open("head")
    a.sprite(38, 26, ["..PPPP..", ".PhH##..", "P####ss.", "PP##sEss", "PP##ssss", ".##ssss.", "..#sss..", "...ss..."],
             {"P": t["phones"], "#": t["hair"], "h": t["hair_hi"], "H": t["hair_hi"], "s": t["skin"], "E": t["hair"]})
    a.px(43, 29, 1, 1, t["skin"], "lid")  # blink
    a.close()
    a.sprite(37, 34, [".#######.", "#hhhhhhh#", "#hHhhhhhh", "#hHhhhhhh", "#hHhhhhhh", "#hHhhhhh.", ".hhhhhh.."],
             {"#": t["hoodie_lo"], "h": t["hoodie"], "H": t["hoodie_lo"]})
    a.px(39, 41, 8, 2, t["pants"]); a.px(45, 43, 2, 4, t["pants"]); a.px(45, 47, 4, 1, t["shoe"])
    a.open("hands")
    a.px(44, 37, 6, 2, t["hoodie"]); a.px(50, 38, 2, 1, t["skin"])
    a.close()

    # --- cat beside the stool ---
    cat = [".c..c.....", ".cccc.....", ".cEcE.....", ".cccc.....", "..ccc.....", ".ccccc....", ".cSccc....", ".ccccc...."]
    a.sprite(30, 42, cat, {"c": t["cat"], "E": t["hair"], "S": t["cat_lo"]})
    a.px(32, 44, 1, 1, t["cat"], "catlid"); a.px(34, 44, 1, 1, t["cat"], "catlid")
    a.open("tail"); a.px(35, 47, 1, 2, t["cat_lo"]); a.px(36, 46, 1, 2, t["cat_lo"]); a.close()

    # --- fireflies (night) or small butterflies (dusk) ---
    for i, (gx, gy, cls) in enumerate(((28, 38, "fly"), (36, 44, "fly b"), (74, 40, "fly c"), (78, 33, "fly"),
                                       (92, 42, "fly b"), (8, 30, "fly c"))):
        if night:
            a.px(gx, gy, 1, 1, t["fly"], cls)
        elif i < 3:
            a.open(cls)
            a.px(gx, gy, 1, 1, t["fly"]); a.px(gx + 2, gy, 1, 1, t["fly"]); a.px(gx + 1, gy + 1, 1, 1, t["hair"])
            a.close()
    return a.o


# Helvetica-Bold advance widths (1/1000 em); viewers' system fonts differ a little,
# so chips get generous padding and labels are centred.
ADV = dict(zip("abcdefghijklmnopqrstuvwxyz", [556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889,
                                              611, 611, 611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500]))
ADV.update(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833,
                                              722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611]))
ADV.update({" ": 278, ".": 278, "&": 722, "-": 333})


def chip_colors(c, t, mode):
    """(fill, stroke, label) for a technology chip of category colour c."""
    if mode == "dark":
        return mix(c, t["surface"], 0.16), mix(c, t["bg"], 0.7), c
    return mix(c, t["bg"], 0.10), mix(c, t["bg"], 0.55), mix(c, "#0A0A0A", 0.72)


def text_width(label, size):
    return sum(ADV.get(ch, 600) for ch in label) * size / 1000


def panel(mode):
    t = THEMES[mode]
    txt = lambda x, y, v, size, fill, weight="400", anchor="start": (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}">{escape(v)}</text>')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">',
         '<title id="t">Pixel-art portfolio scene and technology stack</title>',
         '<desc id="d">Original pixel art: a developer in headphones codes at a retro monitor beside a cozy cottage on a '
         + ("lavender night with stars and fireflies" if mode == "dark" else "lavender dusk with a low sun")
         + ", with a cat by the stool. Technologies: "
         + escape("; ".join(f"{g}: " + ", ".join(items) for g, items in TECH)) + ".</desc>",
         f"<style>{CSS}</style>",
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>',
         f'<clipPath id="sc"><rect x="{SX}" y="{SY}" width="{GW * P}" height="{GH * P}" rx="12"/></clipPath>',
         '<g clip-path="url(#sc)" shape-rendering="crispEdges">', *scene(t), "</g>",
         f'<rect x="{SX}" y="{SY}" width="{GW * P}" height="{GH * P}" rx="12" fill="none" stroke="{t["border"]}"/>']
    o.append(txt(16, 336, "Rolex J. Esto", 26, t["text"], "700"))
    o.append(txt(16, 364, "Software · AI · Data · Cloud", 18, t["accent"], "600"))
    o.append(txt(16, 390, "Founder of BizPilot · Microsoft DP-700", 16, t["muted"]))
    o.append(f'<rect x="16" y="406" width="{W - 32}" height="2" rx="1" fill="{t["surface2"]}"/>')
    y = 440
    for group, items in TECH:
        c = CATEGORY[group][0 if mode == "dark" else 1]
        o.append(f'<rect x="16" y="{y - 12}" width="10" height="10" rx="2" fill="{c}"/>')
        o.append(txt(32, y, group.upper(), 16, c, "700"))
        y += 10
        x = 16
        for name in items:
            w = round(text_width(name, MIN_TEXT)) + 28
            if x + w > W - 16:
                x, y = 16, y + 36
            fill, stroke, label = chip_colors(c, t, mode)
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="7" fill="{fill}" stroke="{stroke}"/>')
            o.append(txt(x + w / 2, y + 19.5, name, MIN_TEXT, label, "600", "middle"))
            x += w + 7
        y += 28 + 29
    if y - 29 > H - 14:
        raise SystemExit(f"tech chips overflow the panel (bottom={y - 29}, limit={H - 14})")
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
