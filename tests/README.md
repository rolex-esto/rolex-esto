# Tests

Browser regression checks for the profile README. Nothing here runs on GitHub automatically; run it locally before merging.

```bash
cd tests
npm install                       # playwright (dev only)
npx playwright install chromium webkit firefox

# Stats generator unit tests (standard library only, run from the repository root)
python3 -m unittest discover -s tests -p "test_*.py"

# README, rendered locally with GitHub's own Markdown API (needs `gh auth login`; no push needed)
README_FILE=../README.md BROWSER=chromium node readme.github.cjs

# README, rendered by github.com itself (use the branch URL to test a PR)
README_URL=https://github.com/rolex-esto/rolex-esto/blob/<branch>/README.md BROWSER=chromium node readme.github.cjs
```

| Suite | What it guards |
|:--|:--|
| `readme.github.cjs` | Broken images, page overflow, sideways-scrolling tables, light/dark `<picture>` switching, real text ≥ 12 px, readable text inside SVG images at 320–1440 px, every featured project heading, hero theme switching, every `<picture>` keeping its `<img>`, in-page anchors, Developer Overview panels side by side on desktop and stacked on phones, and no arcade/game branding or links |
| `test_profile_art.py` | README art uses INK COLUMN tokens and neutral greys, AA contrast, text >= 16 units, 410-wide cards, reduced motion, committed SVGs match the generator; README has no linked `<picture>`, both themes per picture, named anchors, local assets present, no trackers or third-party image services |
| `test_stats.py` | Streak maths, star pagination, missing values rejected, empty year, one calendar cell per day, avatar fallback, and an API failure leaving previously published images untouched |

Passing automated checks is evidence, not an accessibility certification. Check on real devices too.
