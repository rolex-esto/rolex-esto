# GitHub Isometric Developer Dashboard: Audit

## Revision 2: Midnight Pixel redesign (2026-11-17)

**Branch:** `feature/isometric-overview`, fast-forwarded to `main` @ `286434b`
**Verdict: PASS_WITH_LIMITATIONS**

### R2.1 Initial findings
- **PR #5 was already merged** (by the owner, 2026-11-17 02:36 UTC, merge commit `286434b`), so it could not be updated. This revision sits on the same branch, ready for a new PR if the owner approves one.
- **The Primooo screenshot was still not available** to the implementer. The redesign follows the written spec only.
- The left panel is live on the profile through the `output` branch. To avoid showing new-palette stats next to the old-palette art on the live profile, the workflow was **not** run from this branch. The new left panel was generated locally with the same script and tested on github.com through the `OVERVIEW_DIR` override (see R2.6).

### R2.2 Design system
| Role | Dark (Midnight Pixel) | Light (Pastel Dusk) |
|:--|:--|:--|
| Background / surface / secondary surface | `#0B0F19` / `#171C2B` / `#232A3B` | `#FBF8F2` / `#F3EEE4` / `#E9E2D4` |
| Primary / secondary text | `#F5EBD7` / `#A6ADBB` | `#2B2638` / `#5C5768` |
| Primary / secondary accent | `#B8A4FF` lavender / `#A8C7FA` pastel blue | `#6B54D6` / `#345F9E` |
| Contributions / highlight | `#A8D8B9` sage / `#FFD6A5` peach | `#2E6E4A` / `#9A4F12` |
| Border | `#394156` | `#D6CCBA` |

The light-mode accents are darker versions of the pastels. Without that, they fail WCAG AA on cream: `#3D6FB8` measured 4.36:1, sage 3.96:1 and orange 4.28:1, so all three were darkened.

There is **no `#00C389` or `#0EA5E9` left** in either panel, the generated cards, the README or the snake. The README check counted 0 occurrences of the old palette.

### R2.3 What changed
- **Left panel:**
  - avatar as a rounded pixel tile with a lavender border; name, handle, and **account age** ("2 years on GitHub · since Nov 17, 2024")
  - account totals; a large 12-month contribution total with dates
  - 2-column cards for public commits, PRs and issues, repos committed to, and streaks
  - **sage-green isometric blocks** in five intensity levels from GitHub's own `contributionLevel`, shaded faces and a soft pastel rim light on tall towers. Height still comes from the real daily count.
  - busiest day, calendar and legend
- **Right panel:** a redrawn original scene (96 × 72 art pixels):
  - setting: lavender evening sky in seven dithered bands with a warm horizon glow, pastel clouds, layered dusk hills, sage grass with flowers, stepping-stone path
  - cottage: timber frame, lavender roof, glowing windows with flower boxes, door lantern, chimney smoke
  - tree; desk with a retro monitor, desk lamp and light pool, mug with steam, plant
  - a developer in lavender headphones; a peach cat; fireflies (night) or butterflies (dusk)
  - animation: drifting clouds, twinkling stars, typing code lines, blinking cursor, blinking eye, head bob, tapping hands, cat blink and tail wag, swaying grass, rising smoke and steam
  - 43 animations in dark and 29 in light, and **0** under `prefers-reduced-motion`
- **Technology chips:** one pastel colour per category. Languages lavender, Frontend pastel blue, Backend warm cream, Data Engineering sage, Cloud soft orange, Developer Tools & AI muted purple. Same technologies as before, regrouped (Node.js and FastAPI moved under Backend).
- **Rest of the README:**
  - recoloured: banner and footer wave, dividers, section icons, shields badges, typing line, view counter, and the snake
  - **colour values only.** With hex values normalised, the README matches `main` line for line, except the hidden palette comment (394 = 394 lines).

### R2.4 Mobile readability
- Every text element in both panels is **≥ 16 units**, up from 13. Panels are now 410 × 1012.
- Smallest rendered dashboard text: about 9.9 px at 320, 12.1 at 375, 12.6 at 390, 14.2 at 430, and 16 at 768 and 1280.
- Languages card footnote: 13 → 15 units (9.5 px at 320).

### R2.5 Files changed
- `scripts/generate-dashboard-art.py` (rewritten) and `assets/dashboard/portfolio-{dark,light}.svg`
- `scripts/generate-github-stats.py`: new palette and layout for the overview, `account_age`, recoloured cards
- `README.md` (colour values) and `.github/workflows/snake.yml` (snake colours)
- `tests/test_dashboard_theme.py` (new), `tests/test_stats.py`, `tests/readme.github.cjs`
- screenshots: `docs/audit/midnight-*.png`, replacing the PR #5 screenshots

### R2.6 Testing (all actually run)
| Check | Result |
|:--|:--|
| Unit tests: `python3 -m unittest discover -s tests -p "test_*.py"` | **21/21 OK** |
| Covered by those tests | Old teal/blue absent; every text ≥ 16 units; WCAG AA (≥ 4.5:1) for every text colour on its real background, including each chip label on its own tint; reduced-motion rule present; level colours ordered; account age; plus the 14 stats tests (streaks, pagination, empty year, API failure keeps old images) |
| github.com rendering of the branch, 320 / 375 / 390 / 430 / **768** / 1280 px × light/dark, `OVERVIEW_DIR` = locally generated activity and languages cards | **124/132 in each of Chromium, WebKit and Firefox.** Every dashboard check passed: panels load, side by side at 1280, stacked below that, stricter in-image text thresholds (9.5 / 11.5 / 12 / 13 / 14 / 14 px), no broken images, theme switching, no overflow |
| Failing checks | The only 8 failures are the inherited sideways-scrolling tables (Trophy Wall, Experience); those tables are unchanged |
| Animation and reduced motion | 3 engines: running without the preference, 0 animations with `reducedMotion: reduce` |
| Links | **126/126** README URLs return HTTP 200, including every recoloured capsule-render, Iconify and shields URL |
| Statistics accuracy | The generator's data path is unchanged since the R1 cross-check against REST and Search (followers, repos, stars, issues, public PRs) |

Not run: the GitHub Actions workflow from this branch, on purpose (see R2.1). It runs automatically when this branch is merged to `main`, and should be checked then.

### R2.7 Content preservation
- Hex-normalised diff of the README against `main`: 0 changed lines of content.
- All 18 + 1 headings, 23 certificate image references, every project, certification, training, recognition, experience, leadership and hackathon entry, and every URL are unchanged.

### R2.8 Remaining limitations
1. The reference screenshot was never available.
2. PR #5 is merged, so this revision needs a **new PR** (the owner's decision).
3. After merge, the first workflow run on `main` publishes the new left panel and the recoloured languages card and snake. Until then, the live profile keeps the old ones.
4. Panels are taller (1012 units) because of the larger text.
5. Inherited mobile tables. "Rolex Esto" in the left panel comes from the GitHub profile name. FastAPI and GitHub Actions come from the owner's list. GitHub Pages is still enabled.

---

## Revision 1: original dashboard (merged in PR #5)

**Date:** 2026-11-17 · **Branch:** `feature/isometric-overview` · **Base:** `main` @ `2068ef9` (after PR #4)

**Verdict: PASS_WITH_LIMITATIONS.** The Developer Overview dashboard is live on the branch with real GitHub data. It has an isometric 3D graph, an original animated pixel scene and technology chips. It renders correctly on github.com in Chromium, WebKit and Firefox, in light and dark, from 320 px to 1280 px. All existing README content is kept. The limitations are in section 11, the main one being that **the reference screenshot was never available to the implementer**.

## 1. Initial repository findings

- `main` at `2068ef9`. Working tree clean apart from the untracked local `.agent-handoff/`.
- `feature/isometric-overview` already existed on the remote but had **no unique commits** (it pointed at an ancestor of `main`). There was no unfinished work to protect, so this branch continues it from current `main` with a fast-forward push.
- README: the restored pre-arcade layout (PR #4). Teal `#00C389` → sky `#0EA5E9` palette, Iconify `pixelarticons` section icons, capsule-render dividers, skillicons and shields.io badges.
- Stats: `.github/workflows/snake.yml` already ran a hardened pipeline. It has a read-only generate job, a separate write-only publish job, SHA-pinned actions and a validate-before-publish gate. It publishes to the `output` branch: the snake from `Platane/snk` and the self-hosted stats cards from `scripts/generate-github-stats.py`.
- External image providers in the README: capsule-render, readme-typing-svg, shields.io, skillicons.dev, api.iconify.design, komarev (views), github-readme-stats-fast and streak-stats.demolab.

## 2. Design reference interpretation

**The "Primooo" screenshot was not provided to this session and was not found on disk.** It was not inspected. The design follows the written brief:

- a bordered two-column dashboard
- left: avatar, account and activity stats, contribution calendar, isometric 3D contribution graph
- right: an original animated pixel scene with colourful technology badges below
- dark first, with a light variant, in the owner's palette (`#0D1117`, `#161B22`, `#30363D`, `#00C389`, `#0EA5E9`, `#A78BFA`, `#C9D1D9`)

Send the screenshot to get a fidelity pass on proportions, colours and badge style.

## 3. Implementation details

**Layout.** Two SVG panels, each 410 × 772 and shown at `width="410"`, sit inline in one `<p align="center">`. On desktop they line up side by side as one dashboard. On narrower screens GitHub's `max-width:100%` makes them wrap into one stacked, full-width column. This needs no tables, media queries or scripts. Each panel is a `<picture>` with dark and light sources.

**Left panel: generated daily from real data** (`overview-activity-{dark,light}.svg` on the `output` branch). It shows:
- avatar (embedded as a data URI; initials if the download fails), name, handle, join date
- **Account totals:** public repos, followers, stars earned (summed over owned public non-fork repos, with pagination)
- **Last 12 months**, with the exact date range printed: public commits, public PRs, public issues, repos committed to, current and longest streak
- **3D contributions:** a 53 × 7 isometric grid. Each block's height is `3 + 57·√(count / peak)` from the real daily count, so a single busy day does not flatten the rest of the year. The colour is GitHub's own `contributionLevel`. Faces are shaded for light and shadow, tall towers get a highlight edge, and the graph sits on a ground shadow. It also prints the busiest day.
- **Calendar:** a flat 53-week heatmap with a Less/More legend and the year's total

**Right panel: static** (`assets/dashboard/portfolio-{dark,light}.svg`, from `scripts/generate-dashboard-art.py`). It shows:
- an original 96 × 66 pixel scene drawn with 4-unit pixels (`shape-rendering: crispEdges`): a developer on a stool coding at a retro monitor outside a small purple-roofed house, a tree, hills, grass and a path
  - dark: night, crescent moon, twinkling stars, fireflies
  - light: day, sun, white clouds, butterflies
  - animation: drifting clouds, blinking eye, code lines typing, blinking cursor, steam from the mug, swaying grass, floating fireflies or butterflies
  - all of it is CSS inside the SVG and turns off under `prefers-reduced-motion`. The still frame is a complete picture, and there is no sound.
- branding: "Rolex J. Esto · Software · AI · Data · Cloud · Founder of BizPilot · Microsoft Certified DP-700"
- technology chips: brand-tinted, with a brand-colour square and centred labels. They are grouped exactly as the brief lists them: Languages, Frameworks, Data, Cloud, Tools & AI.

**README changes**
- New `## Developer Overview` section placed after the header and before About Me, with alt text that lists every metric and every technology, and a note that explains the data scope.
- In **GitHub Stats**, the third-party stats card and streak card are removed, because the overview now shows the same numbers. The top-languages card switched to the self-hosted one from the same pipeline. The snake stays.

**Isometric generator: build vs. reuse.** I evaluated `yoshi389111/github-profile-3d-contrib`: MIT licence, about 1.8k stars, last push 2026-11-05, latest release v0.9.3 (2026-06-15), not archived. It is well maintained. I still did not use it, for three reasons:
1. It produces a full standalone card in its own style, not a panel that fits the dashboard and palette.
2. It would add a second third-party action and a second publish path.
3. The existing pipeline already fetches the exact calendar data needed.

The custom renderer is about 80 lines inside the existing script.

## 4. Files changed

| File | Change |
|:--|:--|
| `scripts/generate-github-stats.py` | Extended query (join date, avatar, followers, public repos, stars with pagination, issues, weekday and level per day). New overview, isometric and calendar renderers. Avatar fetch with fallback |
| `.github/workflows/snake.yml` | Validates the two new files (XML, at least 300 calendar cells, 3D graph present) before publishing. Permissions unchanged (`{}` by default; generate `contents: read`, publish `contents: write`) |
| `scripts/generate-dashboard-art.py` | New. Static pixel-art and tech-chip panel generator |
| `assets/dashboard/portfolio-{dark,light}.svg` | New generated assets (about 53 KB each) |
| `README.md` | Developer Overview section, plus GitHub Stats de-duplication |
| `tests/test_stats.py` | New. 14 unit tests |
| `tests/readme.github.cjs`, `tests/README.md` | Overview layout checks and documentation |
| `docs/audit/dashboard-*.png` | Screenshots of the real github.com rendering |
| `GITHUB_ISOMETRIC_DASHBOARD_AUDIT.md` | This report |

## 5. GitHub data sources

All numbers come from the GitHub GraphQL API, called by the workflow with the built-in `GITHUB_TOKEN`. No personal access token is stored, and no third-party stats service is involved.

| Metric | Field | Scope |
|:--|:--|:--|
| Join date, followers | `user.createdAt`, `followers.totalCount` | Lifetime |
| Public repos | `repositories(privacy: PUBLIC, ownerAffiliations: OWNER).totalCount` | Current |
| Stars earned | Σ `stargazerCount`, owned public non-fork repos, paginated | Current |
| Public commits, PRs, issues, repos committed to | `contributionsCollection.total*` | Last 12 months, public. Dates printed on the panel |
| Streaks, calendar, 3D graph, total | `contributionCalendar` | Last 12 months. Includes the private contribution **counts** the profile already shows publicly, marked `*` |

Private repository names, content and details are never read. Streaks are never presented as lifetime values.

**Cross-check against independent endpoints (2026-11-17):**
- REST `users/rolex-esto`: created 2024-11-17, 1 follower, 5 public repos. Matches.
- REST repo list: 0 stars. Matches.
- Search API, public issues in the window: 0. Matches.
- Search API, **public** PRs in the window: 14. Matches. Search without `is:public` returns 184, because it includes private repositories. That is why the panel says "Public PRs".

## 6. Stats refresh strategy

- **When it runs:** daily cron (`17 3 * * *` UTC), on push to `main`, and on manual dispatch.
- **Publishing:** the generate job writes nothing on any API, data-sanity or XML failure. A bad set never reaches the publish job, so the previous images on `output` stay as they are. Each file is written atomically.
- **Verified on this branch** with two real runs: [44003277621](https://github.com/rolex-esto/rolex-esto/actions/runs/44003277621) and [44003451642](https://github.com/rolex-esto/rolex-esto/actions/runs/44003451642). Both succeeded, the avatar was embedded, and the validation gate passed (367 calendar cells).

## 7. Mobile testing results

`tests/readme.github.cjs` ran against the branch as rendered by **github.com itself**, at 320, 375, 390, 430 and 1280 px, dark and light, in Chromium, WebKit and Firefox. **Each engine passed 102 of 110 checks.**

| Check | Result |
|:--|:--|
| Overview panels load (both themes) | PASS, every width and engine |
| Side by side at 1280 px / stacked at ≤ 430 px | PASS, every width and engine |
| Smallest text inside SVG images | 8.1 px at 320 px, 10.3 px at 390 px, 13 px at desktop. PASS (thresholds 8 / 9.5 / 11) |
| Broken images, page overflow, real text ≥ 12 px, `<picture>` theme switching, project headings, no game wording or links | PASS |
| Sideways-scrolling tables | **FAIL ×8, inherited.** Trophy Wall, Experience, and the projects grid at 320 px. These tables are unchanged from the original layout and were already documented in the pre-arcade restore audit |

Other checks:
- **Animation:** 31 animations run (24 in light mode) in all three engines, and **0** with `reducedMotion: reduce`.
- **Unit tests:** `python3 -m unittest discover -s tests -p "test_*.py"` gives **14/14 OK**.
- **Links:** 126/126 README URLs return HTTP 200, and every local image path exists.

## 8. Dark/light screenshots

Real github.com rendering of this branch:
The R1 screenshots were replaced by the Revision 2 screenshots (`docs/audit/midnight-*.png`). The originals are in Git history at `c5019e2`.

## 9. Content preservation results

The `main` README was compared with the branch README by script, line by line.

- **Lines removed: 9.** They are exactly the source and image lines of the three third-party cards that the overview replaced (GitHub stats, top languages, streak).
- Headings: all 18 kept, plus 1 new.
- Certificate image references: 23 → 23.

| Area | Status |
|:--|:--|
| Projects: BizPilot, SmartWatts, OpsPilot, BahaRoute, Weather Weather Lang, Ulan Ba?, Classic Flagship Store, TAPME, plus Project details | ✅ unchanged |
| Certifications: DP-700 (with verification link), DataCamp ×4, ISC2 CC, Appkademiya CCP, CTIGA, Google AI | ✅ unchanged |
| Training: AWS SimuLearn, Microsoft DP-900/DP-700/PL-300 tracks, DICT Region V | ✅ unchanged |
| Professional recognition: DICT Category 2 | ✅ unchanged |
| Experience: TAPME, BizPilot, Eskwelabs EIF, GCI World 2026 | ✅ unchanged |
| Leadership and affiliations | ✅ unchanged |
| Hackathons: Top 2, 3rd, Top 10, Top 36 / Climate Top 10 | ✅ unchanged |
| Education: STI College Fairview BSIT 2023–2027 | ✅ unchanged |
| URLs: portfolio, LinkedIn, email, GitHub, project and demo links, Microsoft Learn | ✅ all present, all HTTP 200 |
| Certificate image paths | ✅ 23/23, files exist |

## 10. Accessibility findings

- Both panels have descriptive `alt` text in the README. The alt text lists every metric name and all 30 technologies. Each SVG also has `<title>` and `<desc>`, and the generated `<desc>` contains the live numbers.
- The full technology list also stays as real text in the Tech Stack section.
- Contrast: muted text `#8B949E` on `#161B22` is about 5:1 (dark). `#57606A` on `#F6F8FA` is about 6:1 (light). Chip labels use the strongest text colour on a 16% brand tint.
- Motion: everything is decorative and subtle, stops under `prefers-reduced-motion`, has no flashing above 3 Hz, and plays no sound.
- These automated checks are evidence, not a certification. A real screen reader and real devices were not tested.

## 11. Remaining limitations

1. **The reference screenshot was not available.** The design follows the written brief only.
2. **"Live" means daily.** The panel refreshes once a day (UTC) and on pushes to `main`. Running the workflow on this branch already published the new overview files to `output`. This is harmless, because the live README on `main` doesn't reference them yet.
3. **Small text on the smallest phones.** At 320 px the smallest SVG label renders at about 8 px. The panel is legible but tight there, and every value is also in the alt text.
4. **Inherited mobile tables.** Trophy Wall and Experience still scroll sideways on phones (see the pre-arcade restore audit).
5. **Name difference.** The overview shows the GitHub profile name ("Rolex Esto"). The README and right panel use "Rolex J. Esto".
6. **Unverified technologies.** FastAPI and GitHub Actions appear in the dashboard because the owner's brief lists them, but they are not in the README's Tech Stack text. They were not verified independently.
7. **Desktop width.** Side by side needs about 830 px of README width. Narrower desktop windows show the panels stacked, which still renders correctly. The profile page itself (github.com/rolex-esto) can only be checked after merge.
8. **GitHub Pages** is still enabled from the arcade era. It was not changed.

## 12. Final verdict

**PASS_WITH_LIMITATIONS.** The dashboard is implemented, data-accurate, automated with least privilege and safe on failure, tested on github.com in three engines, and keeps all content. The pull request is open and **not merged**. Deployment: **NOT DEPLOYED** to the profile until you merge.
