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
//  2. <picture> serves the asset matching the colour scheme.
//  3. Real text in the README is >= 12 px at every tested width.
//  4. Any content image that contains SVG <text> renders that text >= MIN_IMG_TEXT px,
//     except the hero (decorative; its information is repeated as Markdown text).
//  5. Every featured project has a visible text heading, Problem line and links.
const pw = require('playwright');
const engine = pw[process.env.BROWSER || 'chromium'];
const URL = process.env.README_URL || 'https://github.com/rolex-esto/rolex-esto';
const SHOTS = process.env.SHOTS || '';
const WIDTHS = [320, 375, 390, 430, 1280];
const MIN_IMG_TEXT = { 320: 8, 375: 9, 390: 9.5, 430: 10, 1280: 11 };
const PROJECTS = ['BizPilot', 'SmartWatts', 'OpsPilot', 'BahaRoute', 'Weather Weather Lang', 'Ulan Ba?'];

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
      await p.goto(URL, { waitUntil: 'load', timeout: 90000 });
      await p.waitForSelector('article.markdown-body', { timeout: 30000 });
      await p.evaluate(async () => { // load lazy images
        for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
        window.scrollTo(0, 0);
      });
      await p.waitForTimeout(1500);
      const tag = `[${scheme} ${w}]`;
      const r = await p.evaluate(() => {
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
        const text = a.innerText;
        return {
          heroSrc: (hero.currentSrc || hero.src).split('/').pop(), minText, minWhere, tablesScrolling, contentImgs, headings,
          overflow: document.documentElement.scrollWidth - innerWidth,
          problems: (text.match(/Problem:/g) || []).length,
        };
      });
      check(`${tag} no broken images`, r.contentImgs.every(i => !i.broken), r.contentImgs.filter(i => i.broken).map(i => i.src.split('/').pop()).join(', '));
      check(`${tag} no horizontal page overflow`, r.overflow <= 0, `${r.overflow}px`);
      check(`${tag} no sideways-scrolling tables`, r.tablesScrolling === 0, `${r.tablesScrolling}`);
      check(`${tag} hero matches theme`, r.heroSrc === `hero-${scheme}.svg`, r.heroSrc);
      check(`${tag} real text >= 12px`, r.minText >= 12, `${r.minText}px "${r.minWhere}"`);
      check(`${tag} all project headings visible`, PROJECTS.every(n => r.headings.some(h => h.includes(n))));
      check(`${tag} every project states its problem`, r.problems >= PROJECTS.length, `${r.problems}`);
      // Rule 4: text inside SVG content images
      let worst = { px: 99, img: '' };
      for (const img of r.contentImgs) {
        if (img.hero || !/\.svg(\?|$)/.test(img.src) || !img.nat) continue;
        if (!svgCache.has(img.src)) {
          const res = await ctx.request.get(img.src).catch(() => null);
          svgCache.set(img.src, res && res.ok() ? await res.text() : '');
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
