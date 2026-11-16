# GitHub Profile Redesign — Audit

**Branch:** `feature/profile-modern-redesign` (from `main` @ `8422bb7`)
**Date:** 2026-11-17
**Verdict:** **PASS_WITH_LIMITATIONS**. The redesign is implemented, rendered through GitHub's Markdown API, link-checked and visually reviewed. The arcade is live on GitHub Pages and passed the full test suite in production. Remaining limitations are listed in section 8.

---

## 1. Inspiration references (what I took, and didn't)

| Reference | Pattern adopted | Deliberately not copied |
|:--|:--|:--|
| [topics/readme-profile](https://github.com/topics/readme-profile) | Hero → about → projects → stack → stats → contact order; a quick-scan link row | Visitor badges and "fun facts" filler |
| [salesp07/salesp07](https://github.com/salesp07/salesp07) | Centered hero with compact contact badges; typing headline | Third-party typing service (`readme-typing-svg`); emoji headings |
| [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats) | Stats-card format | The service itself: **upstream is now marked unmaintained**, and the copy the profile used was slow (~2 s) with a redirecting top-languages URL |
| [lowlighter/metrics](https://github.com/lowlighter/metrics) | Generate stats **inside your own GitHub Action** and publish SVGs | The full plugin system (needs a personal token secret) |
| [Platane/snk](https://github.com/Platane/snk) | Contribution snake with `<picture>` dark/light from an `output` branch | — (kept; recoloured to the profile palette) |
| awesome-github-profile-readme | Project cards in a 2-column grid; collapsible secondary detail | Giant trophy tables, banner GIFs |

The identity is original: a modern GitHub-native layout (system sans type, GitHub's own neutrals) with a **signature pixel accent**. That accent is the pixel developer at a desk, pixel project icons, pixel medals and dividers, and it is shared with the ROLEX.EXE arcade.

## 2. Before / after

| | Before (`main` @ 8422bb7) | After |
|:--|:--|:--|
| Concept | Full-screen RPG: hero "ROLEX.EXE", quest map, trophy chests | Professional portfolio; arcade is one section near the bottom |
| Above the fold | Arcade title + 5 pixel buttons + game notice | Name, three roles, rotating real highlights, 5 contact/nav links |
| Projects | Collapsed `<details>` "worlds" (needed a click) | 6 visible cards (title, achievement, summary, role, stack/highlights, links) + 2 "more work" lines |
| Tech | Table of inline code chips | One categorized stack graphic (8 groups, consistent chips) with full alt text |
| Achievements | Chests, collapsed except hackathons | 4 visible result tiles + a text table + certification summary table; gallery/journey collapsible |
| Stats | Third-party Vercel instances + view counter | Self-generated real-data cards (activity, languages) + snake, built daily by this repo's workflow |
| Arcade | README PLAY linked to source folder (Pages off) | "Take a Break" section → **live** Pages URL + source link |
| Third-party image requests | stats ×3, streak, view counter | **0 third-party services** (all images from this repo or its `output` branch) |

Screenshots: `docs/audit/profile-v2-dark-top.png`, `profile-v2-hero.png`, `profile-v2-cards-light.png`, `profile-v2-components-light.png`, `profile-v2-mobile.png`. The before-state screenshots of the previous version are `docs/audit/readme-dark.png` and `readme-light-mobile.png`.

## 3. Design system

- **Colour:** GitHub neutrals (`#0D1117`/`#161B22`/`#30363D` dark; `#FFFFFF`/`#F6F8FA`/`#D0D7DE` light). Accents carried over from the arcade: green `#70F5A3`/`#0E8A4E`, purple `#A78BFA`/`#6D4ED8`, gold `#FFD166`/`#9A6700`, pink `#FF6B9E`/`#BF3989`. Light-mode accents were darkened for contrast on white.
- **Type:** the system UI sans stack (GitHub's own) for content, monospace for the terminal line. Pixel bitmap text only appears inside the arcade preview.
- **Pixel accents:** desk-scene avatar, project icons, medals, pill icons, dividers. They appear only in the hero, separators, icons and the arcade section.
- **Motion:** rotating typed highlight (4 real facts, 16 s cycle), monitor code lines, blinking cursor, and arcade preview sprites. There are no flashes. Under `prefers-reduced-motion`, all animation stops and the first highlight shows statically.
- **Assets:** 27 SVGs, 106 KB total. They are reproducible with `python3 scripts/generate-profile-assets.py`, which reuses the arcade's sprite/font module.

## 4. Changes made

| File | Change |
|:--|:--|
| `README.md` | Full rewrite in the requested order: Hero → About → Featured Projects → Tech Stack → Achievements & Certifications → Experience & Fellowships → GitHub Stats → Arcade → Contact |
| `assets/profile/*.svg` | New: hero (dark/light), 6 project cards ×2 themes, tech stack ×2, hackathon tiles ×2, arcade preview, divider, 7 link pills |
| `scripts/generate-profile-assets.py` | New asset generator |
| `scripts/generate-github-stats.py` | New. GraphQL with the built-in `GITHUB_TOKEN`; public non-fork repos only; writes activity + language cards (dark/light) |
| `.github/workflows/snake.yml` | Renamed the workflow to "Generate profile graphics"; added checkout + stats step; snake recoloured to the palette. Same schedule, trigger and `output` branch |
| `arcade/README.md` | "Play online" now points to the live Pages URL |
| `GITHUB_PROFILE_REDESIGN_AUDIT.md`, `docs/audit/profile-v2-*.png` | This report + screenshots |

**Content preservation (automated diff against both previous READMEs):**
- Every credential, date, role, organisation, affiliation and project description is still present.
- Every certificate image and thumbnail path, and the DP-700 Microsoft Learn verification URL, are preserved.

Dropped on purpose:
- the dead Ulan Ba? demo URL;
- the old arcade-source links, replaced by the live game URL plus an `arcade/` source link;
- the third-party stats services and the view counter.

**Repository settings:** GitHub Pages enabled (source `main` / root) so the arcade can launch as its own site. This is the only setting changed, and it's reversible under Settings → Pages.

## 5. Test results

| Check | Result | Evidence |
|:--|:--|:--|
| GitHub Markdown rendering | PASS | `gh api markdown` (mode `markdown`, repo context): 6/6 `<details>` balanced, 12 `<picture>`, 7 tables, 0 broken local images |
| Heading anchors | PASS (by rule) | `#featured-projects`, `#achievements--certifications`; slug rule confirmed against the live profile (e.g. "Leadership & Affiliations" → `-leadership--affiliations`) |
| Local image paths | PASS | Every `assets/…` path in README exists |
| External links | PASS | 19/19 return HTTP 200: projects, demos, credential verification, LinkedIn, Pages, `output`-branch stats |
| Stats workflow in CI | PASS | `workflow_dispatch` run 43914762521 on this branch succeeded; generated real data (1,256 contributions, 100 public commits, 7-day streak); files served from `output` (200) |
| Dark/light assets | PASS | All SVGs rendered via `<img>` on dark and white backgrounds and reviewed |
| Hero animation | PASS | Captured at t = 1.5 s / 3 s / 7 s: phrases type in and rotate. A fill-mode bug that hid the text was found and fixed |
| Reduced motion | PASS (assets) | CSS `prefers-reduced-motion` rule disables all SVG animation; static state shows the first highlight |
| Mobile layout | PASS_WITH_NOTE | 390 px render: no horizontal scroll. YAML intro reflowed to short lines after a first pass overflowed. Card text is small on phones (see limitations) |
| Arcade launch URL (production) | PASS | `https://rolex-esto.github.io/rolex-esto/arcade/` 200; the full 69-check Playwright suite run **against the live site**: 69/69 pass (desktop, reduced-motion, mobile portrait/landscape, tablet touch), axe-core 0 WCAG A/AA violations, 0 console errors. One mobile navigation needed a retry (network timeout, then loaded) |
| Accessibility | PASS | Every content image has descriptive alt text (cards/stack/tiles carry their full text); decorative dividers use empty alt; SVGs have `<title>`/`<desc>` |
| Performance | PASS | Local profile assets 106 KB total; no third-party image services |

**Broken links fixed:** the Ulan Ba? live demo (`kiro-ph-weather.vercel.app`, 404) was removed, and the README "Play" link now opens a working hosted game instead of a source folder.

## 6. Accuracy notes
- Stats come from GitHub's GraphQL contribution calendar. "Contributions" includes private contribution *counts* because your profile is set to show them. Commits and PRs are labelled "public".
- In-card summaries were shortened for space. The full original descriptions remain in "Project details".
- No proficiency bars, ranks, or invented metrics were added.

## 7. Deployment status
- **README:** on `feature/profile-modern-redesign`, with a PR open for review. **Not merged.** The live profile still shows the previous version until you merge.
- **GitHub Pages:** **DEPLOYED and verified** (arcade, from `main`).
- **Stats on `output`:** currently generated from this branch's workflow run. Until merge, `main`'s old workflow regenerates `output` daily at 00:00 UTC and will drop the stats files, so the PR preview's stats images may disappear after that. They return on the first run after merge, which triggers automatically on push to `main`.

## 8. Remaining limitations
1. **Project-card text is small on phones.** These are 2-column SVG cards, so at 390 px the card text is ~7 px. Full text is in alt text and "Project details". If mobile matters more than desktop polish, switch to one card per row.
2. **Light/dark swapping in previews:** GitHub's `<themed-picture>` script does the swap on github.com. My offline preview couldn't run it, so light-mode `<picture>` swapping in the README was verified per-asset, not on the live page. This is the same mechanism the snake already uses on your profile.
3. **Owner checks still open from the last audit:** confirm the BahaRoute role (README: Lead Developer; portfolio site: Hackathon Team Contributor), and restore Ulan Ba?'s Vercel domain if you want a live link back.
4. Not tested: real devices, Safari/Firefox, or the GitHub mobile app.

## 9. Final recommendation
Merge `feature/profile-modern-redesign` into `main` after a quick look at the PR's rich diff. Then open your profile once in dark and once in light mode to confirm the theme swap, and run "Generate profile graphics" if the stats cards are missing.
