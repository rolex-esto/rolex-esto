# Tests

Browser regression checks for the profile README and the ROLEX.EXE arcade. Nothing here runs on GitHub automatically; run it locally before merging.

```bash
cd tests
npm install                       # playwright + @axe-core/playwright (dev only)
npx playwright install chromium webkit firefox

# README, rendered by github.com itself (use the branch URL to test a PR)
README_URL=https://github.com/rolex-esto/rolex-esto/blob/<branch>/README.md BROWSER=chromium node readme.github.cjs

# Arcade (defaults to the live GitHub Pages URL; point at a local server to test changes)
python3 -m http.server 8000 --directory ..   # in another terminal
ARCADE_URL=http://127.0.0.1:8000/arcade/ BROWSER=webkit node arcade.qa.cjs
```

| Suite | What it guards |
|:--|:--|
| `readme.github.cjs` | Broken images, page/table overflow, light/dark `<picture>` switching, real text ≥ 12 px, readable text inside images at 320–1280 px, every featured project has a visible heading and problem statement |
| `arcade.qa.cjs` | Loading state, movement/collisions, tokens, power-ups, checkpoints, pause, game over/continue, all worlds + bonus, saves, terminal (incl. HTML-injection input), settings, reduced motion, axe-core WCAG A/AA scan, mobile/tablet touch controls |

Passing automated checks (including axe-core) is evidence, not an accessibility certification. Test with a screen reader and real devices too.
