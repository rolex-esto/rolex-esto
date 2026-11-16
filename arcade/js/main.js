import { Game, GAME_ACHIEVEMENTS } from './game.js';
import { LEVELS } from './levels.js';
import { PROJECTS } from './data.js';
import { SKINS, skinPreview } from './sprites.js';
import { Audio8 } from './audio.js';
import { Terminal } from './terminal.js';
import { loadSave, writeSave, resetSave, addUnique } from './storage.js';

const $ = id => document.getElementById(id);
const save = loadSave();
const mqMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const mqTouch = window.matchMedia('(hover: none) and (pointer: coarse)');
const reduced = () => (save.settings.reducedMotion ?? mqMotion.matches);
const persist = () => writeSave(save);

const audio = new Audio8(save.settings.muted);
const stage = $('stage');
const overlays = ['ov-title', 'ov-pause', 'ov-clear', 'ov-over', 'ov-victory', 'ov-bonus'];

// ---------- feedback ----------
let toastTimer = 0;
function toast(text) {
  const t = $('toast');
  t.textContent = text;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, 3200);
}

function announce(text) { $('status').textContent = text; }

let bannerTimer = 0;
function banner(text) {
  const b = $('banner');
  b.textContent = text;
  b.hidden = false;
  clearTimeout(bannerTimer);
  bannerTimer = setTimeout(() => { b.hidden = true; }, 2200);
}

function unlockAchievement(id) {
  if (!GAME_ACHIEVEMENTS[id]) return;
  if (addUnique(save.achievements, id)) {
    persist();
    audio.play('secret');
    toast(`★ BADGE: ${GAME_ACHIEVEMENTS[id].name}`);
    if (id === 'cheat' && addUnique(save.skins, 'glitch')) { persist(); renderSkins(); }
    renderRecords();
  }
}

// ---------- overlays ----------
function show(id, focusId) {
  overlays.forEach(o => { $(o).hidden = o !== id; });
  stage.classList.toggle('menu-open', !!id);
  if (id) {
    const target = focusId ? $(focusId) : $(id).querySelector('button:not([hidden])');
    // Only move focus if the player is not typing in the terminal.
    if (target && document.activeElement !== $('term-input')) target.focus({ preventScroll: true });
  }
}

// ---------- unlock cards ----------
function projectCard(container, projectId, heading) {
  const p = PROJECTS.find(x => x.id === projectId);
  container.replaceChildren();
  if (!p) return;
  const h = document.createElement('h4');
  h.textContent = `${heading}: ${p.name}`;
  const s = document.createElement('p'); s.textContent = p.summary;
  const m = document.createElement('p'); m.className = 'small'; m.textContent = `${p.role} · ${p.status}`;
  const links = document.createElement('p'); links.className = 'links';
  p.links.forEach(l => {
    const a = document.createElement('a');
    a.href = l.url; a.textContent = `${l.label} ↗`; a.target = '_blank'; a.rel = 'noopener noreferrer';
    links.append(a);
  });
  container.append(h, s, m);
  if (p.links.length) container.append(links);
}

// ---------- quest log ----------
function renderQuests() {
  const wrap = $('quest-cards');
  wrap.replaceChildren();
  PROJECTS.forEach(p => {
    const cleared = save.unlockedProjects.includes(p.id);
    const level = LEVELS.findIndex(l => l.project === p.id);
    const card = document.createElement('article');
    card.className = 'card' + (cleared ? ' cleared' : '');
    const world = document.createElement('p'); world.className = 'world';
    world.textContent = level >= 0 ? `WORLD ${level + 1} · ${p.world.toUpperCase()}` : p.id === 'ulanba' ? `BONUS · ${p.world.toUpperCase()}` : `SIDE QUEST · ${p.world.toUpperCase()}`;
    const h = document.createElement('h3'); h.textContent = p.name;
    const meta = document.createElement('p'); meta.className = 'meta'; meta.textContent = p.status;
    const role = document.createElement('p'); role.className = 'small'; role.textContent = p.role;
    const sum = document.createElement('p'); sum.textContent = p.summary;
    const tags = document.createElement('ul'); tags.className = 'tags'; tags.setAttribute('aria-label', 'Highlights and stack');
    p.stack.forEach(t => { const li = document.createElement('li'); li.textContent = t; tags.append(li); });
    const links = document.createElement('p'); links.className = 'links';
    p.links.forEach(l => { const a = document.createElement('a'); a.href = l.url; a.textContent = `${l.label} ↗`; a.target = '_blank'; a.rel = 'noopener noreferrer'; links.append(a); });
    if (!p.links.length) { const span = document.createElement('span'); span.className = 'small'; span.textContent = 'No public link'; links.append(span); }
    const stamp = document.createElement('p'); stamp.className = 'stamp';
    const playable = level >= 0 || p.id === 'ulanba';
    stamp.textContent = cleared ? '★ CLEARED IN GAME' : playable ? '○ NOT YET CLEARED IN GAME' : '○ NOT A GAME LEVEL';
    card.append(world, h, meta, role, sum, tags, links, stamp);
    wrap.append(card);
  });
}

// ---------- records ----------
const HIDDEN = new Set(['duck', 'cheat', 'coffee', 'sudo']);
function renderRecords() {
  $('rec-best').textContent = save.best.toLocaleString('en-US');
  $('hud-best').textContent = save.best.toLocaleString('en-US');
  $('rec-cleared').textContent = `${LEVELS.filter(l => save.cleared.includes(l.id)).length} / ${LEVELS.length}`;
  $('rec-badges').textContent = `${save.achievements.length} / ${Object.keys(GAME_ACHIEVEMENTS).length}`;
  const list = $('badge-list');
  list.replaceChildren();
  Object.entries(GAME_ACHIEVEMENTS).forEach(([id, a]) => {
    const got = save.achievements.includes(id);
    const li = document.createElement('li');
    li.className = got ? 'got' : '';
    const b = document.createElement('b');
    b.textContent = got || !HIDDEN.has(id) ? a.name : '??? HIDDEN BADGE';
    li.append(b, document.createTextNode(got || !HIDDEN.has(id) ? a.desc : 'Keep exploring. The terminal and the dungeon hide things.'));
    list.append(li);
  });
  const cont = $('btn-continue');
  const resumeAt = Math.min(save.highestLevel, LEVELS.length - 1);
  cont.hidden = resumeAt <= 0;
  cont.textContent = `⟳ CONTINUE: WORLD ${resumeAt + 1}`;
  $('btn-bonus').hidden = !save.cleared.includes(LEVELS[LEVELS.length - 1].id);
}

// ---------- skins ----------
function renderSkins() {
  const list = $('skin-list');
  list.replaceChildren();
  list.setAttribute('role', 'radiogroup');
  list.setAttribute('aria-label', 'Developer skin');
  Object.entries(SKINS).forEach(([id, s]) => {
    if (s.secret && !save.skins.includes(id)) return;
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'skin';
    b.setAttribute('role', 'radio');
    b.setAttribute('aria-checked', String(save.skin === id));
    b.title = s.desc;
    b.append(skinPreview(id), document.createTextNode(s.label));
    b.addEventListener('click', () => {
      save.skin = id; persist();
      game.skin = id;
      audio.unlock(); audio.play('select');
      list.querySelectorAll('.skin').forEach(x => x.setAttribute('aria-checked', String(x === b)));
    });
    list.append(b);
  });
}

// ---------- HUD ----------
function onHud(h) {
  $('hud-level').textContent = h.level;
  $('hud-hp').textContent = '♥'.repeat(h.hp) + '♡'.repeat(Math.max(0, h.maxHp - h.hp));
  $('hud-hp').setAttribute('aria-label', `${h.hp} of ${h.maxHp} health`);
  $('hud-tokens').textContent = `${h.tokens}/${h.total}`;
  $('hud-score').textContent = h.score.toLocaleString('en-US');
  $('hud-credits').textContent = h.level === 'BONUS' ? '–' : String(h.credits);
  const power = [];
  if (h.shield) power.push(`◈ SHIELD ${h.shield}s`);
  if (h.speed) power.push(`⚡ BOOST ${h.speed}s`);
  if (h.time !== null) power.push(`⏱ ${h.time}s`);
  if (h.portalOpen) power.push('▣ PORTAL OPEN');
  $('hud-power').hidden = !power.length;
  $('hud-power').textContent = power.join('  ');
}

function onScore(score) {
  if (score > save.best) { save.best = score; persist(); renderRecords(); }
}

// ---------- game events ----------
function onEvent(type, d) {
  if (type === 'level') {
    show(null);
    $('objective').textContent = `${d.bonus ? 'BONUS' : `WORLD ${d.num}`} · ${d.goal}`;
    banner(d.bonus ? d.name : `WORLD ${d.num}: ${d.name}`);
    if (!d.bonus && d.num - 1 > save.highestLevel) { save.highestLevel = d.num - 1; persist(); renderRecords(); }
  }
  if (type === 'pause') show('ov-pause');
  if (type === 'resume') show(null);
  if (type === 'levelclear' || type === 'victory') {
    addUnique(save.cleared, d.levelId);
    addUnique(save.unlockedProjects, d.project);
    save.highestLevel = Math.max(save.highestLevel, Math.min(d.index + 1, LEVELS.length - 1));
    persist(); renderQuests(); renderRecords();
    const line = `CLEAR +${d.bonuses.clear} · TIME +${d.bonuses.time} · NO-HIT +${d.bonuses.noHit} · XP ${d.score.toLocaleString('en-US')}`;
    if (type === 'levelclear') {
      $('clear-score').textContent = line;
      projectCard($('clear-card'), d.project, 'PROJECT UNLOCKED');
      show('ov-clear', 'btn-next');
    } else {
      $('victory-score').textContent = `${line} · BEST ${save.best.toLocaleString('en-US')}`;
      projectCard($('victory-card'), d.project, 'FINAL PROJECT UNLOCKED');
      show('ov-victory', 'btn-victory-bonus');
    }
  }
  if (type === 'gameover') {
    $('over-score').textContent = `XP ${d.score.toLocaleString('en-US')} · CREDITS LEFT ${d.credits}`;
    const cont = $('btn-cont');
    cont.hidden = !d.canContinue;
    cont.textContent = d.checkpoint ? '⟳ CONTINUE FROM CHECKPOINT' : '⟳ CONTINUE THIS WORLD';
    show('ov-over');
  }
  if (type === 'bonusend') {
    $('ov-bonus-h').textContent = d.won ? 'OBSERVATORY CLEAR!' : 'TIME!';
    $('bonus-score').textContent = `RAINDROPS ${d.caught}/${d.total} · XP ${d.score.toLocaleString('en-US')}`;
    if (d.won) { addUnique(save.unlockedProjects, d.project); persist(); renderQuests(); }
    projectCard($('bonus-card'), d.project, d.won ? 'BONUS PROJECT UNLOCKED' : 'BONUS PROJECT');
    show('ov-bonus', 'btn-bonus-retry');
  }
}

// ---------- game ----------
const game = new Game($('world'), {
  skin: save.skin, reducedMotion: reduced(), assist: save.settings.assist, audio,
  hooks: { onHud, onEvent, onScore, announce, unlock: unlockAchievement },
});

function startRun(level = 0) { audio.unlock(); game.newRun(level); }

$('btn-start').addEventListener('click', () => startRun(0));
$('btn-continue').addEventListener('click', () => startRun(Math.min(save.highestLevel, LEVELS.length - 1)));
$('btn-bonus').addEventListener('click', () => { audio.unlock(); game.startBonus(); });
$('btn-resume').addEventListener('click', () => game.resume());
$('btn-restart').addEventListener('click', () => game.restartLevel());
$('btn-quit').addEventListener('click', () => toTitle());
$('btn-next').addEventListener('click', () => game.nextLevel());
$('btn-cont').addEventListener('click', () => game.continueFromCheckpoint());
$('btn-retry').addEventListener('click', () => startRun(0));
$('btn-over-title').addEventListener('click', () => toTitle());
$('btn-victory-bonus').addEventListener('click', () => game.startBonus());
$('btn-victory-title').addEventListener('click', () => toTitle());
$('btn-bonus-retry').addEventListener('click', () => game.startBonus());
$('btn-bonus-title').addEventListener('click', () => toTitle());

function toTitle() {
  game.toTitle();
  $('objective').textContent = 'Choose a skin and press START to begin.';
  renderRecords();
  show('ov-title');
}

// ---------- settings ----------
function syncSettings() {
  const s = $('btn-sound'), m = $('btn-motion'), a = $('btn-assist'), t = $('btn-touch');
  s.setAttribute('aria-pressed', String(!audio.muted)); s.textContent = `♪ Sound: ${audio.muted ? 'off' : 'on'}`;
  m.setAttribute('aria-pressed', String(reduced())); m.textContent = `◐ Reduced motion: ${reduced() ? 'on' : 'off'}`;
  a.setAttribute('aria-pressed', String(save.settings.assist)); a.textContent = `✚ Assist mode: ${save.settings.assist ? 'on' : 'off'}`;
  t.setAttribute('aria-pressed', String(touchOn)); t.textContent = `✥ Touch pad: ${touchOn ? 'on' : 'off'}`;
  $('touchpad').classList.toggle('on', touchOn);
}
function toggleSound() {
  audio.setMuted(!audio.muted);
  save.settings.muted = audio.muted; persist(); syncSettings();
  announce(audio.muted ? 'Sound off.' : 'Sound on.');
}
let touchOn = mqTouch.matches;
$('btn-sound').addEventListener('click', toggleSound);
$('btn-motion').addEventListener('click', () => {
  save.settings.reducedMotion = !reduced(); persist();
  game.reducedMotion = reduced(); syncSettings();
});
$('btn-assist').addEventListener('click', () => {
  save.settings.assist = !save.settings.assist; persist();
  game.assist = save.settings.assist; syncSettings();
  announce(`Assist mode ${save.settings.assist ? 'on' : 'off'}. Enemy speed changes from the next world you start.`);
});
$('btn-touch').addEventListener('click', () => { touchOn = !touchOn; syncSettings(); });
mqMotion.addEventListener?.('change', () => { game.reducedMotion = reduced(); syncSettings(); });

$('btn-reset').addEventListener('click', () => {
  if (!window.confirm('Reset best score, cleared worlds and badges saved in this browser?')) return;
  Object.assign(save, resetSave());
  game.skin = save.skin;
  renderSkins(); renderQuests(); renderRecords(); syncSettings();
  announce('Game progress reset.');
});

// ---------- input ----------
const KEYMAP = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', w: 'up', s: 'down', a: 'left', d: 'right', W: 'up', S: 'down', A: 'left', D: 'right' };
const KONAMI = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
let konami = 0;
const typing = el => el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);

window.addEventListener('keydown', e => {
  if (typing(e.target) || e.metaKey || e.ctrlKey || e.altKey) return;
  // Konami code on the title screen unlocks a secret skin.
  if (game.state === 'title') {
    const want = KONAMI[konami];
    konami = (e.key === want || e.key.toLowerCase() === want) ? konami + 1 : (e.key === KONAMI[0] ? 1 : 0);
    if (konami === KONAMI.length) { konami = 0; unlockAchievement('cheat'); announce('Secret skin unlocked: GLITCH.'); }
  }
  const onButton = e.target && e.target.tagName === 'BUTTON';
  const dir = KEYMAP[e.key];
  if (dir && game.state === 'playing') { e.preventDefault(); game.input[dir] = true; return; }
  if ((e.key === 'p' || e.key === 'P' || e.key === 'Escape' || (e.key === ' ' && !onButton)) && (game.state === 'playing' || game.state === 'paused')) {
    e.preventDefault(); game.togglePause(); return;
  }
  if ((e.key === 'r' || e.key === 'R') && game.state === 'paused') { game.restartLevel(); return; }
  if (e.key === 'm' || e.key === 'M') toggleSound();
});
window.addEventListener('keyup', e => { const dir = KEYMAP[e.key]; if (dir) game.input[dir] = false; });
window.addEventListener('blur', () => { game.clearInput(); game.pause(); });
document.addEventListener('visibilitychange', () => { if (document.hidden) { game.clearInput(); game.pause(); } });

// Touch / pointer D-pad (press-and-hold)
document.querySelectorAll('.dpad button').forEach(b => {
  const dir = b.dataset.dir;
  const down = e => { e.preventDefault(); audio.unlock(); game.input[dir] = true; b.classList.add('held'); try { b.setPointerCapture(e.pointerId); } catch { /* ignore */ } };
  const up = () => { game.input[dir] = false; b.classList.remove('held'); };
  b.addEventListener('pointerdown', down);
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(n => b.addEventListener(n, up));
  b.addEventListener('contextmenu', e => e.preventDefault());
});
$('pad-pause').addEventListener('click', () => { if (game.state === 'playing' || game.state === 'paused') game.togglePause(); });

window.addEventListener('resize', () => game.resize());
new ResizeObserver(() => game.resize()).observe($('world'));

// ---------- terminal ----------
new Terminal({
  output: $('term-out'), form: $('term-form'), input: $('term-input'),
  actions: {
    play: () => { $('game').scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth' }); startRun(0); $('world').focus?.(); },
    unlock: unlockAchievement,
    bonus: () => {
      const ready = save.cleared.includes(LEVELS[LEVELS.length - 1].id);
      const t = document.createElement('p');
      t.className = ready ? 't-ok' : 't-dim';
      t.textContent = ready ? 'Opening the Rain Observatory…' : 'The observatory is locked. Clear all five worlds first (hint: it rains after the storm).';
      $('term-out').append(t);
      if (ready) { $('game').scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth' }); audio.unlock(); game.startBonus(); }
    },
    reset: () => $('btn-reset').click(),
  },
});

// ---------- boot ----------
renderSkins();
renderQuests();
renderRecords();
syncSettings();
show('ov-title');
// Don't steal focus on first load; keyboard users start from the top of the page.
document.activeElement?.blur?.();
announce('Ready. Choose a skin and press START.');

// QA hook for automated browser tests only (opt-in via ?qa=1).
if (new URLSearchParams(location.search).has('qa')) {
  window.__rolexQA = {
    snapshot: () => game.snapshot(),
    teleport: (x, y) => { game.player.x = x; game.player.y = y; },
    game,
  };
}
document.documentElement.dataset.ready = 'true';
