"""Theme, readability and contrast checks for both Developer Overview panels (standard library only).

Run from the repository root:  python3 -m unittest discover -s tests -p "test_*.py"
"""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


stats = load("stats", "scripts/generate-github-stats.py")
art = load("art", "scripts/generate-dashboard-art.py")
from test_stats import make_user  # noqa: E402  (same directory)

# Retired palettes: Fabric Teal, Midnight Pixel, then GitHub-neutral monochrome.
OLD_PALETTE = ("#00C389", "#0EA5E9", "#00A06E", "#0284C7", "#0B0F19", "#B8A4FF", "#A8C7FA", "#A8D8B9", "#FFD6A5",
               "#F5EBD7", "#6B54D6", "#345F9E", "#0D1117", "#161B22", "#30363D", "#F0F6FC", "#D1D5DB", "#9CA3AF",
               "#374151", "#6B7280")

# INK COLUMN design tokens, copied from the portfolio (rolex-esto/portfolio, app/globals.css, :root and .dark).
INK = {
    "dark": {"background": "#0B0B0D", "foreground": "#F4F4F5", "surface": "#131316", "surface-hover": "#1B1B1F",
             "border": "#26262C", "border-strong": "#3D3D45", "muted": "#B1B1BA", "muted-subtle": "#A1A1AA",
             "ink-faint": "#34343C"},
    "light": {"background": "#FFFFFF", "foreground": "#0A0A0A", "surface": "#FAFAFA", "surface-hover": "#F4F4F5",
              "border": "#E7E7E9", "border-strong": "#C9C9CF", "muted": "#62626C", "muted-subtle": "#6B6B75",
              "ink-faint": "#D4D4D8"},
}


def lum(hex_color):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def panels():
    s = stats.summarize(make_user([i % 9 for i in range(367)]))
    out = {f"overview-{m}": stats.overview_card(s, stats.DASH[m], None) for m in stats.DASH}
    out.update({f"portfolio-{m}": art.panel(m) for m in art.THEMES})
    return out


class Theme(unittest.TestCase):
    def test_same_panel_size(self):
        self.assertEqual((stats.PANEL_W, stats.PANEL_H), (art.PANEL_W, art.PANEL_H))

    def test_chrome_uses_exact_portfolio_tokens(self):
        for m in ("dark", "light"):
            k, d, a = INK[m], stats.DASH[m], art.THEMES[m]
            for theme in (d, a):
                self.assertEqual(theme["bg"], k["background"])
                self.assertEqual(theme["surface"], k["surface"])
                self.assertEqual(theme["surface2"], k["surface-hover"])
                self.assertEqual(theme["border"], k["border"])
                self.assertEqual(theme["text"], k["foreground"])
                self.assertEqual(theme["muted"], k["muted"])
            card = stats.THEMES[m]
            self.assertEqual((card["bg"], card["panel"], card["border"], card["text"], card["muted"]),
                             (k["background"], k["surface"], k["border"], k["foreground"], k["muted"]))

    def test_neutral_reproduces_ink_greys(self):
        for m in INK:
            for name, c in INK[m].items():
                got = art.neutral(c)
                for i in (1, 3, 5):
                    self.assertLessEqual(abs(int(got[i:i + 2], 16) - int(c[i:i + 2], 16)), 3, f"{name} {c} -> {got}")

    def test_every_colour_is_a_neutral_grey(self):
        """INK COLUMN greys are zinc: equal red and green, blue lifted by up to ~10."""
        for name, svg in panels().items():
            for c in set(re.findall(r'(?:fill|stroke)="(#[0-9A-Fa-f]{6})"', svg)):
                r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
                self.assertLessEqual(max(r, g, b) - min(r, g, b), 12, f"{c} in {name} is not neutral")

    def test_old_palettes_gone(self):
        for name, svg in panels().items():
            for c in OLD_PALETTE:
                self.assertNotIn(c.upper(), svg.upper(), f"{c} in {name}")

    def test_no_text_below_16_units(self):
        for name, svg in panels().items():
            sizes = [float(x) for x in re.findall(r'<text[^>]*font-size="([\d.]+)"', svg)]
            self.assertTrue(sizes, name)
            self.assertGreaterEqual(min(sizes), 16, name)

    def test_text_contrast_wcag_aa(self):
        for m, t in stats.DASH.items():
            for key in ("text", "muted", "accent", "accent2", "success", "highlight"):
                for bg in ("bg", "surface"):
                    self.assertGreaterEqual(contrast(t[key], t[bg]), 4.5, f"overview {m}: {key} on {bg}")
        for m, t in art.THEMES.items():
            for key in ("text", "muted", "accent"):
                self.assertGreaterEqual(contrast(t[key], t["bg"]), 4.5, f"portfolio {m}: {key}")
            for group, (dark, light) in art.CATEGORY.items():
                c = dark if m == "dark" else light
                fill, _, label = art.chip_colors(c, t, m)
                self.assertGreaterEqual(contrast(label, fill), 4.5, f"portfolio {m}: {group} chip label")
                self.assertGreaterEqual(contrast(c, t["bg"]), 4.5, f"portfolio {m}: {group} heading")

    def test_reduced_motion_disables_animation(self):
        for m in art.THEMES:
            self.assertIn("@media (prefers-reduced-motion:reduce){*{animation:none!important}}", art.panel(m))

    def test_contribution_levels_get_lighter_or_darker_in_order(self):
        for m, t in stats.DASH.items():
            ls = [lum(t["levels"][k]) for k in stats.LEVELS[1:]]
            self.assertEqual(ls, sorted(ls, reverse=(m == "light")), m)


class AccountAge(unittest.TestCase):
    def test_age(self):
        self.assertEqual(stats.account_age("2024-11-17", "2026-11-17"), "2 years")
        self.assertEqual(stats.account_age("2024-11-18", "2026-11-17"), "1 year, 11 months")
        self.assertEqual(stats.account_age("2026-11-01", "2026-11-17"), "under a month")


if __name__ == "__main__":
    unittest.main()
