# GitHub Profile — UX Refinement Audit

**Branch:** `feature/profile-ux-polish` (from `main` @ `36ec7cb`, the PR #1 merge)
**Date:** 2026-11-17
**Verdict:** **PASS_WITH_LIMITATIONS**. Every defect I found is fixed and covered by a committed regression test. The two owner-only accuracy questions remain open (section 6).

All "github.com" results below come from the README **rendered by github.com itself**, with GitHub's own scripts running, including theme switching. They do not come from a local preview.

---

## 1. Defects found (evidence first)

| # | Defect | Evidence | Severity |
|:-:|:--|:--|:--|
| D1 | Featured-project cards unreadable on phones | Real github.com at 390 px: card text ~4–5 CSS px; at 320 px the README column is only **254 px** | High |
| D2 | Text-heavy SVGs (tech stack, hackathon tiles, stats cards) had the same problem | Suite on `main`: smallest image text **2.5 px** at 320 px (stats card at 49% width); 8.3 px even on desktop | High |
| D3 | Two tables scrolled sideways on phones | Suite on `main`: 2 sideways-scrolling tables at 320/375/390 px | Medium |
| D4 | YAML intro clipped on phones ("University o…") | github.com screenshot at 390 px | Medium |
| D5 | Keyboard hints at 11 px (`<kbd>` inside `<sub>`) | Suite on `main`: min real text 11 px at all widths | Low |
| D6 | Certification count overstated: "10 certifications" counted DICT Category 2, which the README itself calls a professional recognition | README text vs. its own footnote; owner's portfolio records classify DICT Cat. 2 as `recognition` | Medium (credibility) |
| D7 | Training list incomplete: README listed 2 tracks; the owner's published records list 5 | `data/certifications.ts` in the portfolio repo: DP-900 (Jul 2026), DP-700 track (Aug 2026), PL-300 (Oct 2026) missing | Low |
| D8 | Weather Weather Lang repo presented as yours alone | `rolex-esto/Kirovers-Hack-Sprint-Shipaton-Edition` is a **fork**; teammate @debiangee has 10 commits vs 6 | Medium (credibility) |
| D9 | Stats labels ambiguous: "Contributions"/streaks include **1,141 private** contribution counts; "Repos contributed to" was public-only | GraphQL `restrictedContributionsCount` = 1,141 | Medium |
| D10 | Third-party snake action ran with a **write** token | Old workflow: single job with `contents: write` | Medium (security) |
| D11 | Stats generation had no retries and no output validation | Code review; failure paths tested (see 5.3) | Low (failure already left old images intact) |
| D12 | Arcade HUD stale after Start in WebKit | Repro: right after Start, `state: playing` but HUD `–` in WebKit; `0/12` after the next frame | Low |
| D13 | Arcade showed a blank canvas while loading; a failed script load would leave a dead START button visible | Code review; regression test added | Low |
| D14 | README arcade preview was a hand-drawn SVG, not the real game | Compared against the actual canvas | Low |

Not defects (verified): the light/dark `<picture>` switching works on github.com (light → `hero-light.svg`, dark → `hero-dark.svg`), which closes the previous audit's open item. There were no broken images or links on `main`, and Pages was serving the game.

## 2. Improvements made

**README (phone-first, identity preserved)**
- **Rule adopted:** images carry identity, not information. Everything a visitor needs to read is now Markdown text.
- **Projects:** each project is a text block with a pixel icon: role, status, achievement, **Problem / Built**, stack, links. Problem statements come from your portfolio's documented problems, or from the original README for SmartWatts. Classic Flagship Store and TAPME are under "More work".
- **Tech stack, hackathons, certifications:** real-text lists (pixel medals for hackathons). The certificate gallery and journey remain collapsible, and all 11 images and the DP-700 verification link are preserved.
- **Hero:** redrawn at 1000×380 with larger type and short rotating highlights. It's followed by a real-text summary line, so the top communicates who, what and where without relying on the image.
- **Discoverability:** a "Play ROLEX.EXE" pill in the top link row, plus a real gameplay screenshot (14.6 KB PNG) in the arcade section.
- **Other:** stats cards display at a fixed 400 px, so they sit side by side on desktop and stack full-width on phones. The YAML intro was reflowed to short lines.
- **Weight:** profile SVGs went from **106 KB to 26.5 KB**.

**Accuracy fixes:** D6 (now "9 certifications · 1 professional recognition"), D7 (training tracks added from your records), D8 ("Team repository"), D9 (labels marked `*` = includes private counts; others say "Public …").

**Stats pipeline (`scripts/generate-github-stats.py`, `.github/workflows/snake.yml`)**
- **Script:** retries transient errors (but not 401/403/404); sanity-checks the calendar (≥ 300 days) and values; validates every SVG as XML; writes atomically. Any failure exits non-zero **before** writing.
- **Workflow:** split into `generate` (`contents: read`, runs third-party actions) and `publish` (`contents: write`, deploy only). Top-level `permissions: {}`. Every action is pinned to a commit SHA. A `concurrency` guard and an explicit validation step run before publish.
- **Schedule:** moved from `0 0` to `17 3` UTC. The history shows the top-of-hour run arriving about 4 hours late.

**Arcade:**
- The HUD now updates synchronously on start and continue (D12).
- Visible loading message; menus stay hidden until ready (D13).
- `modulepreload` hints for all 7 modules.
- Data labels match the README.

**Tests (new, committed):** `tests/readme.github.cjs` (rules R1–R5, run against github.com) and `tests/arcade.qa.cjs` (the existing 69 checks + 3 regression checks), both engine-parameterized. See `tests/README.md`.

## 3. Mobile readability comparison (measured on github.com, dark theme)

| Viewport | Smallest image text, `main` | Smallest image text, branch | Smallest real text, branch | Project descriptions |
|:--|:--|:--|:--|:--|
| 320 px | **2.5 px** | 8.3 px (stats footnote) | 12 px | 16 px Markdown text |
| 375 px | 3.1 px | 10.0 px | 12 px | 16 px |
| 390 px | 3.2 px | 10.5 px | 12 px | 16 px |
| 430 px | 3.6 px | 11.8 px | 12 px | 16 px |
| 1280 px | 8.3 px | 12.7 px | 12 px | 16 px |

The hero is excluded from the image-text rule because it is decorative and its information is repeated as text directly below it. At 320 px the name still renders at ~19 px.

Screenshots: `docs/audit/ux-before-projects-390-light.png` (before), `ux-after-top-390-light.png`, `ux-after-projects-stack-390-light.png`, `ux-after-top-1280-dark.png` (after).

## 4. Link verification
All external README links return HTTP 200: projects, demos, Microsoft Learn DP-700 verification, LinkedIn, the Pages game, and the `output`-branch stats and snake images. Every local asset path in the README exists. The automated diff against `main` shows **no external link or certificate path removed**; only replaced image assets left.

## 5. Workflow verification

5.1 **Daily schedule works (history):** scheduled runs succeeded on Nov 12, 13, 14, 15 and 16 (`43158059808` … `43800754831`). There has not yet been a scheduled run *after* the PR #1 merge. The next one is the first real-schedule test of the new workflow.

5.2 **New workflow, real run on this branch:** `43919737238`: `generate` ✅ (log: `GITHUB_TOKEN Permissions — Contents: read`), `publish` ✅ (`Contents: write`). It generated real data (1,256 contributions incl. 1,141 private counts, 100 public commits), validated 6 SVGs, and published to `output`. All six images served with HTTP 200 afterwards.

5.3 **Failure paths (local):**
- An invalid token gives `HTTP 401`, exit 1, 0 files written.
- An unknown user gives a GraphQL `NOT_FOUND`, exit 1, 0 files.
- A missing token exits 1.
- A pre-existing file survived a failed run unchanged.

In CI, any of these stops the `generate` job, so `publish` never runs and the previously published images remain.

5.4 **Numbers differ by context, and both are real:** a local run (Manila date) showed 1,268 contributions, while CI (UTC date) showed 1,256. Streak "today" is the UTC day.

## 6. Unresolved — needs the owner

| Item | What the records say | What I did |
|:--|:--|:--|
| **BahaRoute role** | README: *Lead Developer*. Portfolio site: *Hackathon Team Contributor*. Repo: you own it and are the top committer (21 of 45 commits; teammates 14 and 10) | **Kept "Lead Developer"** (your README wording). The commit data supports a leading role but doesn't prove the title. Please confirm or change it |
| **Ulan Ba? live demo** | `kiro-ph-weather.vercel.app` still **404**. The latest deployment URL works but is a per-deployment Vercel URL under another project scope | **No demo link shown.** Re-add it once the production domain is fixed |
| **Microsoft training records** | The portfolio data (Oct 18) lists a DP-700 *training* track; the README shows the DP-700 *certification* (Nov 2026, verification link returns 200) | Both shown: the track as training, the certificate as a certification. Update `data/certifications.ts` in the portfolio repo if it should show the certification |

## 7. Test results (actual)

| Suite | Target | Chromium | WebKit | Firefox |
|:--|:--|:--|:--|:--|
| `readme.github.cjs` | `main` (before) | **34/80** | — | — |
| `readme.github.cjs` | branch on github.com | **80/80** | **80/80** | **80/80** |
| `arcade.qa.cjs` | local build of branch | **72/72** | **72/72** (69/70 before the D12 fix) | **72/72** |

The README suite runs 2 themes × 5 widths (320, 375, 390, 430, 1280) × 8 rules. The arcade suite includes an axe-core WCAG 2.0/2.1 A + AA scan (0 violations) and phone/tablet touch play.

**Accessibility statement:** automated checks, including axe-core, pass. That is evidence, **not** an accessibility certification. Screen-reader and real-device testing have not been done.

## 8. Remaining risks
1. The new two-job workflow has been verified via `workflow_dispatch` but not yet via its **schedule**. Check the first scheduled run after merge.
2. Until this PR merges, `main`'s workflow keeps publishing the old (wider) stats design. Harmless.
3. The hero's small text (terminal line, typed highlight) is decorative at 320 px. The same information is real text right below it.
4. No testing on real devices or the GitHub mobile app; engines were tested via Playwright only.
5. Pinned action SHAs need occasional manual updates (Dependabot could automate this).
