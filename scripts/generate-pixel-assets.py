#!/usr/bin/env python3
"""Generate the README's original pixel-art SVGs (ROLEX.EXE — Developer Quest).

All text is drawn with a built-in 5x7 bitmap font as pixel rectangles, so the SVGs
render identically on GitHub (which proxies images and cannot load web fonts).
Run from the repository root:  python3 scripts/generate-pixel-assets.py
Output: assets/arcade/*.svg
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "arcade"

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "10001", "11001", "10101", "10011", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10011", "10101", "10101", "10101", "11001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    ">": ["10000", "01000", "00100", "00010", "00100", "01000", "10000"],
    "<": ["00001", "00010", "00100", "01000", "00100", "00010", "00001"],
    "*": ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
    "#": ["01010", "11111", "01010", "01010", "01010", "11111", "01010"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "|": ["00100", "00100", "00100", "00100", "00100", "00100", "00100"],
    " ": ["00000"] * 7,
}
# Small glyphs used inside text: middle dot and play triangle.
FONT["·"] = ["00000", "00000", "00000", "01100", "01100", "00000", "00000"]
FONT["▶"] = ["10000", "11000", "11100", "11110", "11100", "11000", "10000"]
FONT["♥"] = ["00000", "01010", "11111", "11111", "01110", "00100", "00000"]


def text_width(s, scale, spacing=1):
    return len(s) * (5 + spacing) * scale - spacing * scale


def text_path(s, x, y, scale, spacing=1):
    """Return SVG path data for string s drawn at (x, y) with given pixel scale."""
    d = []
    for i, ch in enumerate(s.upper()):
        g = FONT.get(ch, FONT["?"])
        ox = x + i * (5 + spacing) * scale
        for ry, row in enumerate(g):
            rx = 0
            while rx < 5:
                if row[rx] == "1":
                    start = rx
                    while rx < 5 and row[rx] == "1":
                        rx += 1
                    w = (rx - start) * scale
                    d.append(f"M{ox + start * scale} {y + ry * scale}h{w}v{scale}h-{w}z")
                else:
                    rx += 1
    return "".join(d)


def text(s, x, y, scale, fill, anchor="start", spacing=1, cls="", extra=""):
    w = text_width(s, scale, spacing)
    if anchor == "middle":
        x = x - w / 2
    elif anchor == "end":
        x = x - w
    x = round(x)
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} fill="{fill}" d="{text_path(s, x, y, scale, spacing)}"{extra}/>'


def sprite(rows, palette, x, y, scale):
    """Pixel map -> grouped paths per colour."""
    by_col = {}
    for ry, row in enumerate(rows):
        rx = 0
        while rx < len(row):
            ch = row[rx]
            if ch in palette:
                start = rx
                while rx < len(row) and row[rx] == ch:
                    rx += 1
                w = (rx - start) * scale
                by_col.setdefault(palette[ch], []).append(f"M{x + start * scale} {y + ry * scale}h{w}v{scale}h-{w}z")
            else:
                rx += 1
    return "".join(f'<path fill="{c}" d="{"".join(ds)}"/>' for c, ds in by_col.items())


DEV = [
    "....HHHH....",
    "...HHHHHHH..",
    "...HSSSSSH..",
    "...SSESSES..",
    "...SSSSSSS..",
    "....SSMSS...",
    "..CCCCCCCC..",
    ".SCCLLLLCCS.",
    ".SCCLLLLCCS.",
    "..CCCCCCCC..",
    "...PP..PP...",
    "...BB..BB...",
]
BUG = [".A......A.", "..A....A..", "..BBBBBB..", ".BBWBBWBB.", "LBBEBBEBBL", ".BBBBBBBB.", "LBBBBBBBBL", ".BBBBBBBB.", "..BBBBBB..", ".L..L..L.."]
TOKEN = [".DDDD.", "DYYYYD", "DYDDYD", "DYDDYD", "DYYYYD", ".DDDD."]

THEMES = {
    "dark": dict(bg="#0B1020", bg2="#141D31", bg3="#1b2742", sky="#101830", green="#70F5A3", purple="#A78BFA",
                 gold="#FFD166", pink="#FF6B9E", text="#E8F2FF", muted="#8fa3c4", shadow="#1d4a3a", pshadow="#3d2a73",
                 city="#1b2742", city2="#24345c", star="#E8F2FF", ground="#141D31", grid="#24345c", win="#FFD166",
                 desk="#3a2f5c", crt="#2b3a5c", screen="#0a0f1c", hair="#2b1d14", skin="#f1c27d"),
    "light": dict(bg="#E8F2FF", bg2="#D3E3FA", bg3="#c3d6f2", sky="#dbe8fb", green="#0E8A4E", purple="#6D4ED8",
                  gold="#B7791F", pink="#C2255C", text="#0B1020", muted="#4a5a78", shadow="#9fd9b8", pshadow="#cbbcf5",
                  city="#c3d6f2", city2="#aec6ea", star="#6D4ED8", ground="#c3d6f2", grid="#aec6ea", win="#B7791F",
                  desk="#6D4ED8", crt="#4a5a78", screen="#0B1020", hair="#2b1d14", skin="#e0ac69"),
}

ANIM_CSS = """
<style>
@keyframes blink{50%{opacity:0}}
@keyframes bob{50%{transform:translateY(-8px)}}
@keyframes walk{0%{transform:translateX(0)}50%{transform:translateX(160px)}100%{transform:translateX(0)}}
@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes type{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
@keyframes fill{0%{transform:scaleX(.15)}100%{transform:scaleX(1)}}
.blink{animation:blink 1.4s steps(1) infinite}
.bob{animation:bob 1.6s steps(2) infinite}
.bob2{animation:bob 1.6s steps(2) .8s infinite}
.walk{animation:walk 6s steps(24) infinite}
.tw{animation:twinkle 2.4s steps(3) infinite}
.tw2{animation:twinkle 3.1s steps(3) 1s infinite}
.type{transform-box:fill-box;transform-origin:left;animation:type 2.4s steps(12) infinite}
.type2{transform-box:fill-box;transform-origin:left;animation:type 2.4s steps(12) .8s infinite}
.xp{transform-box:fill-box;transform-origin:left;animation:fill 5s steps(20) infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


def hero(theme):
    t = THEMES[theme]
    W, H = 1200, 420
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" role="img" aria-labelledby="t d">',
         '<title id="t">ROLEX.EXE — Developer Quest</title>',
         '<desc id="d">Original pixel-art arcade title screen: a pixel developer coding at a retro computer, a walking bug, collectible tokens, and the text Rolex J. Esto, Software Developer and AI Builder, press start.</desc>',
         ANIM_CSS, f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    # stars
    stars = [(60, 96), (130, 150), (210, 76), (250, 180), (960, 70), (1010, 150), (1100, 104), (1150, 176), (40, 200), (1180, 60), (180, 120), (920, 190)]
    for i, (x, y) in enumerate(stars):
        o.append(f'<rect class="{"tw" if i % 2 else "tw2"}" x="{x}" y="{y}" width="4" height="4" fill="{t["star"]}"/>')
    # skyline
    bld = [(0, 250, 70, 110), (70, 220, 50, 140), (120, 270, 80, 90), (200, 235, 60, 125), (900, 245, 60, 115), (960, 210, 70, 150), (1030, 260, 90, 100), (1120, 230, 80, 130)]
    for i, (x, y, w, h) in enumerate(bld):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{t["city"] if i % 2 else t["city2"]}"/>')
        for wy in range(y + 12, y + h - 20, 22):
            for wx in range(x + 10, x + w - 10, 18):
                if (wx * 7 + wy * 3) % 5 < 2:
                    o.append(f'<rect x="{wx}" y="{wy}" width="6" height="8" fill="{t["win"]}" opacity=".7"/>')
    # ground grid
    o.append(f'<rect x="0" y="360" width="{W}" height="60" fill="{t["ground"]}"/>')
    o.append(f'<rect x="0" y="360" width="{W}" height="4" fill="{t["green"]}"/>')
    for gx in range(0, W, 40):
        o.append(f'<rect x="{gx}" y="368" width="2" height="52" fill="{t["grid"]}"/>')
    o.append(f'<rect x="0" y="390" width="{W}" height="2" fill="{t["grid"]}"/>')
    # HUD corners
    o.append(text("1P ROLEX", 44, 32, 3, t["gold"]))
    o.append(text("STAGE: BUILD/LEARN/SHIP", W - 44, 32, 3, t["gold"], anchor="end"))
    o.append(text("♥♥♥", 44, 60, 3, t["pink"]))
    # title
    o.append(text("PLAYER 01 · DEVELOPER QUEST", W / 2, 62, 3, t["purple"], anchor="middle"))
    o.append(text("ROLEX.EXE", W / 2 + 7, 99, 10, t["shadow"], anchor="middle"))
    o.append(text("ROLEX.EXE", W / 2, 92, 10, t["green"], anchor="middle"))
    o.append(text("ROLEX J. ESTO", W / 2, 180, 4, t["text"], anchor="middle"))
    o.append(text("SOFTWARE DEVELOPER / AI BUILDER", W / 2, 218, 3, t["gold"], anchor="middle"))
    o.append(text("SOFTWARE · AI · DATA · CLOUD · SECURITY", W / 2, 248, 2, t["muted"], anchor="middle"))
    # press start + xp bar
    o.append(f'<g class="blink">{text("▶ PRESS START", W / 2, 286, 4, t["pink"], anchor="middle")}</g>')
    o.append(f'<rect x="440" y="326" width="320" height="16" fill="{t["bg3"]}"/>')
    o.append(f'<rect class="xp" x="444" y="330" width="312" height="8" fill="{t["green"]}"/>')
    o.append(text("XP", 412, 328, 2, t["gold"]))
    # desk scene (right of centre)
    dx, dy = 820, 268
    o.append(f'<rect x="{dx}" y="{dy + 52}" width="150" height="10" fill="{t["desk"]}"/>')
    o.append(f'<rect x="{dx + 10}" y="{dy + 62}" width="8" height="30" fill="{t["desk"]}"/><rect x="{dx + 132}" y="{dy + 62}" width="8" height="30" fill="{t["desk"]}"/>')
    o.append(f'<rect x="{dx + 64}" y="{dy - 8}" width="78" height="60" fill="{t["crt"]}"/>')
    o.append(f'<rect x="{dx + 70}" y="{dy - 2}" width="66" height="42" fill="{t["screen"]}"/>')
    o.append(f'<rect class="type" x="{dx + 76}" y="{dy + 4}" width="40" height="4" fill="#70F5A3"/>')
    o.append(f'<rect class="type2" x="{dx + 82}" y="{dy + 12}" width="46" height="4" fill="#A78BFA"/>')
    o.append(f'<rect class="type" x="{dx + 82}" y="{dy + 20}" width="30" height="4" fill="#FFD166"/>')
    o.append(f'<rect class="blink" x="{dx + 76}" y="{dy + 28}" width="6" height="6" fill="#E8F2FF"/>')
    o.append(f'<rect x="{dx + 96}" y="{dy + 46}" width="14" height="6" fill="{t["crt"]}"/>')
    pal = {"H": t["hair"], "S": t["skin"], "E": "#0B1020", "M": "#b5651d", "C": "#70F5A3", "L": "#E8F2FF", "P": "#3b4a7a", "B": "#141D31"}
    o.append(sprite(DEV, pal, dx + 2, dy - 4, 5))
    # tokens + bug (left of centre)
    tpal = {"Y": "#FFD166", "D": "#986617"}
    o.append(f'<g class="bob">{sprite(TOKEN, tpal, 300, 300, 5)}</g>')
    o.append(f'<g class="bob2">{sprite(TOKEN, tpal, 360, 284, 5)}</g>')
    bpal = {"B": "#FF6B9E", "W": "#E8F2FF", "E": "#0B1020", "L": "#7a1f43", "A": "#7a1f43"}
    o.append(f'<g class="walk">{sprite(BUG, bpal, 110, 318, 4)}</g>')
    # frame corners
    for (x, y, h, v) in [(12, 12, 1, 1), (W - 12, 12, -1, 1), (12, H - 12, 1, -1), (W - 12, H - 12, -1, -1)]:
        o.append(f'<path fill="{t["green"]}" d="M{x} {y}h{60 * h}v{4 * v}h{-56 * h}v{56 * v}h{-4 * h}z"/>')
    o.append("</svg>")
    return "\n".join(o)


ICONS = {
    "merchant": (["..AAAAAAAA..", ".APAPAPAPAP.", "AAAAAAAAAAAA", ".W........W.", ".W..YYYY..W.", ".W..YDDY..W.", ".W..YYYY..W.", ".WWWWWWWWWW."], {"A": "#FF6B9E", "P": "#FFD166", "W": "#A78BFA", "Y": "#FFD166", "D": "#986617"}),
    "energy": (["......YY....", ".....YYY....", "....YYY.....", "...YYYYYYY..", "......YYY...", ".....YYY....", "....YY......", "...Y........"], {"Y": "#70F5A3"}),
    "incident": (["..WWWWWWWW..", ".WWWWWWWWWW.", "WWW......WWW", "WW..B..B..WW", "WW...BB...WW", "WW..B..B..WW", "WW........WW", "WWWWWWWWWWWW"], {"W": "#8b78d0", "B": "#FF6B9E"}),
    "flood": (["....R.......", "...RRR......", "..RRRRR.....", "....R.......", "BB..BB..BB..", ".BBBBBBBBBBB", "B..BB..BB..B", ".BBBBBBBBBBB"], {"R": "#FFD166", "B": "#8fd3ff"}),
    "weather": (["....WWWW....", "..WWWWWWWW..", ".WWWWWWWWWW.", "WWWWWWWWWWWW", ".WWWWWWWWWW.", "..Y..Y..Y...", ".Y..Y..Y....", "............"], {"W": "#E8F2FF", "Y": "#8fd3ff"}),
    "observatory": (["....GGGG....", "...GGGGGG...", "..GGGGGGGG..", "..GGGTTGGG..", "...GGGGGG...", "....WWWW....", "...WWWWWW...", "..WWWWWWWW.."], {"G": "#70F5A3", "T": "#0B1020", "W": "#A78BFA"}),
    "commerce": (["...PPPPPP...", "..PPPPPPPP..", ".WWWWWWWWWW.", ".W.YY..YY.W.", ".W.YY..YY.W.", ".W........W.", ".W..DDDD..W.", ".WWWDDDDWWW."], {"P": "#FFD166", "W": "#A78BFA", "Y": "#8fd3ff", "D": "#FF6B9E"}),
    "guild": (["WWWWWWWWWWWW", "W..........W", "W.GG..YYYY.W", "W.GG.......W", "W....YYYYY.W", "W..........W", "WWWWWWWWWWWW", "............"], {"W": "#70F5A3", "G": "#FFD166", "Y": "#E8F2FF"}),
}


def quest_map(theme):
    t = THEMES[theme]
    W, H = 1200, 420
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" role="img" aria-labelledby="t d">',
         '<title id="t">Quest map</title>',
         '<desc id="d">Pixel world map linking five project worlds in order — Merchant Kingdom (BizPilot), Energy Realm (SmartWatts), Incident Dungeon (OpsPilot), Floodlands (BahaRoute), Weather World (Weather Weather Lang) — plus the bonus Rain Observatory (Ulan Ba?) and two side quests, Commerce City (Classic Flagship Store) and Guild Hall (TAPME).</desc>',
         ANIM_CSS, f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    o.append(text("WORLD MAP", 28, 24, 3, t["gold"]))
    o.append(text("SELECT A WORLD BELOW", W - 28, 24, 3, t["muted"], anchor="end"))
    nodes = [
        ("merchant", "1 MERCHANT KINGDOM", "BIZPILOT", 150, 110),
        ("energy", "2 ENERGY REALM", "SMARTWATTS", 380, 210),
        ("incident", "3 INCIDENT DUNGEON", "OPSPILOT", 610, 110),
        ("flood", "4 FLOODLANDS", "BAHAROUTE", 840, 210),
        ("weather", "5 WEATHER WORLD", "WEATHER WEATHER LANG", 1060, 110),
        ("observatory", "BONUS RAIN OBSERVATORY", "ULAN BA?", 1060, 320),
        ("commerce", "SIDE QUEST COMMERCE CITY", "CLASSIC FLAGSHIP STORE", 230, 330),
        ("guild", "SIDE QUEST GUILD HALL", "TAPME", 590, 330),
    ]
    # dotted path along main worlds then to bonus
    order = [0, 1, 2, 3, 4, 5]
    for a, b in zip(order, order[1:]):
        x1, y1 = nodes[a][3], nodes[a][4]
        x2, y2 = nodes[b][3], nodes[b][4]
        steps = int(max(abs(x2 - x1), abs(y2 - y1)) / 16)
        for s in range(1, steps):
            px = round(x1 + (x2 - x1) * s / steps)
            py = round(y1 + (y2 - y1) * s / steps)
            col = t["purple"] if b == 5 else t["green"]
            o.append(f'<rect x="{px - 3}" y="{py - 3}" width="6" height="6" fill="{col}" opacity=".7"/>')
    for i, (key, title, sub, x, y) in enumerate(nodes):
        rows, pal = ICONS[key]
        o.append(f'<rect x="{x - 34}" y="{y - 30}" width="68" height="52" fill="#141D31"/>')
        o.append(f'<rect x="{x - 34}" y="{y + 22}" width="68" height="4" fill="{t["green"] if key not in ("commerce", "guild", "observatory") else t["purple"]}"/>')
        lw = max(text_width(title, 2), text_width(sub, 2)) + 12
        o.append(f'<rect x="{round(x - lw / 2)}" y="{y + 30}" width="{lw}" height="40" fill="{t["bg"]}"/>')
        cls = "bob" if i % 2 == 0 else "bob2"
        o.append(f'<g class="{cls}">{sprite(rows, pal, x - 24, y - 20, 4)}</g>')
        label_col = t["purple"] if key in ("observatory",) else t["muted"] if key in ("commerce", "guild") else t["gold"]
        o.append(text(title, x, y + 36, 2, label_col, anchor="middle"))
        o.append(text(sub, x, y + 54, 2, t["text"], anchor="middle"))
    # player marker on world 1
    pal = {"H": t["hair"], "S": t["skin"], "E": "#0B1020", "M": "#b5651d", "C": "#70F5A3", "L": "#E8F2FF", "P": "#3b4a7a", "B": "#141D31"}
    o.append(f'<g class="bob2">{sprite(DEV, pal, 92, 62, 3)}</g>')
    o.append("</svg>")
    return "\n".join(o)


def button(label, fg, bg, fname, icon=None):
    W, H = int(text_width(label, 3)) + 66, 66
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" role="img" aria-label="{label.title()}">',
         f'<title>{label.title()}</title>',
         f'<rect x="6" y="6" width="{W - 6}" height="{H - 6}" fill="#050811"/>',
         f'<rect x="0" y="0" width="{W - 6}" height="{H - 6}" fill="{fg}"/>',
         f'<rect x="4" y="4" width="{W - 14}" height="{H - 14}" fill="{bg}"/>',
         text(label, (W - 6) / 2, (H - 6) / 2 - 10, 3, fg, anchor="middle", spacing=1),
         "</svg>"]
    (OUT / fname).write_text("\n".join(o) + "\n")


def divider():
    W, H = 1200, 16
    cols = ["#70F5A3", "#A78BFA", "#FFD166", "#FF6B9E"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" aria-hidden="true">']
    for i, x in enumerate(range(0, W, 24)):
        o.append(f'<rect x="{x}" y="6" width="12" height="4" fill="{cols[i % 4]}" opacity="{1 if i % 6 == 0 else .55}"/>')
    o.append("</svg>")
    return "\n".join(o)


def footer(theme):
    t = THEMES[theme]
    W, H = 1200, 120
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" role="img" aria-label="Game saved. Thanks for playing. Continue?">',
         ANIM_CSS, f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
         f'<rect x="0" y="0" width="{W}" height="4" fill="{t["green"]}"/>',
         text("GAME SAVED · THANKS FOR PLAYING", W / 2, 34, 3, t["green"], anchor="middle"),
         f'<g class="blink">{text("CONTINUE? ▶ YES", W / 2, 72, 3, t["gold"], anchor="middle")}</g>',
         "</svg>"]
    return "\n".join(o)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for th in ("dark", "light"):
        (OUT / f"hero-{th}.svg").write_text(hero(th) + "\n")
        (OUT / f"quest-map-{th}.svg").write_text(quest_map(th) + "\n")
        (OUT / f"footer-{th}.svg").write_text(footer(th) + "\n")
    (OUT / "divider.svg").write_text(divider() + "\n")
    button("▶ PLAY BUG HUNTER", "#70F5A3", "#0B1020", "btn-play.svg")
    button("WORLD MAP", "#A78BFA", "#0B1020", "btn-quests.svg")
    button("TROPHY ROOM", "#FFD166", "#0B1020", "btn-trophies.svg")
    button("PORTFOLIO", "#70F5A3", "#0B1020", "btn-portfolio.svg")
    button("LINKEDIN", "#8fd3ff", "#0B1020", "btn-linkedin.svg")
    button("EMAIL", "#FF6B9E", "#0B1020", "btn-email.svg")
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.name:28} {f.stat().st_size:>7} bytes")


if __name__ == "__main__":
    main()
