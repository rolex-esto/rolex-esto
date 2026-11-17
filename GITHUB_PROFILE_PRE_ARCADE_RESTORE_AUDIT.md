# GitHub Profile: Pre-Arcade Restore Audit

**Date:** 2026-11-17 · **Branch:** `revert/restore-pre-arcade-profile` · **Base:** `main` @ `1fbc8aa` (after PR #3)
**Backup of main:** `backup/main-before-pre-arcade-restore` → `1fbc8aa` (pushed)

**Verdict: PASS_WITH_LIMITATIONS.** The README is restored to its last pre-arcade design with newer verified details. All arcade and game-themed files are removed. The only failing check is sideways-scrolling tables on phones, which the original design already had (see section 6).

## 1. Pre-arcade commit identified

| Commit | Date | What it is |
|:--|:--|:--|
| `fef5b05` | 2026-11-16 | Last real README edit before the arcade ("Align profile README with updated resume") |
| `7b2e32f` / `6bd2c6e` | 2026-11-16 | A "Redesign profile README" merge, reverted by the owner right away |
| **`7decc54`** | **2026-11-16 23:42** | **Revert of that redesign. Its tree is identical to `fef5b05` (`git diff fef5b05 7decc54` is empty). This is the restore source.** |
| `5e1f2ac` | 2026-11-17 00:02 | **First arcade commit** ("feat: add playable pixel arcade portfolio quest"). Parent: `7decc54` |

The game-inspired changes that followed, in order: `4b9d6e1` (pixel arcade README hub, quests), `4ff3387` and `97386f4` (pixel arcade hero), `42846b4` (BUG HUNTER game), `5d85f96` (pixel hero, world map, buttons), `cb1d303` (README as "ROLEX.EXE developer quest"), `8422bb7` (Pages hosting files), PR #1 (`9daeef1` modern redesign with arcade section and pixel assets), PR #2 (arcade fixes, game screenshot), and PR #3 (pixel HUD "about" and "skills" panels).

## 2. Original README design recovered

Commit `7b97169` copies `README.md` byte-for-byte from `7decc54`. The design it brings back:

- Capsule-render wave banner (teal `#00C389` → `#0EA5E9`), typing tagline, shields.io badges, profile view counter
- Sections in the original order: About Me, Trophy Wall, Featured Projects (2-column table + "Project details"), Experience, Tech Stack (skillicons and badges), Certifications (featured DP-700 plus category galleries and journey), Leadership & Affiliations, GitHub Stats, Let's Connect, wave footer
- Themed Iconify `pixelarticons` section icons and GitHub Stats/Streak cards with light and dark variants

These were all in the pre-arcade README, so they are kept. "Trophy Wall" is the original section title. It is a common README heading, not part of the game. Renaming it would depart from the original, so that is left for you to decide (see section 6).

## 3. Professional information preserved or updated

Commit `54b9427` adds newer verified details without changing the layout. They come from the post-arcade README, which was checked against the portfolio data during PR #2.

| Area | Change |
|:--|:--|
| BizPilot | Added live site link `biz-pilot-msme.vercel.app` (HTTP 200) |
| SmartWatts | Added "Top 10 Finalist" and "Lead Developer, Team KuryenTech" |
| OpsPilot | Added "Top 2 Winner" and "Solo Developer" |
| BahaRoute | Added "Top 10 Climate Change Track", "Lead Developer" and the live demo `baha-route.vercel.app` (200) |
| Weather Weather Lang | Added the event name. The link is now labelled "Team repo" because the repository belongs to the team |
| Ulan Ba? | Added "Creator & Frontend Developer". **Removed the live link** `kiro-ph-weather.vercel.app`, which returns **404** |
| Classic Flagship Store | Added site link `classicflagshipstore.com` (200) |
| Certification badges | Changed "10 certifications" to **9 certifications + 1 DICT professional recognition**. Security: 4 → 3. Training: 2 → 5 |
| Training | Added the Microsoft DP-900, DP-700 and PL-300 curriculum tracks (Jul–Oct 2026) to Fellowships, the journey table and the footnote |

**Checklist:** DP-700 (featured, with Microsoft Learn verification link) · ISC2 CC and the other 7 certifications · DICT Category 2 recognition · four hackathon top finishes · Eskwelabs EIF Cohort 11 · GCI World 2026 · TAPME · BizPilot founder role · education (STI College Fairview BSIT, 2023–2027) · leadership and affiliations: **all present**.

## 4. Files removed or retained

**Removed** (commit `664ffb5`; all still in Git history and on the backup branch). Each was checked to have no remaining reference outside the arcade, its audit, or the post-arcade READMEs:

| Path | Why |
|:--|:--|
| `arcade/` (13 files) | The ROLEX.EXE: BUG HUNTER game |
| `assets/arcade/` (13 SVGs), `assets/pixel-arcade-banner.svg` | Arcade buttons, quest map, hero and footer |
| `scripts/generate-pixel-assets.py` | Generator for `assets/arcade/` |
| `assets/profile/` (25 files), `scripts/generate-profile-assets.py` | Assets for the game-inspired redesigns (PR #1–#3): pixel hero, HUD panels, "Play" button, gameplay screenshot. The generator says it exists to "share one visual identity" with the arcade. The restored README uses none of them |
| `index.html` | GitHub Pages redirect into `arcade/` |
| `tests/arcade.qa.cjs` | Tests that only cover the game |
| `ROLEX_EXE_FINAL_AUDIT.md`, `docs/audit/arcade-*.png`, `docs/audit/readme-{dark,light-mobile}.png` | Game documentation and its screenshots |

**Retained:**

- `assets/certs/**` and `dict-cyberpro-badge.png` (used by the README)
- `.github/workflows/snake.yml` and `scripts/generate-github-stats.py` (contribution snake, plus the self-hosted stats cards on the `output` branch)
- `GITHUB_PROFILE_REDESIGN_AUDIT.md`, `GITHUB_PROFILE_UX_REFINEMENT_AUDIT.md` and their `docs/audit/profile-v2-*` and `ux-*` screenshots (historical record)
- `.nojekyll` (no effect on the profile)
- `tests/readme.github.cjs` (updated, see below)

**Tests updated:** the README suite now checks all 8 project headings and light/dark `<picture>` switching (on the snake image, since the original banner is not themed). It also asserts that no arcade or game wording and no Pages/arcade links appear. The checks tied to the removed design ("hero-*.svg", "Problem:" lines) are gone, and so is the unused `@axe-core/playwright` dependency.

## 5. Validation results

| Check | Result | Evidence |
|:--|:--|:--|
| GitHub rendering, github.com's own pipeline | 82/90 in **Chromium, WebKit and Firefox** | `node tests/readme.github.cjs` against the branch blob URL; 320/375/390/430/1280 px × light/dark |
| Images load | PASS, 0 broken (all engines and widths) | Same suite |
| Light/dark mode | PASS, the correct `<picture>` source is served in each scheme | Same suite. Screenshots reviewed at 390 px light and 1280 px dark |
| Real text size | PASS, ≥ 12 px everywhere | Same suite |
| Page overflow on mobile | PASS, 0 px | Same suite |
| Tables on mobile | **FAIL** (inherited): see section 6 | Same suite |
| Remote links and images | PASS, **126/126 URLs return HTTP 200** (projects, demos, Microsoft Learn, LinkedIn, badges, icons, stats) | `curl -L` on every URL in README.md |
| Local assets | PASS, 22/22 certificate images and thumbnails exist | Path check |
| GitHub statistics | PASS. Stats, top-languages and streak cards return real data (122 commits, 1,263 contributions). The snake still comes from this repo's workflow | Card contents fetched and inspected |
| No ROLEX.EXE / game content | PASS, no ROLEX.EXE, arcade, quest, XP, level or "play" text, and no `github.io` or `arcade/` links | Suite plus `grep` |
| Unrelated content | Unchanged. The diff touches only README.md, the removed files above, tests/ and this report | `git diff --stat main...` |

## 6. Unresolved differences and limitations

1. **Tables scroll sideways on phones (inherited from the original).** Trophy Wall (4 columns) scrolls at 320–430 px. Experience (3 columns) scrolls at 320–390 px. The projects grid scrolls only at 320 px, by 24 px. The page itself never overflows. Fixing this means changing the original table layout, which this restore was asked not to do. If you want it, the lightest fix is short month names in Experience and removing the icon-only column in Trophy Wall.
2. **Third-party stats services.** The original design uses `github-readme-stats-fast.vercel.app` and `streak-stats.demolab.com`. They work today, but they are outside services and have had outages and rate limits before. The workflow still publishes self-hosted cards (`output/stats-activity-*.svg`, `stats-languages-*.svg`) as a drop-in fallback.
3. **"Trophy Wall" heading and pixel-style icons** are kept because they were part of the original pre-arcade design (added by `fc20dc6`, 2026-11-11).
4. **GitHub Pages:** see section 7.
5. Open items from earlier audits that this task did not settle: the exact wording of the BahaRoute role, and whether the portfolio site's data still lists DP-700 as training only.

## 7. GitHub Pages

- **Current config:** enabled, legacy build from `main` / root, public, `https://rolex-esto.github.io/rolex-esto/`.
- **Finding:** Pages was **enabled only for the arcade**. Before the arcade, `GET /repos/rolex-esto/rolex-esto/pages` returned 404 (`ROLEX_EXE_FINAL_AUDIT.md` at `8422bb7`). It was turned on in PR #1 "so the arcade can launch as its own site" (`GITHUB_PROFILE_REDESIGN_AUDIT.md`).
- **After merge:** `/` and `/arcade/` will return 404, because `index.html` and `arcade/` are gone. Nothing in the README links to Pages.
- **Not changed.** If you approve, disable it in Settings → Pages, or run `gh api -X DELETE repos/rolex-esto/rolex-esto/pages`.

## 8. Final restoration verdict

**PASS_WITH_LIMITATIONS.** The README matches the pre-arcade design from `7decc54`, all game elements and arcade files are gone, every professional fact listed in the task is present and up to date, and history is preserved. Commits are ordinary and nothing was force-pushed. `main` is untouched and backed up. **The PR is open and not merged.** Deployment status: **NOT DEPLOYED** until you merge.
