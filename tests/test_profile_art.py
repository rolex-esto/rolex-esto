"""Checks for the README artwork (scripts/generate-profile-art.py) and README.md structure (standard library only).

Run from the repository root:  python3 -m unittest discover -s tests -p "test_*.py"
"""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("profile_art", ROOT / "scripts/generate-profile-art.py")
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)
from test_dashboard_theme import INK, contrast  # noqa: E402  (same directory)

README = (ROOT / "README.md").read_text()


def generated():
    """Every file the generator would write, keyed by path relative to assets/readme/."""
    out = {}
    for mode in pa.INK:
        out[f"hero-{mode}.svg"] = pa.hero(mode)
        for i, p in enumerate(pa.PROJECTS, 1):
            out[f"project-{p[0]}-{mode}.svg"] = pa.project(mode, i, *p)
        for a in pa.AWARDS:
            out[f"award-{a[0]}-{mode}.svg"] = pa.award(mode, *a)
        for c in pa.CREDS:
            out[f"cred-{c[0]}-{mode}.svg"] = pa.cred(mode, *c)
        for key in pa.STACK:
            out[f"stack-{key}-{mode}.svg"] = pa.stack(mode, key)
    for nid, ico, label, ext in pa.NAV:
        out[f"nav-{nid}.svg"] = pa.nav(ico, label, ext)
    return out


ART = generated()


class Tokens(unittest.TestCase):
    def test_ink_column_tokens(self):
        for m in ("dark", "light"):
            k, t = INK[m], pa.INK[m]
            self.assertEqual((t["bg"], t["surface"], t["surface2"], t["border"], t["text"], t["muted"]),
                             (k["background"], k["surface"], k["surface-hover"], k["border"], k["foreground"], k["muted"]))

    def test_every_colour_is_a_neutral_grey(self):
        for name, svg in ART.items():
            for c in set(re.findall(r'(?:fill|stroke|stop-color)="(#[0-9A-Fa-f]{6})"', svg)):
                r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
                self.assertLessEqual(max(r, g, b) - min(r, g, b), 12, f"{c} in {name} is not neutral")

    def test_text_contrast_wcag_aa(self):
        for m, t in pa.INK.items():
            for fg in ("text", "muted", "subtle"):
                for bg in ("bg", "surface", "surface2"):
                    self.assertGreaterEqual(contrast(t[fg], t[bg]), 4.5, f"{m}: {fg} on {bg}")
            self.assertGreaterEqual(contrast(t["bg"], t["text"]), 4.5, f"{m}: filled pill")
        n = pa.NAV_INK
        self.assertGreaterEqual(contrast(n["text"], n["fill"]), 4.5)
        self.assertGreaterEqual(contrast(n["muted"], n["fill"]), 4.5)


class Readability(unittest.TestCase):
    def test_cards_are_410_wide_with_text_at_least_16_units(self):
        for name, svg in ART.items():
            if name.startswith("hero"):
                continue  # decorative banner; its text is repeated as Markdown under it
            sizes = [float(x) for x in re.findall(r'<text[^>]*font-size="([\d.]+)"', svg)]
            self.assertGreaterEqual(min(sizes), 16, name)
            if not name.startswith("nav"):
                self.assertIn('viewBox="0 0 410 ', svg, name)

    def test_accessible_name_and_reduced_motion(self):
        for name, svg in ART.items():
            self.assertIn('role="img"', svg, name)
            self.assertRegex(svg, r'<title id="t">[^<]+</title>', name)
            self.assertIn("@media (prefers-reduced-motion:reduce){*{animation:none!important}}", svg, name)

    def test_committed_assets_match_the_generator(self):
        for name, svg in ART.items():
            path = ROOT / "assets/readme" / name
            self.assertTrue(path.exists(), f"{name} missing: run python3 scripts/generate-profile-art.py")
            self.assertEqual(path.read_text(), svg + "\n", f"{name} is stale: rerun the generator")


class ReadmeStructure(unittest.TestCase):
    def test_local_assets_exist(self):
        for ref in re.findall(r'(?:src|srcset|href)="((?:assets|\./)[^"]+)"', README) + re.findall(r'\]\(((?:assets|\./)[^)]+)\)', README):
            self.assertTrue((ROOT / ref.lstrip("./")).exists(), ref)

    def test_no_picture_inside_a_link(self):
        # GitHub's README pipeline moves the <img> out of such a <picture>, so it can no longer switch theme.
        self.assertNotRegex(README, r"<a [^>]*>\s*<picture")

    def test_every_picture_has_both_themes(self):
        for pic in re.findall(r"<picture>.*?</picture>", README, re.S):
            self.assertIn('prefers-color-scheme: dark', pic)
            self.assertIn('prefers-color-scheme: light', pic)

    def test_named_anchors_for_navigation(self):
        for target in ("featured-projects", "certifications", "developer-overview"):
            self.assertIn(f'<a name="{target}"></a>', README)

    def test_no_tracking_or_unreliable_image_services(self):
        for host in ("komarev", "capsule-render", "readme-typing-svg", "api.iconify.design", "skillicons.dev",
                     "img.shields.io", "github-readme-stats", "streak-stats"):
            self.assertNotIn(host, README)

    def test_every_featured_project_has_a_heading(self):
        for name, *_ in [(p[2],) for p in pa.PROJECTS]:
            self.assertIn(f"### {name}\n", README)


if __name__ == "__main__":
    unittest.main()
