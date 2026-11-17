// BUG HUNTER regression suite.
// Usage: ARCADE_URL=http://127.0.0.1:8000/arcade/ BROWSER=chromium|webkit|firefox node tests/arcade.qa.cjs
// (needs `playwright` and `@axe-core/playwright`; see tests/README.md)
const pw = require('playwright');
const engine = pw[process.env.BROWSER || 'chromium'];
const { AxeBuilder } = require('@axe-core/playwright');
const S = process.env.SHOTS || require('os').tmpdir();
const URL = (process.env.ARCADE_URL || 'https://rolex-esto.github.io/rolex-esto/arcade/') + '?qa=1';
require('fs').mkdirSync(S + '/shots', { recursive: true });
const IS_FIREFOX = (process.env.BROWSER || 'chromium') === 'firefox';
const results = []; let fails = 0;
const check = (name, ok, info = '') => { results.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${info ? '  — ' + info : ''}`); if (!ok) fails++; };
const snap = p => p.evaluate(() => window.__rolexQA.snapshot());
const wait = ms => new Promise(r => setTimeout(r, ms));
const vis = (p, id) => p.evaluate(i => !document.getElementById(i).hidden, id);

(async () => {
  const b = await engine.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('console', m => { if (['error', 'warning'].includes(m.type())) errs.push(m.text()); });
  p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  p.on('requestfailed', r => errs.push('reqfail: ' + r.url()));
  await p.goto(URL, { timeout: 60000 });
  await p.waitForFunction(() => document.documentElement.dataset.ready === 'true');
  // Regression (UX polish): loading indicator must be gone once the game is ready.
  check('loading indicator hidden after ready', await p.evaluate(() => document.getElementById('loading').hidden === true));

  // Init
  let s = await snap(p);
  check('initial state is title', s.state === 'title');
  check('title overlay visible', await vis(p, 'ov-title'));
  check('nothing focused on load', await p.evaluate(() => document.activeElement === document.body));
  check('quest log lists 8 projects without playing', (await p.locator('#quest-cards .card').count()) === 8);

  // Konami on title
  for (const k of ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a']) await p.keyboard.press(k);
  check('konami unlocks secret skin', (await p.locator('.skin').count()) === 4);

  // Start
  await p.click('#btn-start');
  s = await snap(p);
  check('start → playing L1', s.state === 'playing' && s.level === 'merchant' && s.hp === 3, JSON.stringify({ state: s.state, level: s.level }));
  check('overlay hidden while playing', !(await vis(p, 'ov-title')));
  check('HUD tokens shows 0/12', (await p.textContent('#hud-tokens')) === '0/12');

  // Movement
  const x0 = s.player.x;
  await p.keyboard.down('ArrowRight'); await wait(400); await p.keyboard.up('ArrowRight');
  s = await snap(p); check('arrow key moves player right', s.player.x > x0 + 10, `${x0.toFixed(1)} → ${s.player.x.toFixed(1)}`);
  const y0 = s.player.y;
  await p.keyboard.down('w'); await wait(600); await p.keyboard.up('w');
  s = await snap(p); check('wall blocks movement (W into top wall)', s.player.y >= 16 + 5 && s.player.y <= y0, `y ${y0.toFixed(1)} → ${s.player.y.toFixed(1)}`);
  await p.keyboard.down('s'); await wait(300); await p.keyboard.up('s');
  s = await snap(p); check('WASD moves player down', s.player.y > y0, `y → ${s.player.y.toFixed(1)}`);

  // Token pickup
  const tok = await p.evaluate(() => { const t = window.__rolexQA.game.level.tokens[0]; return { x: t.x, y: t.y }; });
  const before = await snap(p);
  await p.evaluate(t => window.__rolexQA.teleport(t.x, t.y), tok); await wait(80);
  s = await snap(p);
  check('token collected → count & score', s.tokensLeft === before.tokensLeft - 1 && s.score === before.score + 100, `left ${s.tokensLeft}, xp ${s.score}`);
  check('HUD updates tokens', (await p.textContent('#hud-tokens')) === '1/12');

  // Enemy collision (wait out spawn invulnerability)
  await wait(1100);
  const hpBefore = (await snap(p)).hp;
  await p.evaluate(() => { const g = window.__rolexQA.game; g.invuln = 0; const e = g.level.enemies[0]; window.__rolexQA.teleport(e.x, e.y); });
  await wait(80);
  s = await snap(p); check('enemy collision costs 1 HP', s.hp === hpBefore - 1, `hp ${hpBefore} → ${s.hp}`);
  check('invulnerability after hit', s.invuln > 0.5);

  // Pause
  await p.keyboard.press('p');
  s = await snap(p); check('P pauses', s.state === 'paused' && await vis(p, 'ov-pause'));
  const frozen = s.player.x; await wait(200);
  check('game frozen while paused', (await snap(p)).player.x === frozen);
  await p.keyboard.press('Escape');
  s = await snap(p); check('Esc resumes', s.state === 'playing' && !(await vis(p, 'ov-pause')));

  // Checkpoint
  await p.evaluate(() => { const c = window.__rolexQA.game.level.checkpointPos; window.__rolexQA.teleport(c.x, c.y); });
  await wait(80);
  check('checkpoint activates', (await snap(p)).checkpoint);

  // Portal locked until tokens collected
  await p.evaluate(() => { const g = window.__rolexQA.game; g.invuln = 99; const q = g.level.portal; window.__rolexQA.teleport(q.x, q.y); });
  await wait(80);
  check('portal locked with tokens left', (await snap(p)).state === 'playing');

  // Power-ups
  await p.evaluate(() => { const g = window.__rolexQA.game; g.hp = 1; const h = g.level.items.find(i => i.kind === 'heal'); window.__rolexQA.teleport(h.x, h.y); });
  await wait(80);
  check('heal power-up restores HP', (await snap(p)).hp === 2);

  // Collect all tokens + reach portal → level clear
  async function clearLevel() {
    await p.evaluate(async () => {
      const g = window.__rolexQA.game; g.invuln = 99;
      for (const t of g.level.tokens) { if (!t.taken) { window.__rolexQA.teleport(t.x, t.y); await new Promise(r => setTimeout(r, 40)); } }
      const q = g.level.portal; window.__rolexQA.teleport(q.x, q.y);
    });
    await wait(120);
  }
  await clearLevel();
  s = await snap(p);
  check('level 1 clear state + overlay', s.state === 'levelclear' && await vis(p, 'ov-clear'));
  check('unlock card shows BizPilot', (await p.textContent('#clear-card')).includes('BizPilot'));
  check('quest card stamped cleared', (await p.locator('#quest-cards .card.cleared').count()) === 1);
  check('focus moved to NEXT button', await p.evaluate(() => document.activeElement.id === 'btn-next'));
  await p.screenshot({ path: S + '/shots/02-level-clear.png' });

  await p.keyboard.press('Enter');
  s = await snap(p); check('NEXT → level 2 Energy Realm', s.level === 'energy' && s.state === 'playing');
  await wait(300); await p.screenshot({ path: S + '/shots/03-energy.png' });

  // Speed power-up
  await p.evaluate(() => { const g = window.__rolexQA.game; const f = g.level.items.find(i => i.kind === 'speed'); window.__rolexQA.teleport(f.x, f.y); });
  await wait(80); check('speed power-up active', (await snap(p)).speedBoost > 5);
  await p.evaluate(() => { const g = window.__rolexQA.game; const f = g.level.items.find(i => i.kind === 'shield'); window.__rolexQA.teleport(f.x, f.y); });
  await wait(80); check('shield power-up active', (await snap(p)).shield > 5);
  await p.evaluate(() => { const g = window.__rolexQA.game; g.invuln = 0; const hp = g.hp; const e = g.level.enemies[0]; window.__rolexQA.teleport(e.x, e.y); window.__hp = hp; });
  await wait(80); check('shield blocks damage', await p.evaluate(() => window.__rolexQA.snapshot().hp === window.__hp));
  await p.evaluate(() => { const g = window.__rolexQA.game; g.shield = 0; window.__rolexQA.teleport(g.level.start.x, g.level.start.y); });

  // Game over + continue
  await p.evaluate(() => { const g = window.__rolexQA.game; g.hp = 1; g.invuln = 0; const e = g.level.enemies[0]; window.__rolexQA.teleport(e.x, e.y); });
  await wait(100);
  s = await snap(p); check('HP 0 → game over overlay', s.state === 'gameover' && await vis(p, 'ov-over'));
  await p.screenshot({ path: S + '/shots/04-gameover.png' });
  await p.click('#btn-cont');
  s = await snap(p); check('continue uses a credit and resumes same world', s.state === 'playing' && s.credits === 1 && s.level === 'energy' && s.hp === 3);

  // Clear remaining levels 2..5
  for (const id of ['energy', 'incident', 'flood', 'weather']) {
    if (id === 'incident') {
      await wait(200); await p.screenshot({ path: S + '/shots/05-incident-dark.png' });
      await p.evaluate(() => { const g = window.__rolexQA.game; window.__rolexQA.teleport(g.level.duck.x, g.level.duck.y); });
      await wait(100);
      check('rubber duck secret found', await p.evaluate(() => window.__rolexQA.game.level.duck.found));
    }
    if (id === 'flood') {
      const sp = await p.evaluate(async () => {
        const g = window.__rolexQA.game; g.invuln = 99;
        // find a water tile and measure speed vs dry
        const wi = g.level.water.findIndex(Boolean); const wx = (wi % 32) * 16 + 8, wy = Math.floor(wi / 32) * 16 + 8;
        window.__rolexQA.teleport(wx, wy); g.input.down = true; await new Promise(r => setTimeout(r, 250)); g.input.down = false;
        return g.player.y - wy;
      });
      check('flood water slows movement', sp > 0 && sp < 74 * 0.25 * 0.75, `moved ${sp.toFixed(1)}px in 250ms`);
      await wait(100); await p.screenshot({ path: S + '/shots/06-flood.png' });
    }
    if (id === 'weather') {
      const dx = await p.evaluate(async () => {
        const g = window.__rolexQA.game; g.invuln = 99;
        const wi = g.level.wind.findIndex(v => v === -1) + 10; const wx = (wi % 32) * 16 + 8, wy = Math.floor(wi / 32) * 16 + 8;
        window.__rolexQA.teleport(wx, wy); await new Promise(r => setTimeout(r, 300)); return g.player.x - wx;
      });
      check('wind lane pushes player', dx < -5, `dx ${dx.toFixed(1)}`);
    }
    await clearLevel();
    s = await snap(p);
    if (id !== 'weather') { check(`${id} cleared`, s.state === 'levelclear'); await p.click('#btn-next'); }
  }
  s = await snap(p);
  check('final world → victory overlay', s.state === 'victory' && await vis(p, 'ov-victory'));
  await p.screenshot({ path: S + '/shots/07-victory.png' });

  // Bonus stage: time attack, time-out path
  await p.click('#btn-victory-bonus');
  s = await snap(p); check('bonus stage starts with timer', s.level === 'observatory' && s.timeLeft > 80);
  await p.evaluate(() => { window.__rolexQA.game.timeLeft = 0.05; });
  await wait(150);
  check('bonus time-out → result overlay', (await snap(p)).state === 'bonusend' && await vis(p, 'ov-bonus'));
  await p.click('#btn-bonus-retry');
  await clearLevel();
  check('bonus win', (await p.textContent('#ov-bonus-h')).includes('CLEAR'));

  // Records / persistence
  const best = await p.evaluate(() => JSON.parse(localStorage.getItem('rolex-exe:save:v1')).best);
  check('best score saved to localStorage', best > 0, `best ${best}`);
  await p.reload(); await p.waitForFunction(() => document.documentElement.dataset.ready === 'true');
  check('best score persists after reload', (await p.textContent('#rec-best')) === best.toLocaleString('en-US'));
  check('continue + bonus buttons available after progress', await vis(p, 'btn-continue') && await vis(p, 'btn-bonus'));
  check('all 6 playable worlds stamped', (await p.locator('#quest-cards .card.cleared').count()) === 6);

  // Terminal
  await p.fill('#term-input', 'help'); await p.press('#term-input', 'Enter');
  check('terminal help', (await p.textContent('#term-out')).includes('achievements'));
  await p.fill('#term-input', 'projects'); await p.press('#term-input', 'Enter');
  const tout = await p.textContent('#term-out');
  check('terminal projects lists real projects', ['BizPilot', 'SmartWatts', 'OpsPilot', 'BahaRoute', 'Weather Weather Lang'].every(n => tout.includes(n)));
  await p.fill('#term-input', '<img src=x onerror=alert(1)>'); await p.press('#term-input', 'Enter');
  check('terminal escapes HTML input', (await p.locator('#term-out img').count()) === 0);
  await p.fill('#term-input', 'sudo'); await p.press('#term-input', 'Enter');
  await p.fill('#term-input', 'coffee'); await p.press('#term-input', 'Enter');
  check('hidden terminal badges unlock', await p.evaluate(() => { const a = JSON.parse(localStorage.getItem('rolex-exe:save:v1')).achievements; return a.includes('sudo') && a.includes('coffee'); }));
  await p.fill('#term-input', 'w'); await p.keyboard.press('ArrowRight');
  check('typing in terminal does not move game', (await snap(p)).state === 'title');
  await p.fill('#term-input', 'clear'); await p.press('#term-input', 'Enter');
  check('terminal clear', (await p.locator('#term-out p').count()) === 0);
  await p.fill('#term-input', 'play'); await p.press('#term-input', 'Enter');
  check('terminal play starts game', (await snap(p)).state === 'playing');

  // Settings
  await p.click('#btn-sound');
  check('sound toggle persists muted', await p.evaluate(() => JSON.parse(localStorage.getItem('rolex-exe:save:v1')).settings.muted === true));
  await p.click('#btn-motion');
  check('reduced-motion toggle applies to game', await p.evaluate(() => window.__rolexQA.game.reducedMotion === true));
  await p.screenshot({ path: S + '/shots/08-terminal.png', fullPage: true });

  // Accessibility scan (title state)
  await p.evaluate(() => window.__rolexQA.game.pause()); await p.click('#btn-quit');
  const axe = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
  check('axe: no WCAG A/AA violations', axe.violations.length === 0, axe.violations.map(v => `${v.id}(${v.nodes.length})`).join(', '));
  check('no console errors/failed requests', errs.length === 0, errs.join(' | '));
  await ctx.close();

  // Regression (UX polish): if the game script never loads, show the loading
  // message and no dead controls (START must not be clickable/visible).
  const bctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const bp = await bctx.newPage();
  await bp.route('**/js/main.js', r => r.abort());
  await bp.goto(URL, { timeout: 60000 }); await bp.waitForTimeout(800);
  check('script failure: loading message visible', await bp.isVisible('#loading'));
  check('script failure: no dead START button', !(await bp.isVisible('#btn-start')));
  await bctx.close();

  // Reduced-motion media query default
  const rm = await b.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
  const rp = await rm.newPage(); await rp.goto(URL, { timeout: 60000 }); await rp.waitForFunction(() => document.documentElement.dataset.ready === 'true');
  check('prefers-reduced-motion respected by default', await rp.evaluate(() => window.__rolexQA.game.reducedMotion === true && document.getElementById('btn-motion').getAttribute('aria-pressed') === 'true'));
  await rm.close();

  // Mobile
  for (const [name, vp] of [['mobile-portrait', { width: 390, height: 844 }], ['mobile-landscape', { width: 844, height: 390 }], ['tablet', { width: 820, height: 1180 }]]) {
    const m = await b.newContext({ viewport: vp, hasTouch: true, isMobile: !IS_FIREFOX && name !== 'tablet', deviceScaleFactor: 2 });
    const mp = await m.newPage(); const merr = [];
    mp.on('pageerror', e => merr.push(e.message));
    try { await mp.goto(URL, { timeout: 25000 }); } catch { results.push(`RETRY ${name}: first navigation timed out`); await mp.goto(URL, { timeout: 60000 }); } await mp.waitForFunction(() => document.documentElement.dataset.ready === 'true');
    await mp.screenshot({ path: `${S}/shots/09-${name}-title.png` });
    const overflow = await mp.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    check(`${name}: no horizontal overflow`, overflow <= 0, `overflow ${overflow}px`);
    await mp.tap('#btn-start');
    const pad = await mp.evaluate(() => getComputedStyle(document.getElementById('touchpad')).display !== 'none');
    check(`${name}: touch pad shown on touch device`, pad);
    const sx = (await mp.evaluate(() => window.__rolexQA.snapshot())).player.x;
    const box = await mp.locator('[data-dir="right"]').boundingBox();
    await mp.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2); // tap = brief
    await mp.dispatchEvent('[data-dir="right"]', 'pointerdown', { pointerId: 1 });
    await wait(400);
    await mp.dispatchEvent('[data-dir="right"]', 'pointerup', { pointerId: 1 });
    const ex = (await mp.evaluate(() => window.__rolexQA.snapshot())).player.x;
    check(`${name}: D-pad hold moves player`, ex > sx + 10, `${sx.toFixed(1)} → ${ex.toFixed(1)}`);
    await mp.screenshot({ path: `${S}/shots/10-${name}-play.png` });
    check(`${name}: no page errors`, merr.length === 0, merr.join('|'));
    await m.close();
  }
  await b.close();
  console.log(results.join('\n'));
  const total = results.filter(r => !r.startsWith('RETRY')).length;
  console.log(`\n[${process.env.BROWSER || 'chromium'}] ${total - fails}/${total} passed`);
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
