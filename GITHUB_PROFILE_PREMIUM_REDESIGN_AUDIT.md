# GitHub Profile: Premium Redesign Audit (INK COLUMN 2.0)

**Date:** 2026-11-17 · **Branch:** `feature/premium-profile-redesign` · **Base:** `main` @ `d488102` (after PR #8)
**Verdict: PASS_WITH_LIMITATIONS.** Not yet checked on github.com itself, because nothing has been pushed (see section 5).

The ROLEX.EXE arcade stays removed, as decided in PR #4. There are no arcade links, cards, previews or game wording, and no arcade code was restored.

## 1. What changed

| Area | Before | After |
|:--|:--|:--|
| Hero | capsule-render wave, typing SVG, shields badges, view counter | Self-hosted `hero-{dark,light}.svg`: name, positioning, verified credentials, isometric workstation on a circuit board (monitor, server, database, AI chip, cloud, shield) with CSS-only packets. The facts are repeated as Markdown under it |
| Navigation | 4 shields badges | 5 self-hosted buttons (Portfolio, LinkedIn, Projects, Certifications, Email); `<a name>` anchors make the in-page links work |
| Developer Overview | Panel B = tech chips (duplicated the Tech Stack) | Panel B = **Engineering Identity**: five domains, each with the evidence behind it. Panel A (real GitHub API data, daily workflow) unchanged |
| Achievements | 4-column table (scrolled sideways on phones) | 4 award cards (410 wide: 2×2 on desktop, stacked on phones) |
| Featured Projects | 2-column table, 24 px scroll at 320 px, separate "Project details" | 8 covers floated beside Problem / Built / Role / Recognition / Stack text. Stacks only where verified |
| Experience | 3-column table (scrolled on phones) | Timeline: role, organisation, date chip, type (Freelance / Own startup / Fellowship / Program / Education) |
| Tech Stack | skillicons + coloured shields | 2 grouped monochrome stack cards. Note that tools are not certifications |
| Certifications | "9 certifications" badge row + tables | DP-700 and ISC2 CC credential cards; separate counts (9 certifications · 1 recognition · 5 training); dated list, recognition/training and gallery in `<details>` |
| Icons | ~60 requests to api.iconify.design | Pixelarticons (MIT) vendored in `scripts/pixelarticons.json`, rendered locally |
| Third parties | capsule-render, readme-typing-svg, komarev (tracker), iconify, skillicons, shields.io | None. Images are in-repo or from this repo's `output` branch |

## 2. Files

- `README.md`: rewritten (all facts carried over; see section 4)
- `scripts/generate-profile-art.py` (new): writes `assets/readme/` (65 SVGs, 308 KB; the largest is 18.8 KB)
- `scripts/pixelarticons.json` (new): 37 vendored icons, MIT, with source and licence noted
- `scripts/generate-dashboard-art.py`: Panel B chips → domains (`DOMAINS`); `TECH`/`CATEGORY` kept for the stack cards
- `assets/dashboard/portfolio-{dark,light}.svg`: regenerated
- `tests/test_profile_art.py` (new, 12 tests); `tests/readme.github.cjs`: local mode, 1440 px, 3 new rules; `tests/README.md`
- `docs/audit/premium-{before,after}-{dark,light}-{1280,390}.png`

Workflow (`.github/workflows/snake.yml`) and `scripts/generate-github-stats.py`: **unchanged**.

## 3. Two GitHub rendering pitfalls found and fixed

1. **A `<picture>` inside a link breaks.** In README mode GitHub wraps every `<img>` in its own link. When the `<picture>` is already inside `<a>`, the `<img>` ends up outside the `<picture>`, so theme switching stops and the link points at the SVG. Fix: navigation buttons are single theme-neutral images; cards are unlinked `<picture>`s with their links in the text. Guarded by tests.
2. **Heading slugs start with `-`** because of the icon before the text (`#-featured-projects`). The old `#developer-overview` link on `main` was broken for this reason. Fix: `<a name="…">` anchors, which GitHub keeps as `user-content-…`.

## 4. Accuracy sources

The README on `main`, plus `rolex-esto/portfolio` `data/projects.ts`, plus GitHub's API for public repos. Nothing was invented.
- Stacks shown only where verified: BahaRoute (repo `package.json` + languages), Ulan Ba?, Weather Weather Lang, Classic Flagship Store (portfolio data). OpsPilot shows "Focus" (portfolio). BizPilot shows "Key features". SmartWatts and TAPME show no stack.
- Classic Flagship Store role "Lead Developer" comes from portfolio data. Ulan Ba? live demo omitted (404).
- Team attribution is explicit: Weather Weather Lang and BahaRoute are "team project", SmartWatts is "Team KuryenTech".

## 5. Validation

| Check | Result |
|:--|:--|
| README suite, local mode (GitHub `/markdown` API in README mode + github-markdown-css), 320/375/390/430/768/1280/1440 × light/dark | **Chromium 196/196, WebKit 196/196, Firefox 196/196** |
| Unit tests `python3 -m unittest discover -s tests` | **36/36** (24 existing + 12 new) |
| Links and images in README | 84 local paths exist; 18 remote URLs return 200 (LinkedIn included) |
| SVG well-formedness | 65/65 `assets/readme` + 2 dashboard files parse |
| Third-party/tracker/arcade scan | none |

Not verified: **github.com itself.** No branch was pushed, as instructed. The local harness uses GitHub's own sanitizer but not github.com's page chrome, and it emulates `<themed-picture>`. Before merging, run `README_URL=https://github.com/rolex-esto/rolex-esto/blob/feature/premium-profile-redesign/README.md node tests/readme.github.cjs` for each engine.

## 6. Open items for the owner

1. **BahaRoute role:** the README says "Lead Developer", but portfolio data says "Hackathon Team Contributor". Kept "Lead Developer · team project". Please confirm.
2. **Event spelling:** "BuildOvernights KiroxHackaton" (README) vs "KiroxHackathon" (portfolio). Kept the README spelling.
3. The hero's small text is decorative on phones (about 4–6 px at 320 px). Every fact in it is repeated as Markdown text right below.
4. GitHub Pages is still enabled and serves 404 (noted in the PR #4 audit). Unchanged.
5. SVG text uses system fonts, so glyph widths vary slightly by OS. Cards have padding and an overflow guard in the generator.
