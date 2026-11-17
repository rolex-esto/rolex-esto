# Tests

Browser regression checks for the profile README. Nothing here runs on GitHub automatically; run it locally before merging.

```bash
cd tests
npm install                       # playwright (dev only)
npx playwright install chromium webkit firefox

# README, rendered by github.com itself (use the branch URL to test a PR)
README_URL=https://github.com/rolex-esto/rolex-esto/blob/<branch>/README.md BROWSER=chromium node readme.github.cjs
```

| Suite | What it guards |
|:--|:--|
| `readme.github.cjs` | Broken images, page overflow, sideways-scrolling tables, light/dark `<picture>` switching, real text ≥ 12 px, readable text inside SVG images at 320–1280 px, every featured project heading, and no arcade/game branding or links |

Passing automated checks is evidence, not an accessibility certification. Check on real devices too.
