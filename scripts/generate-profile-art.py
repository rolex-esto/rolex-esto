#!/usr/bin/env python3
"""Generate the static README artwork (INK COLUMN 2.0) into assets/readme/.

Every image comes in a dark and a light variant and is served through <picture> with
prefers-color-scheme, so it follows GitHub's theme. Colours are the INK COLUMN tokens of
the portfolio site (rolex-esto/portfolio, app/globals.css), the same ones the Developer
Overview uses; scripts/generate-dashboard-art.py owns them and this script imports it.

  hero-*.svg                 banner: name, positioning, credentials, isometric workstation
  nav-<id>.svg               navigation buttons (one file: linked images cannot switch theme)
  project-<id>-*.svg         one cover per featured project (410 wide, like the overview panels)
  award-<id>-*.svg           hackathon result cards
  cred-<id>-*.svg            featured certification cards
  stack-<a|b>-*.svg          grouped technology stack
  icons/<name>-*.svg         section heading icons

Content rules: every fact here is also written as Markdown text in README.md (the images
add visual structure, they never carry information that is only in the image). No text is
smaller than 16 units and cards are 410 units wide, so text stays >= 11 px on a 320 px
phone. Animation is CSS only, stops under prefers-reduced-motion, and every still frame is
complete. Icons: Pixelarticons (MIT), vendored in scripts/pixelarticons.json.

Run from the repository root:  python3 scripts/generate-profile-art.py
"""
import importlib.util
import json
import xml.dom.minidom
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "readme"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


art = _load("dashboard_art", "scripts/generate-dashboard-art.py")
ICONS = json.loads((ROOT / "scripts" / "pixelarticons.json").read_text())["icons"]
FONT = art.FONT
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
MIN_TEXT = 16
CARD_W = 410
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"

# INK COLUMN tokens (dark = .dark, light = :root in the portfolio's globals.css).
INK = {
    "dark": dict(bg="#0B0B0D", surface="#131316", surface2="#1B1B1F", border="#26262C", strong="#3D3D45",
                 faint="#34343C", text="#F4F4F5", muted="#B1B1BA", subtle="#A1A1AA"),
    "light": dict(bg="#FFFFFF", surface="#FAFAFA", surface2="#F4F4F5", border="#E7E7E9", strong="#C9C9CF",
                  faint="#D4D4D8", text="#0A0A0A", muted="#62626C", subtle="#6B6B75"),
}
# Isometric shading for the hero illustration: top, left face, right face, edge, screen, screen ink.
ISO = {
    "dark": dict(top="#3D3D45", left="#26262C", right="#1B1B1F", edge="#52525B", screen="#0B0B0D",
                 ink="#A1A1AA", ink_hi="#F4F4F5", trace="#3D3D45", packet="#F4F4F5"),
    "light": dict(top="#FFFFFF", left="#F4F4F5", right="#E4E4E7", edge="#A1A1AA", screen="#26262C",
                  ink="#A1A1AA", ink_hi="#FFFFFF", trace="#C9C9CF", packet="#0A0A0A"),
}


# --------------------------------------------------------------------------- helpers
def width(label, size, mono=False):
    """Conservative advance width: Helvetica-Bold metrics for proportional text."""
    return len(label) * size * 0.61 if mono else art.text_width(label, size)


def wrap(label, size, max_w, mono=False):
    lines, cur = [], ""
    for word in label.split():
        nxt = f"{cur} {word}".strip()
        if cur and width(nxt, size, mono) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = nxt
    return lines + ([cur] if cur else [])


def txt(x, y, v, size, fill, weight="400", anchor="start", mono=False, ls=None, cls=None):
    extra = f' letter-spacing="{ls}"' if ls is not None else ""
    extra += f' class="{cls}"' if cls else ""
    return (f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" font-family="{MONO if mono else FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"{extra}>{escape(v)}</text>')


def icon(name, x, y, size, fill, cls=None):
    body = ICONS[name].replace('fill="currentColor"', f'fill="{fill}"')
    c = f' class="{cls}"' if cls else ""
    return f'<g{c} transform="translate({x:g} {y:g}) scale({size / 24:g})">{body}</g>'


def svg(w, h, title, desc, body, css=""):
    out = "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d">',
        f'<title id="t">{escape(title)}</title>', f'<desc id="d">{escape(desc)}</desc>',
        f"<style>{css}{REDUCED}</style>", *body, "</svg>"])
    xml.dom.minidom.parseString(out)  # never write malformed XML
    return out


def frame(w, h, t, rx=16):
    return f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>'


def grid(pid, t, step=16):
    """Pixel-dot grid pattern (the 'data grid' motif)."""
    return (f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<rect x="{step // 2 - 1}" y="{step // 2 - 1}" width="2" height="2" fill="{t["faint"]}"/></pattern>')


def pill(x, y, label, t, size=MIN_TEXT, filled=False, ico=None, mono=False, h=30):
    """Rounded tag; returns (svg, width)."""
    pad, gap = 12, (24 if ico else 0)
    w = round(width(label, size, mono) + 2 * pad + gap)
    fill, stroke, ink = (t["text"], t["text"], t["bg"]) if filled else (t["surface2"], t["border"], t["text"])
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}"/>']
    if ico:
        o.append(icon(ico, x + pad - 2, y + (h - 20) / 2, 20, ink))
    o.append(txt(x + pad + gap, y + h / 2 + size * 0.35, label, size, ink, "600", mono=mono))
    return "".join(o), w


def tile(x, y, s, name, t, rx=12):
    """Icon tile: the miniature illustration shared by every card."""
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{rx}" fill="{t["surface2"]}" stroke="{t["strong"]}"/>'
            + f'<rect x="{x + 6}" y="{y + s - 6}" width="{s - 12}" height="2" fill="{t["strong"]}"/>'
            + icon(name, x + s * 0.17, y + s * 0.14, s * 0.66, t["text"]))


# --------------------------------------------------------------------------- hero
C30, S30 = 0.8660254, 0.5


class Iso:
    def __init__(self, ox, oy, k, sc=1.0):
        self.ox, self.oy, self.k, self.sc, self.o = ox, oy, k, sc, []

    def p(self, x, y, z=0):
        return self.ox + (x - y) * C30 * self.sc, self.oy + ((x + y) * S30 - z) * self.sc

    def poly(self, pts, fill, stroke=None, cls=None, sw=1.2):
        s = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
        c = f' class="{cls}"' if cls else ""
        self.o.append(f'<polygon{c} points="{s}" fill="{fill}"{st}/>')

    def box(self, x, y, z, w, d, h, shade=None):
        k = self.k
        top, left, right = shade or (k["top"], k["left"], k["right"])
        p = self.p
        self.poly([p(x, y + d, z + h), p(x + w, y + d, z + h), p(x + w, y + d, z), p(x, y + d, z)], left, k["edge"])
        self.poly([p(x + w, y, z + h), p(x + w, y + d, z + h), p(x + w, y + d, z), p(x + w, y, z)], right, k["edge"])
        self.poly([p(x, y, z + h), p(x + w, y, z + h), p(x + w, y + d, z + h), p(x, y + d, z + h)], top, k["edge"])

    def face_y(self, y, x0, x1, z0, z1, fill, cls=None):
        """Rectangle on a plane of constant y (the left-facing side)."""
        p = self.p
        self.poly([p(x0, y, z1), p(x1, y, z1), p(x1, y, z0), p(x0, y, z0)], fill, cls=cls)

    def face_x(self, x, y0, y1, z0, z1, fill, cls=None):
        p = self.p
        self.poly([p(x, y0, z1), p(x, y1, z1), p(x, y1, z0), p(x, y0, z0)], fill, cls=cls)

    def cylinder(self, cx, cy, z, r, h, discs=3):
        k, (sx, sy) = self.k, self.p(cx, cy, z)
        rx, ry, h = r * 1.2247 * self.sc, r * 0.7071 * self.sc, h * self.sc
        top_y = sy - h
        self.o.append(f'<path d="M{sx - rx:.1f},{top_y:.1f} L{sx - rx:.1f},{sy:.1f} A{rx:.1f},{ry:.1f} 0 0 0 '
                      f'{sx + rx:.1f},{sy:.1f} L{sx + rx:.1f},{top_y:.1f} Z" fill="{k["left"]}" stroke="{k["edge"]}" stroke-width="1.2"/>')
        self.o.append(f'<path d="M{sx:.1f},{top_y:.1f} L{sx + rx:.1f},{top_y:.1f} L{sx + rx:.1f},{sy:.1f} '
                      f'A{rx:.1f},{ry:.1f} 0 0 1 {sx:.1f},{sy + ry:.1f} Z" fill="{k["right"]}"/>')
        for i in range(1, discs):
            yy = sy - h * i / discs
            self.o.append(f'<path d="M{sx - rx:.1f},{yy:.1f} A{rx:.1f},{ry:.1f} 0 0 0 {sx + rx:.1f},{yy:.1f}" '
                          f'fill="none" stroke="{k["edge"]}" stroke-width="1.2"/>')
            self.o.append(f'<circle class="led {"b" if i % 2 else ""}" cx="{sx + rx * 0.55:.1f}" cy="{yy + ry * 0.62:.1f}" r="2.2" fill="{k["packet"]}"/>')
        self.o.append(f'<ellipse cx="{sx:.1f}" cy="{top_y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{k["top"]}" stroke="{k["edge"]}" stroke-width="1.2"/>')

    def trace(self, pts, z, cls):
        d = "M" + " L".join("{:.1f},{:.1f}".format(*self.p(x, y, z)) for x, y in pts)
        self.o.append(f'<path d="{d}" fill="none" stroke="{self.k["trace"]}" stroke-width="2.5" stroke-linejoin="round"/>')
        self.o.append(f'<path class="pk {cls}" d="{d}" fill="none" stroke="{self.k["packet"]}" stroke-width="3" '
                      f'stroke-linecap="round" stroke-dasharray="7 520" stroke-dashoffset="-40"/>')


HERO_CSS = """
.cur{animation:cur 1.1s steps(1) infinite}
.pk{animation:pk 5.5s linear infinite}.pk.b{animation-delay:-1.8s}.pk.c{animation-delay:-3.6s}.pk.d{animation-delay:-2.7s}
.led{animation:led 2.6s steps(1) infinite}.led.b{animation-delay:-1.3s}
.float{animation:float 6s ease-in-out infinite alternate}.float.b{animation-delay:-3s}
.code{animation:type 7s steps(1) infinite}
.code.b{animation-delay:-2.2s}.code.c{animation-delay:-4.4s}
.live{animation:live 2.4s ease-in-out infinite}
@keyframes cur{0%,50%{opacity:1}51%,100%{opacity:0}}
@keyframes pk{from{stroke-dashoffset:527}to{stroke-dashoffset:0}}
@keyframes led{0%,60%{opacity:1}61%,100%{opacity:.25}}
@keyframes float{from{transform:translateY(0)}to{transform:translateY(-7px)}}
@keyframes type{0%,18%{opacity:.15}19%,100%{opacity:1}}
@keyframes live{0%,100%{opacity:1}50%{opacity:.35}}
"""


def label_tag(o, x, y, text, t, anchor_pt):
    """Callout: mono tag joined to an object by a hairline."""
    w = round(width(text, MIN_TEXT, True) + 20)
    ax, ay = anchor_pt
    o.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{x + w / 2:.1f}" y2="{y + 14:.1f}" stroke="{t["strong"]}" stroke-dasharray="2 3"/>')
    o.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="3" fill="{t["text"]}"/>')
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="6" fill="{t["bg"]}" stroke="{t["strong"]}"/>')
    o.append(txt(x + 10, y + 19, text, MIN_TEXT, t["text"], "600", mono=True))


def hero(mode):
    t, k = INK[mode], ISO[mode]
    W, H = 1200, 440
    o = [frame(W, H, t, rx=24),
         "<defs>", grid("g", t, 20),
         '<linearGradient id="fade" x1="0" x2="1" y1="0" y2="0"><stop offset="0.35" stop-color="#000000"/>'
         '<stop offset="0.75" stop-color="#FFFFFF"/></linearGradient>',
         f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>',
         f'<clipPath id="c"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="22"/></clipPath>', "</defs>",
         f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#g)" mask="url(#m)" clip-path="url(#c)"/>']

    # ---- left: identity
    x0 = 64
    o.append(txt(x0, 84, "~/rolex-esto", 20, t["subtle"], "500", mono=True))
    o.append(txt(x0 + width("~/rolex-esto ", 20, True), 84, "$ whoami", 20, t["text"], "600", mono=True))
    o.append(f'<rect class="cur" x="{x0 + width("~/rolex-esto $ whoami ", 20, True):.0f}" y="68" width="11" height="20" fill="{t["text"]}"/>')
    o.append(txt(x0 - 4, 176, "Rolex J. Esto", 84, t["text"], "800", ls=-2.5))
    o.append(txt(x0, 224, "Software Engineering · AI · Data Engineering · Cloud", 24, t["muted"], "500"))
    o.append(f'<rect x="{x0}" y="248" width="56" height="4" fill="{t["text"]}"/>')
    x, y = x0, 276
    for ico, label in (("check", "Microsoft Certified · DP-700"), ("shield", "ISC2 Certified in Cybersecurity"),
                       ("trophy", "4× hackathon top finishes")):
        w = round(width(label, 17) + 48)
        if x + w > 660:
            x, y = x0, y + 46
        s, _ = pill(x, y, label, t, size=17, ico=ico, h=36)
        o.append(s)
        x += w + 10
    o.append(f'<circle class="live" cx="{x0 + 6}" cy="{y + 72}" r="6" fill="{t["text"]}"/>')
    o.append(txt(x0 + 22, y + 78, "building BizPilot · BSIT, STI College Fairview", 18, t["muted"], "500", mono=True))

    # ---- right: isometric workstation on a circuit board
    g = Iso(922, 158, k, 1.22)
    g.box(0, 0, 0, 200, 200, 14, (t["surface2"] if mode == "dark" else "#FAFAFA", k["left"], k["right"]))
    for i in range(1, 10):  # board grid
        for a, b in ((g.p(i * 20, 0, 14), g.p(i * 20, 200, 14)), (g.p(0, i * 20, 14), g.p(200, i * 20, 14))):
            g.o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["border"]}"/>')
    z = 14
    g.trace([(150, 56), (150, 112), (140, 112)], z, "")            # server -> db
    g.trace([(60, 140), (60, 112), (92, 112)], z, "b")             # chip -> db
    g.trace([(130, 66), (100, 66), (100, 44)], z, "c")             # server -> monitor
    g.trace([(36, 140), (14, 140), (14, 64), (44, 64)], z, "d")    # chip -> monitor
    # painter's order: back (small x + y) to front
    g.box(132, 8, z, 40, 46, 88)                                    # server tower
    for i in range(6):
        zz = z + 12 + i * 12.5
        g.face_x(172, 16, 48, zz, zz + 6, k["left"])
        g.face_x(172, 40, 45, zz + 1, zz + 5, k["packet"], cls=f'led{" b" if i % 2 else ""}')
    g.box(50, 30, z, 46, 24, 4)                                     # monitor foot
    g.box(68, 38, z + 4, 10, 8, 22)                                 # stand
    g.box(14, 36, z + 26, 112, 8, 58)                               # screen
    g.face_y(44, 20, 120, z + 31, z + 79, k["screen"])
    for i, (x1, cls) in enumerate(((92, "code"), (74, "code b"), (108, "code c"), (60, "code"), (86, "code b"))):
        zz = z + 73 - i * 9
        g.face_y(44, 28 + (8 if i in (2, 3) else 0), x1, zz - 5, zz, k["ink_hi"] if i == 0 else k["ink"], cls=cls)
    g.cylinder(118, 120, z, 26, 54)                                 # database
    g.box(26, 136, z, 52, 52, 8)                                    # AI chip
    for i in range(4):
        g.box(30 + i * 12, 188, z, 6, 6, 3)
        g.box(78, 140 + i * 12, z, 6, 6, 3)
    cx, cy = g.p(52, 162, z + 8)
    g.o.append(f'<g transform="matrix({C30 * 1.22:.4f} {S30 * 1.22:.4f} {-C30 * 1.22:.4f} {S30 * 1.22:.4f} {cx:.1f} {cy:.1f})">'
               + txt(0, 9, "AI", 26, t["text"], "800", "middle", mono=True) + "</g>")
    o.extend(g.o)
    # cloud (top right) and security shield (right) float above the board
    cx, cy = 1088, 66
    o.append(f'<g class="float"><path d="M{cx - 70},{cy + 26} h140 a24,24 0 0 0 -4,-47 a32,32 0 0 0 -60,-14 '
             f'a24,24 0 0 0 -44,14 a22,22 0 0 0 -32,47 z" fill="{t["surface2"]}" stroke="{k["edge"]}" stroke-width="1.6"/>'
             f'{icon("cloud-server", cx - 54, cy - 12, 26, t["text"])}'
             f'{txt(cx - 22, cy + 8, "CLOUD", MIN_TEXT, t["text"], "700", mono=True)}</g>')
    sx, sy = 1162, 196
    o.append(f'<g class="float b"><rect x="{sx - 24}" y="{sy - 24}" width="48" height="48" rx="12" fill="{t["surface2"]}" '
             f'stroke="{k["edge"]}" stroke-width="1.6"/>{icon("shield", sx - 15, sy - 15, 30, t["text"])}</g>')
    label_tag(o, 752, 44, "SOFTWARE", t, g.p(20, 44, z + 79))
    label_tag(o, 1094, 250, "SECURITY", t, (sx, sy + 24))
    label_tag(o, 1060, 386, "DATA", t, g.p(136, 130, z + 26))
    label_tag(o, 746, 386, "AI", t, g.p(26, 162, z + 6))

    desc = ("Banner. Rolex J. Esto: Software Engineering, AI, Data Engineering, Cloud. Microsoft Certified DP-700, ISC2 "
            "Certified in Cybersecurity, four hackathon top finishes; building BizPilot; BSIT at STI College Fairview. "
            "Illustration: an isometric workstation on a circuit board with a monitor, server, database, AI chip, a cloud "
            "and a security shield, joined by traces that carry small data packets.")
    return svg(W, H, "Rolex J. Esto", desc, o, HERO_CSS)


# --------------------------------------------------------------------------- nav buttons
NAV = [  # id, icon, label, external
    ("portfolio", "globe", "Portfolio", True),
    ("linkedin", "linkedin", "LinkedIn", True),
    ("projects", "folder", "Projects", False),
    ("certifications", "notes", "Certifications", False),
    ("email", "mail", "Email", False),
]


# One file per button, readable on both GitHub themes: GitHub's README pipeline moves an <img> out of a
# <picture> that sits inside a link, so linked images cannot switch theme. Ink-black button, INK COLUMN tokens.
NAV_INK = dict(fill="#131316", stroke="#3D3D45", text="#F4F4F5", muted="#B1B1BA")


def nav(ico, label, external):
    t = NAV_INK
    h, size = 44, 17
    w = round(16 + 22 + 10 + width(label, size) + (26 if external else 0) + 16)
    o = [f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="10" fill="{t["fill"]}" stroke="{t["stroke"]}" stroke-width="1.5"/>',
         icon(ico, 16, 11, 22, t["text"]), txt(48, 28.5, label, size, t["text"], "600")]
    if external:
        o.append(icon("external-link", w - 34, 14, 16, t["muted"]))
    return svg(w, h, label, f"Button: {label}{' (opens external site)' if external else ''}", o)


# --------------------------------------------------------------------------- project covers
PROJECTS = [  # id, icon, name, tagline, domain, highlight, highlight_is_award, chips
    ("bizpilot", "store", "BizPilot", "MSME operations platform", "MSME OPS · AI",
     "Active development", False, ["Founder & Developer", "Solo build"]),
    ("opspilot", "server", "OpsPilot", "AI DevOps incident investigator", "AI · DEVOPS",
     "Top 2 Winner", True, ["Solo Developer", "Public repo"]),
    ("smartwatts", "zap", "SmartWatts", "Household electricity tracker", "ENERGY · AI ADVISOR",
     "Top 10 Finalist", True, ["Lead Developer", "Team KuryenTech"]),
    ("baharoute", "map-pin", "BahaRoute", "Flood-aware route helper", "CLIMATE · MAPS",
     "Top 10 Climate Track", True, ["Lead Developer", "Team project"]),
    ("weather-weather-lang", "message-text", "Weather Weather Lang", "Conversational weather companion",
     "AI · WEATHER", "3rd Place", True, ["AI Orchestrator", "Team project"]),
    ("ulan-ba", "cloud-sun", "Ulan Ba?", "Philippine rain forecast dashboard", "DATA · WEATHER",
     "Public repo", False, ["Creator & Frontend Dev", "Solo build"]),
    ("classic-flagship-store", "shopping-bag", "Classic Flagship Store", "E-commerce, POS & inventory",
     "E-COMMERCE · POS", "Live site", False, ["Lead Developer", "Capstone"]),
    ("tapme", "smartphone", "TAPME", "NFC pages & client websites", "NFC · WEB",
     "2025 – Present", False, ["Freelance Web Developer"]),
]


def project(mode, idx, pid, ico, name, tagline, domain, highlight, award, chips):
    t = INK[mode]
    W, H = CARD_W, 256
    o = [frame(W, H, t), "<defs>", grid("g", t), "</defs>",
         f'<rect x="12" y="12" width="{W - 24}" height="122" rx="10" fill="{t["surface"]}" stroke="{t["border"]}"/>',
         f'<rect x="13" y="13" width="{W - 26}" height="120" rx="9" fill="url(#g)"/>',
         tile(28, 28, 90, ico, t, rx=14),
         txt(W - 28, 46, f"{idx:02d} / {len(PROJECTS):02d}", MIN_TEXT, t["subtle"], "500", "end", mono=True),
         txt(138, 80, domain, MIN_TEXT, t["muted"], "600", mono=True)]
    s, _ = pill(138, 94, highlight, t, filled=award, ico="trophy" if award else None)
    o.append(s)
    size = 28 if width(name, 28) <= W - 48 else 24
    o.append(txt(24, 176, name, size, t["text"], "700", ls=-0.5))
    o.append(txt(24, 202, tagline, 17, t["muted"], "500"))
    x = 24
    for c in chips:
        s, w = pill(x, 218, c, t, h=28)
        if x + w > W - 20:
            raise SystemExit(f"{pid}: chips overflow")
        o.append(s)
        x += w + 8
    desc = f"{name}: {tagline}. {domain.title()}. {highlight}. " + ", ".join(chips) + "."
    return svg(W, H, f"{name} project cover", desc, o)


# --------------------------------------------------------------------------- award cards
AWARDS = [  # id, icon, rank, suffix, (event, organiser line), when, project, role
    ("devkada", "trophy", "TOP 2", "WINNER", ("DevKada × ClankerCloud", "Build Challenge"), "Aug 24–29, 2026",
     "OpsPilot", "Solo Developer"),
    ("meralco", "target", "TOP 10", "FINALIST", ("Meralco IDOL Hackathon", "Meralco Power Academy"), "Nov 12–13, 2026",
     "SmartWatts", "Lead Developer · KuryenTech"),
    ("kiroverse", "star", "3RD", "PLACE", ("KiroVerse Hack Sprint", "with AWS & RevenueCat"), "Jun – Aug 2026",
     "Weather Weather Lang", "AI Orchestrator · team project"),
    ("buildovernights", "flag", "TOP 10", "CLIMATE TRACK", ("BuildOvernights KiroxHackaton", "AWS Office · Top 36 team"),
     "Oct 3–4, 2026", "BahaRoute", "Lead Developer · team project"),
]


def award(mode, aid, ico, rank, suffix, event, when, proj, role):
    t = INK[mode]
    W, H = CARD_W, 200
    o = [frame(W, H, t), "<defs>", grid("g", t, 12), "</defs>",
         f'<rect x="14" y="14" width="98" height="{H - 28}" rx="12" fill="{t["surface"]}" stroke="{t["border"]}"/>',
         f'<rect x="15" y="15" width="96" height="{H - 30}" rx="11" fill="url(#g)"/>',
         icon(ico, 31, 46, 64, t["text"]),
         txt(63, H - 32, "2026", MIN_TEXT, t["muted"], "600", "middle", mono=True)]
    x0, max_w = 130, W - 130 - 18
    o.append(txt(x0, 48, rank, 30, t["text"], "800", ls=-0.5))
    o.append(txt(x0 + width(rank, 30) + 6, 48, suffix, MIN_TEXT, t["muted"], "700", mono=True))
    rows = [(event[0], 17, t["text"], "600", False), (event[1], MIN_TEXT, t["muted"], "500", False),
            (when, MIN_TEXT, t["muted"], "500", True), (proj, 17, t["text"], "700", False),
            (role, MIN_TEXT, t["muted"], "500", False)]
    for i, (v, size, fill, weight, mono) in enumerate(rows):
        if width(v, size, mono) > max_w:
            raise SystemExit(f"{aid}: '{v}' is too wide for the card")
        o.append(txt(x0, (76, 98, 124, 154, 176)[i], v, size, fill, weight, mono=mono))
    desc = f"{rank.title()} {suffix.lower()}: {event[0]}, {event[1]}, {when}. Project {proj}; {role}."
    return svg(W, H, f"{rank} {suffix}".title(), desc, o)


# --------------------------------------------------------------------------- credential cards
CREDS = [  # id, icon, issuer, name, rows
    ("dp700", "database", "MICROSOFT CERTIFIED", "Fabric Data Engineer Associate",
     [("Exam", "DP-700"), ("Earned", "Nov 2026"), ("Valid until", "Nov 10, 2027"), ("Verify", "Microsoft Learn")]),
    ("isc2-cc", "shield", "ISC2", "Certified in Cybersecurity",
     [("Credential", "CC"), ("Earned", "Mar 2026"), ("Cycle", "Mar 2026 – Feb 2029"), ("View", "Certificate image")]),
]


def cred(mode, cid, ico, issuer, name, rows):
    t = INK[mode]
    W, H = CARD_W, 262
    o = [frame(W, H, t), "<defs>", grid("g", t), "</defs>",
         f'<rect x="12" y="12" width="{W - 24}" height="104" rx="10" fill="{t["surface"]}" stroke="{t["border"]}"/>',
         f'<rect x="13" y="13" width="{W - 26}" height="102" rx="9" fill="url(#g)"/>',
         tile(26, 26, 76, ico, t),
         txt(118, 48, issuer, MIN_TEXT, t["muted"], "700", mono=True)]
    lines = wrap(name, 21, W - 118 - 24)
    if len(lines) > 2:
        raise SystemExit(f"{cid}: name needs {len(lines)} lines")
    for i, line in enumerate(lines):
        o.append(txt(118, 76 + i * 25, line, 21, t["text"], "700"))
    for i, (k_, v) in enumerate(rows):
        y = 150 + i * 30
        o.append(f'<rect x="24" y="{y - 21}" width="{W - 48}" height="1" fill="{t["border"]}"/>')
        o.append(txt(24, y, k_, MIN_TEXT, t["muted"], "500", mono=True))
        o.append(txt(W - 24, y, v, MIN_TEXT, t["text"], "700" if i == 0 else "600", "end", mono=i == 0))
    desc = f"{issuer.title()}: {name}. " + "; ".join(f"{a}: {b}" for a, b in rows) + "."
    return svg(W, H, f"{name} ({rows[0][1]})", desc, o)


# --------------------------------------------------------------------------- stack
STACK = {
    "a": [("code", "Languages", "Languages", ["JavaScript", "TypeScript", "Python", "PHP", "SQL"]),
          ("terminal", "Frontend & Backend", "Frontend", ["React", "Next.js", "Node.js", "Vite", "FastAPI", "HTML", "CSS", "OAuth"]),
          ("cloud", "Cloud & Security", "Cloud", ["AWS", "Azure", "Google Cloud", "Vercel", "IAM"])],
    "b": [("database", "Data & Analytics", "Data Engineering",
           ["Microsoft Fabric", "Power BI", "Pandas", "NumPy", "DuckDB", "PostgreSQL", "MySQL", "Parquet", "Excel", "Recharts"]),
          ("cpu", "Developer & AI Tools", "Developer Tools & AI",
           ["Git", "GitHub", "GitHub Actions", "Playwright", "Claude Code", "Codex", "Cursor", "Kiro", "Antigravity"])],
}


def stack_layout(groups, mode):
    t = INK[mode]
    o, y = [], 30
    for ico, label, cat, items in groups:
        c = art.CATEGORY[cat][0 if mode == "dark" else 1]
        o.append(icon(ico, 20, y - 10, 22, c))
        o.append(txt(50, y + 7, label.upper(), MIN_TEXT, c, "700", mono=True))
        y += 22
        x = 20
        for name in items:
            w = round(art.text_width(name, MIN_TEXT)) + 26
            if x + w > CARD_W - 20:
                x, y = 20, y + 38
            fill, stroke, lab = art.chip_colors(c, t, mode)
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="8" fill="{fill}" stroke="{stroke}"/>')
            o.append(txt(x + w / 2, y + 20.5, name, MIN_TEXT, lab, "600", "middle"))
            x += w + 8
        y += 30 + 44
    return o, y - 30


def stack(mode, key):
    t = INK[mode]
    heights = [stack_layout(g, mode)[1] for g in STACK.values()]
    H = max(heights) + 4
    body, _ = stack_layout(STACK[key], mode)
    desc = "; ".join(f"{label}: {', '.join(items)}" for _, label, _, items in STACK[key]) + "."
    return svg(CARD_W, H, "Technology stack", desc, [frame(CARD_W, H, t), *body])


# --------------------------------------------------------------------------- heading icons
HEADINGS = ["analytics", "user", "trophy", "folder", "briefcase", "code", "notes", "users", "chart", "mail",
            "lock", "external-link", "check"]


def heading_icon(mode, name):
    c = INK[mode]["text"] if name not in ("lock", "external-link") else INK[mode]["muted"]
    return svg(24, 24, name, f"{name} icon", [icon(name, 0, 0, 24, c)])


def main():
    (OUT / "icons").mkdir(parents=True, exist_ok=True)
    files = {}
    for mode in INK:
        files[f"hero-{mode}.svg"] = hero(mode)
        for i, p in enumerate(PROJECTS, 1):
            files[f"project-{p[0]}-{mode}.svg"] = project(mode, i, *p)
        for a in AWARDS:
            files[f"award-{a[0]}-{mode}.svg"] = award(mode, *a)
        for c in CREDS:
            files[f"cred-{c[0]}-{mode}.svg"] = cred(mode, *c)
        for key in STACK:
            files[f"stack-{key}-{mode}.svg"] = stack(mode, key)
        for name in HEADINGS:
            files[f"icons/{name}-{mode}.svg"] = heading_icon(mode, name)
    for nid, ico, label, ext in NAV:
        files[f"nav-{nid}.svg"] = nav(ico, label, ext)
    total = 0
    for rel, content in files.items():
        (OUT / rel).write_text(content + "\n")
        total += len(content)
    print(f"wrote {len(files)} files to assets/readme/ ({total:,} bytes)")


if __name__ == "__main__":
    main()
