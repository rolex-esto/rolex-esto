// README regression suite, run against the REAL github.com rendering (GitHub's own
// Markdown pipeline + scripts, including <themed-picture> theme switching).
//
// Usage:
//   README_URL=https://github.com/rolex-esto/rolex-esto/blob/<branch>/README.md \
//   BROWSER=chromium|webkit|firefox node tests/readme.github.cjs
// Default URL is the live profile repository page.
//
// Rules enforced (from GITHUB_PROFILE_UX_REFINEMENT_AUDIT.md):
//  1. No broken images; no horizontal page overflow; no table that scrolls sideways.
//  2. <picture> serves the asset matching the colour scheme (checked on the contribution snake).
//  3. Real text in the README is >= 12 px at every tested width.
//  4. Any content image that contains SVG <text> renders that text >= MIN_IMG_TEXT px,
//     except the banner (decorative; its information is repeated as Markdown text).
//  5. Every featured project has a visible text heading.
//  6. Developer Overview panels load: side by side at desktop width, stacked on phones.
//  7. No arcade/game branding or links remain (pre-arcade restore, see
//     GITHUB_PROFILE_PRE_ARCADE_RESTORE_AUDIT.md).
const pw = require('playwright');
const engine = pw[process.env.BROWSER || 'chromium'];
const URL = process.env.README_URL || 'https://github.com/rolex-esto/rolex-esto';
const SHOTS = process.env.SHOTS || '';
const WIDTHS = [320, 375, 390, 430, 768, 1280];
// Smallest rendered text inside README SVGs (px). The dashboard uses >= 16-unit text in 410-unit panels.
const MIN_IMG_TEXT = { 320: 9.5, 375: 11.5, 390: 12, 430: 13, 768: 14, 1280: 14 };
// OVERVIEW_DIR=<dir with overview-activity-{dark,light}.svg>: serve a locally generated activity panel instead of
// the one published on the output branch, to test an unpublished design on github.com's real rendering.
const OVERVIEW_DIR = process.env.OVERVIEW_DIR || '';
const OVERVIEW_RE = /raw\.githubusercontent\.com\/rolex-esto\/rolex-esto\/output\/(overview-activity-(?:dark|light)\.svg)/;
const fs = require('fs');
const path = require('path');
const PROJECTS = ['BizPilot', 'SmartWatts', 'OpsPilot', 'BahaRoute', 'Weather Weather Lang', 'Ulan Ba?', 'Classic Flagship Store', 'TAPME'];
const GAME_TEXT = /ROLEX\.EXE|arcade|BUG HUNTER|\bquest|\bXP\b|level up|play (the|my) game/i;

const results = [];
let fails = 0;
const check = (name, ok, info = '') => { results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${info ? '  — ' + info : ''}`); if (!ok) fails++; };

(async () => {
  const b = await engine.launch();
  const svgCache = new Map();
  for (const scheme of ['dark', 'light']) {
    for (const w of WIDTHS) {
      const mobile = w < 800;
      const ctx = await b.newContext({
        viewport: { width: w, height: 900 }, colorScheme: scheme, deviceScaleFactor: mobile ? 2 : 1,
        isMobile: mobile && (process.env.BROWSER || 'chromium') !== 'firefox', hasTouch: mobile,
      });
      const p = await ctx.newPage();
      if (OVERVIEW_DIR) await p.route(OVERVIEW_RE, route => route.fulfill({
        contentType: 'image/svg+xml', body: fs.readFileSync(path.join(OVERVIEW_DIR, route.request().url().match(OVERVIEW_RE)[1])) }));
      await p.goto(URL, { waitUntil: 'load', timeout: 90000 });
      await p.waitForSelector('article.markdown-body', { timeout: 30000 });
      await p.evaluate(async () => { // load lazy images
        for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
        window.scrollTo(0, 0);
      });
      await p.waitForTimeout(1500);
      const tag = `[${scheme} ${w}]`;
      const r = await p.evaluate(({ gameSrc, scheme }) => {
        const GAME_TEXT_SRC = new RegExp(gameSrc, 'i');
        const a = document.querySelector('article.markdown-body');
        const imgs = [...a.querySelectorAll('img')];
        const hero = imgs[0];
        // smallest real-text font size (skip code inside <kbd>, sub notes are allowed at 12)
        let minText = 99, minWhere = '';
        const walker = document.createTreeWalker(a, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const n = walker.currentNode;
          if (!n.textContent.trim()) continue;
          const el = n.parentElement;
          if (!el.offsetParent && el.closest('details:not([open])')) continue; // collapsed content
          if (el.closest('details:not([open])') && !el.closest('summary')) continue;
          const fs = parseFloat(getComputedStyle(el).fontSize);
          if (fs < minText) { minText = fs; minWhere = n.textContent.trim().slice(0, 40); }
        }
        const tablesScrolling = [...a.querySelectorAll('table')].filter(t => !t.closest('details:not([open])') && t.scrollWidth > t.clientWidth + 2).length;
        const contentImgs = imgs.filter(i => !i.closest('details:not([open])')).map(i => ({
          src: i.currentSrc || i.src, alt: i.alt, w: i.getBoundingClientRect().width, nat: i.naturalWidth,
          broken: i.complete && i.naturalWidth === 0, hero: i === hero,
        }));
        const headings = [...a.querySelectorAll('h3')].map(h => h.textContent.trim());
        const text = a.textContent; // includes collapsed <details>
        const snakePic = [...a.querySelectorAll('picture')].find(pc => /snake/i.test(pc.querySelector('img').alt));
        const want = snakePic && snakePic.querySelector(`source[media*="${scheme}"]`);
        const snakeOk = !!(snakePic && want && snakePic.querySelector('img').currentSrc === want.srcset.trim());
        const dash = [...a.querySelectorAll('img')].filter(i => /overview-activity|dashboard\/portfolio/.test(i.closest('picture') ? i.closest('picture').innerHTML : i.src))
          .map(i => { const r = i.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, left: r.left, w: r.width, ok: i.complete && i.naturalWidth > 0 }; });
        const gameLinks = [...a.querySelectorAll('a[href]')].map(x => x.href).filter(h => /github\.io\/rolex-esto|\/arcade/i.test(h));
        return {
          dash, snakeOk, snakeSrc: snakePic ? snakePic.querySelector('img').currentSrc.slice(-60) : 'missing',
          gameText: (text.match(GAME_TEXT_SRC) || [''])[0], gameLinks, minText, minWhere, tablesScrolling, contentImgs, headings,
          overflow: document.documentElement.scrollWidth - innerWidth,
        };
      }, { gameSrc: GAME_TEXT.source, scheme });
      check(`${tag} no broken images`, r.contentImgs.every(i => !i.broken), r.contentImgs.filter(i => i.broken).map(i => i.src.split('/').pop()).join(', '));
      check(`${tag} no horizontal page overflow`, r.overflow <= 0, `${r.overflow}px`);
      check(`${tag} no sideways-scrolling tables`, r.tablesScrolling === 0, `${r.tablesScrolling}`);
      check(`${tag} <picture> serves ${scheme} asset`, r.snakeOk, r.snakeSrc);
      check(`${tag} real text >= 12px`, r.minText >= 12, `${r.minText}px "${r.minWhere}"`);
      check(`${tag} all project headings visible`, PROJECTS.every(n => r.headings.some(h => h.includes(n))));
      // Developer Overview: both panels load; side by side on desktop, stacked full width on phones.
      const [L, R] = r.dash;
      check(`${tag} overview panels load`, r.dash.length === 2 && r.dash.every(d => d.ok), JSON.stringify(r.dash.map(d => d.ok)));
      if (L && R) check(`${tag} overview ${w >= 1000 ? 'side by side' : 'stacked'}`,
        w >= 1000 ? Math.abs(L.top - R.top) < 2 && R.left > L.left : R.top >= L.bottom - 2, `L ${L.left|0},${L.top|0} R ${R.left|0},${R.top|0} w ${R.w|0}`);
      check(`${tag} no game branding in text`, !r.gameText, r.gameText);
      check(`${tag} no arcade / Pages game links`, r.gameLinks.length === 0, r.gameLinks.join(', '));
      // Rule 4: text inside SVG content images
      let worst = { px: 99, img: '' };
      for (const img of r.contentImgs) {
        if (img.hero || !/\.svg(\?|$)/.test(img.src) || !img.nat) continue;
        if (!svgCache.has(img.src)) {
          const local = OVERVIEW_DIR && img.src.match(OVERVIEW_RE);
          if (local) svgCache.set(img.src, fs.readFileSync(path.join(OVERVIEW_DIR, local[1]), 'utf8'));
          else {
            const res = await ctx.request.get(img.src).catch(() => null);
            svgCache.set(img.src, res && res.ok() ? await res.text() : '');
          }
        }
        const svg = svgCache.get(img.src);
        const vb = svg.match(/viewBox="0 0 ([\d.]+) [\d.]+"/);
        const sizes = [...svg.matchAll(/<text[^>]*font-size="([\d.]+)"/g)].map(m => +m[1]);
        if (!vb || !sizes.length) continue;
        const px = Math.min(...sizes) * img.w / +vb[1];
        if (px < worst.px) worst = { px, img: img.src.split('/').pop() };
      }
      check(`${tag} text inside content images >= ${MIN_IMG_TEXT[w]}px`, worst.px >= MIN_IMG_TEXT[w], `${worst.px.toFixed(1)}px in ${worst.img}`);
      if (SHOTS) await p.locator('article.markdown-body').screenshot({ path: `${SHOTS}/readme-${scheme}-${w}.png` }).catch(() => {});
      await ctx.close();
    }
  }
  await b.close();
  console.log(results.join('\n'));
  console.log(`\n[${process.env.BROWSER || 'chromium'}] ${results.length - fails}/${results.length} passed  (${URL})`);
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
