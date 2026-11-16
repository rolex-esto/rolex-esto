// BUG HUNTER — Developer Quest. Canvas game engine (no dependencies).
import { LEVELS, BONUS_LEVEL, TILE, COLS, ROWS } from './levels.js';
import { playerSprite, enemySprite, itemSprite, tokenSprite } from './sprites.js';

export const VIEW_W = 384;
export const VIEW_H = 216;
const WORLD_W = COLS * TILE;
const WORLD_H = ROWS * TILE;
const STEP = 1 / 60;
const PLAYER_SPEED = 74;
const PLAYER_W = 9;
const PLAYER_H = 10;
const ENEMY_BOX = 8;
const POWER_TIME = 6;
const START_CREDITS = 2;

export const GAME_ACHIEVEMENTS = {
  'first-token': { name: 'HELLO, WORLD', desc: 'Collect your first token.' },
  'no-hit': { name: 'ZERO BUGS SHIPPED', desc: 'Clear a level without taking a hit.' },
  duck: { name: 'RUBBER DUCK DEBUGGING', desc: 'Find the duck hiding in the Incident Dungeon.' },
  cheat: { name: 'CHEAT CODE', desc: 'Enter a classic code on the title screen.' },
  coffee: { name: 'CAFFEINATED', desc: 'Brew something in the terminal.' },
  sudo: { name: 'NICE TRY', desc: 'Ask the terminal for root access.' },
  quest: { name: 'QUEST COMPLETE', desc: 'Clear all five worlds.' },
  bonus: { name: 'OBSERVATORY CLEAR', desc: 'Beat the bonus time attack.' },
};

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

export class Game {
  constructor(canvas, { skin = 'dev', reducedMotion = false, assist = false, audio, hooks = {} }) {
    this.canvas = canvas;
    this.g = canvas.getContext('2d');
    this.audio = audio;
    this.hooks = hooks;
    this.skin = skin;
    this.reducedMotion = reducedMotion;
    this.assist = assist;
    this.input = { up: false, down: false, left: false, right: false };
    this.state = 'title';
    this.run = null;
    this.level = null;
    this.particles = [];
    this.shake = 0;
    this.time = 0;
    this.acc = 0;
    this.last = 0;
    this.lastHud = '';
    this.fog = document.createElement('canvas');
    this.fog.width = VIEW_W; this.fog.height = VIEW_H;
    this.loadLevel(LEVELS[0], 0, true);
    this.resize();
    this.frame = this.frame.bind(this);
    requestAnimationFrame(this.frame);
  }

  // ---------- lifecycle ----------
  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const cssW = rect.width || VIEW_W;
    this.scale = Math.max(1, Math.round((cssW * dpr) / VIEW_W));
    this.canvas.width = VIEW_W * this.scale;
    this.canvas.height = VIEW_H * this.scale;
    this.g.imageSmoothingEnabled = false;
  }

  newRun(levelIndex = 0) {
    this.run = { score: 0, credits: START_CREDITS, index: levelIndex, bonus: false };
    this.startLevel(levelIndex);
  }

  startBonus() {
    this.run = { score: 0, credits: 0, index: -1, bonus: true };
    this.loadLevel(BONUS_LEVEL, -1, false);
    this.beginPlay();
  }

  startLevel(index) {
    this.run.index = index;
    this.loadLevel(LEVELS[index], index, false);
    this.beginPlay();
  }

  beginPlay() {
    const L = this.level;
    this.run.levelStartScore = this.run.score;
    this.hp = this.maxHp;
    this.invuln = 1;
    this.shield = 0;
    this.speedBoost = 0;
    this.hitThisLevel = false;
    this.levelTime = 0;
    this.timeLeft = L.def.timeLimit ? L.def.timeLimit : null;
    this.checkpoint = null;
    this.state = 'playing';
    this.emit('level', { name: L.def.name, goal: L.def.goal, num: L.index + 1, bonus: !!L.def.bonus });
    this.announce(`${L.def.name}. ${L.def.goal}`);
  }

  get maxHp() { return this.assist ? 5 : 3; }

  loadLevel(def, index, demo) {
    const walls = [], water = [], wind = [];
    const tokens = [], items = [], enemies = [];
    let start = { x: 24, y: 24 }, portal = null, checkpoint = null, duck = null;
    const diff = (1 + 0.12 * Math.max(0, index)) * (this.assist ? 0.65 : 1);
    let n = 0;
    def.map.forEach((row, ty) => {
      [...row].forEach((ch, tx) => {
        const cx = tx * TILE + TILE / 2, cy = ty * TILE + TILE / 2;
        const i = ty * COLS + tx;
        walls[i] = ch === '#';
        water[i] = ch === '~';
        wind[i] = ch === '>' ? 1 : ch === '<' ? -1 : 0;
        if (ch === 'P') start = { x: cx, y: cy };
        else if (ch === 'T') tokens.push({ x: cx, y: cy, taken: false });
        else if (ch === 'X') portal = { x: cx, y: cy };
        else if (ch === 'K') checkpoint = { x: cx, y: cy };
        else if (ch === 'D') duck = { x: cx, y: cy, found: false };
        else if (ch === 'H' || ch === 'S' || ch === 'F') items.push({ x: cx, y: cy, kind: { H: 'heal', S: 'shield', F: 'speed' }[ch], taken: false });
        else if ('hvbc'.includes(ch)) {
          const dir = n++ % 2 ? 1 : -1;
          const e = { type: ch, x: cx, y: cy, sx: cx, sy: cy, vx: 0, vy: 0, phase: n * 0.37 };
          if (ch === 'h') e.vx = 40 * dir * diff;
          if (ch === 'v') e.vy = 40 * dir * diff;
          if (ch === 'b') { e.vx = 34 * dir * diff; e.vy = 30 * -dir * diff; }
          if (ch === 'c') e.speed = 30 * diff;
          enemies.push(e);
        }
      });
    });
    this.level = { def, index, walls, water, wind, tokens, items, enemies, start, portal, checkpointPos: checkpoint, duck, demo };
    this.player = { x: start.x, y: start.y, facingLeft: false, moving: false, anim: 0 };
    this.cam = { x: clamp(start.x - VIEW_W / 2, 0, WORLD_W - VIEW_W), y: clamp(start.y - VIEW_H / 2, 0, WORLD_H - VIEW_H) };
    this.particles = [];
    this.tileLayer = this.renderTiles(def);
  }

  // ---------- public controls ----------
  togglePause() {
    if (this.state === 'playing') { this.state = 'paused'; this.clearInput(); this.emit('pause'); this.announce('Paused.'); }
    else if (this.state === 'paused') this.resume();
  }

  pause() { if (this.state === 'playing') this.togglePause(); }

  resume() {
    if (this.state !== 'paused') return;
    this.state = 'playing';
    this.emit('resume');
    this.announce('Resumed.');
  }

  restartLevel() {
    if (!this.run) return;
    this.run.score = this.run.levelStartScore ?? 0;
    if (this.run.bonus) this.startBonus(); else this.startLevel(this.run.index);
  }

  canContinue() { return !!this.run && !this.run.bonus && this.run.credits > 0; }

  continueFromCheckpoint() {
    if (!this.canContinue()) return;
    const cp = this.checkpoint;
    const credits = this.run.credits - 1;
    const levelStartScore = this.run.levelStartScore;
    this.loadLevel(LEVELS[this.run.index], this.run.index, false);
    this.run.credits = credits;
    this.hp = this.maxHp; this.invuln = 1.5; this.shield = 0; this.speedBoost = 0;
    this.levelTime = cp ? cp.time : 0;
    this.timeLeft = null;
    this.run.levelStartScore = levelStartScore;
    if (cp) {
      cp.tokens.forEach((t, i) => { this.level.tokens[i].taken = t; });
      cp.items.forEach((t, i) => { this.level.items[i].taken = t; });
      this.run.score = cp.score;
      this.player.x = cp.x; this.player.y = cp.y;
      this.checkpoint = cp;
    } else {
      this.run.score = levelStartScore;
      this.checkpoint = null;
    }
    this.state = 'playing';
    this.emit('resume');
    this.announce(cp ? 'Continued from checkpoint.' : 'Continued from level start.');
  }

  nextLevel() {
    if (this.state !== 'levelclear') return;
    const next = this.run.index + 1;
    if (next < LEVELS.length) this.startLevel(next);
  }

  toTitle() {
    this.state = 'title';
    this.run = null;
    this.loadLevel(LEVELS[0], 0, true);
  }

  clearInput() { for (const k in this.input) this.input[k] = false; }

  // ---------- helpers ----------
  emit(type, data = {}) { this.hooks.onEvent?.(type, data); }
  announce(text) { this.hooks.announce?.(text); }
  unlock(id) { this.hooks.unlock?.(id); }

  tileAt(px, py) {
    const tx = Math.floor(px / TILE), ty = Math.floor(py / TILE);
    if (tx < 0 || ty < 0 || tx >= COLS || ty >= ROWS) return -1;
    return ty * COLS + tx;
  }

  solid(px, py) {
    const i = this.tileAt(px, py);
    return i < 0 || this.level.walls[i];
  }

  boxHits(x, y, w, h) {
    const hw = w / 2, hh = h / 2;
    return this.solid(x - hw, y - hh) || this.solid(x + hw - 0.01, y - hh) ||
      this.solid(x - hw, y + hh - 0.01) || this.solid(x + hw - 0.01, y + hh - 0.01);
  }

  // Axis-separated movement; returns which axes were blocked.
  moveBox(ent, dx, dy, w, h) {
    let bx = false, by = false;
    if (dx) { if (this.boxHits(ent.x + dx, ent.y, w, h)) bx = true; else ent.x += dx; }
    if (dy) { if (this.boxHits(ent.x, ent.y + dy, w, h)) by = true; else ent.y += dy; }
    return { bx, by };
  }

  burst(x, y, color, count = 10) {
    if (this.reducedMotion) return;
    for (let i = 0; i < count && this.particles.length < 160; i++) {
      const a = (Math.PI * 2 * i) / count + Math.random() * 0.4;
      const s = 30 + Math.random() * 50;
      this.particles.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s, life: 0.45 + Math.random() * 0.3, color });
    }
  }

  // ---------- update ----------
  frame(now) {
    const dt = Math.min(0.1, (now - (this.last || now)) / 1000);
    this.last = now;
    this.acc += dt;
    let steps = 0;
    while (this.acc >= STEP && steps < 6) { this.update(STEP); this.acc -= STEP; steps++; }
    if (steps === 6) this.acc = 0;
    this.draw();
    this.pushHud();
    requestAnimationFrame(this.frame);
  }

  update(dt) {
    this.time += dt;
    if (this.state === 'title') { if (!this.reducedMotion) this.updateEnemies(dt, true); return; }
    if (this.state !== 'playing') return;
    const L = this.level, p = this.player;
    this.levelTime += dt;
    this.invuln = Math.max(0, this.invuln - dt);
    this.shield = Math.max(0, this.shield - dt);
    this.speedBoost = Math.max(0, this.speedBoost - dt);
    this.shake = Math.max(0, this.shake - dt);

    if (this.timeLeft !== null) {
      this.timeLeft -= dt;
      if (this.timeLeft <= 0) { this.timeLeft = 0; this.bonusEnd(false); return; }
    }

    // Player movement
    let dx = (this.input.right ? 1 : 0) - (this.input.left ? 1 : 0);
    let dy = (this.input.down ? 1 : 0) - (this.input.up ? 1 : 0);
    const len = Math.hypot(dx, dy) || 1;
    const ti = this.tileAt(p.x, p.y);
    let speed = PLAYER_SPEED * (this.speedBoost > 0 ? 1.5 : 1) * (L.water[ti] ? 0.55 : 1);
    p.moving = dx !== 0 || dy !== 0;
    if (dx) p.facingLeft = dx < 0;
    let mx = (dx / len) * speed * dt, my = (dy / len) * speed * dt;
    if (L.wind[ti]) mx += L.wind[ti] * 42 * dt;
    this.moveBox(p, mx, my, PLAYER_W, PLAYER_H);
    if (p.moving) p.anim += dt;

    // Camera follows smoothly
    const tx = clamp(p.x - VIEW_W / 2, 0, WORLD_W - VIEW_W), ty = clamp(p.y - VIEW_H / 2, 0, WORLD_H - VIEW_H);
    const k = 1 - Math.exp(-dt * (this.reducedMotion ? 14 : 7));
    this.cam.x += (tx - this.cam.x) * k;
    this.cam.y += (ty - this.cam.y) * k;

    this.updateEnemies(dt, false);
    this.collectStuff();

    for (const pt of this.particles) { pt.x += pt.vx * dt; pt.y += pt.vy * dt; pt.vx *= 0.92; pt.vy *= 0.92; pt.life -= dt; }
    this.particles = this.particles.filter(pt => pt.life > 0);
  }

  updateEnemies(dt, demo) {
    const L = this.level, p = this.player;
    for (const e of L.enemies) {
      e.phase += dt;
      if (e.type === 'c') {
        const d = Math.hypot(p.x - e.x, p.y - e.y);
        let vx, vy;
        if (!demo && d < 110) { vx = ((p.x - e.x) / (d || 1)) * e.speed; vy = ((p.y - e.y) / (d || 1)) * e.speed; }
        else { vx = Math.cos(e.phase * 0.8) * e.speed * 0.6; vy = Math.sin(e.phase * 0.6) * e.speed * 0.6; }
        this.moveBox(e, vx * dt, vy * dt, ENEMY_BOX, ENEMY_BOX);
      } else {
        const hit = this.moveBox(e, e.vx * dt, e.vy * dt, ENEMY_BOX, ENEMY_BOX);
        if (hit.bx) e.vx *= -1;
        if (hit.by) e.vy *= -1;
      }
      if (!demo && this.invuln <= 0 && Math.abs(p.x - e.x) < (PLAYER_W + ENEMY_BOX) / 2 - 1 && Math.abs(p.y - e.y) < (PLAYER_H + ENEMY_BOX) / 2 - 1) {
        this.onHit(e);
      }
    }
  }

  onHit(e) {
    if (this.shield > 0) {
      this.invuln = 0.4;
      this.burst(e.x, e.y, '#8fd3ff', 8);
      return;
    }
    this.hp -= 1;
    this.hitThisLevel = true;
    this.invuln = 1.3;
    if (!this.reducedMotion) this.shake = 0.25;
    this.burst(this.player.x, this.player.y, this.level.def.theme.enemy, 12);
    this.audio?.play('hit');
    if (this.hp <= 0) {
      if (this.run.bonus) { this.bonusEnd(false); return; }
      this.state = 'gameover';
      this.audio?.play('over');
      this.saveBest();
      this.emit('gameover', { canContinue: this.canContinue(), credits: this.run.credits, score: this.run.score, checkpoint: !!this.checkpoint });
      this.announce('Game over.');
    } else {
      this.announce(`Hit by a ${this.level.def.enemy}! ${this.hp} HP left.`);
    }
  }

  collectStuff() {
    const L = this.level, p = this.player;
    const near = (o, r) => Math.abs(p.x - o.x) < r && Math.abs(p.y - o.y) < r;
    for (const t of L.tokens) {
      if (!t.taken && near(t, 10)) {
        t.taken = true;
        this.run.score += 100;
        this.audio?.play('token');
        this.burst(t.x, t.y, L.def.theme.token, 8);
        this.unlock('first-token');
        const left = L.tokens.filter(x => !x.taken).length;
        if (left === 0) { this.audio?.play('portal'); this.announce('All tokens collected. The portal is open!'); }
      }
    }
    for (const it of L.items) {
      if (!it.taken && near(it, 10)) {
        if (it.kind === 'heal' && this.hp >= this.maxHp) continue;
        it.taken = true;
        this.run.score += 50;
        this.audio?.play('power');
        this.burst(it.x, it.y, '#e8f2ff', 10);
        if (it.kind === 'heal') { this.hp = Math.min(this.maxHp, this.hp + 1); this.announce('Patch applied: +1 HP.'); }
        if (it.kind === 'shield') { this.shield = POWER_TIME; this.announce('Firewall shield up for 6 seconds.'); }
        if (it.kind === 'speed') { this.speedBoost = POWER_TIME; this.announce('Cache boost: faster movement for 6 seconds.'); }
      }
    }
    if (L.duck && !L.duck.found && near(L.duck, 10)) {
      L.duck.found = true;
      this.run.score += 250;
      this.audio?.play('secret');
      this.burst(L.duck.x, L.duck.y, '#ffd166', 16);
      this.unlock('duck');
      this.announce('You found the rubber duck. Explaining the bug out loud fixed it.');
    }
    const cp = L.checkpointPos;
    if (cp && near(cp, 11) && (!this.checkpoint || this.checkpoint.x !== cp.x)) {
      this.checkpoint = {
        x: cp.x, y: cp.y, score: this.run.score, time: this.levelTime,
        tokens: L.tokens.map(t => t.taken), items: L.items.map(t => t.taken),
      };
      this.audio?.play('checkpoint');
      this.announce('Checkpoint saved.');
    }
    if (L.portal && near(L.portal, 10) && L.tokens.every(t => t.taken)) this.levelClear();
  }

  levelClear() {
    const L = this.level;
    if (L.def.bonus) { this.bonusEnd(true); return; }
    const timeBonus = Math.max(0, Math.floor((90 - this.levelTime) * 5));
    const noHitBonus = this.hitThisLevel ? 0 : 300;
    this.run.score += 500 + timeBonus + noHitBonus;
    if (!this.hitThisLevel) this.unlock('no-hit');
    this.saveBest();
    this.audio?.play('clear');
    const last = this.run.index === LEVELS.length - 1;
    this.state = last ? 'victory' : 'levelclear';
    this.emit(last ? 'victory' : 'levelclear', {
      levelId: L.def.id, index: L.index, name: L.def.name, project: L.def.project,
      bonuses: { clear: 500, time: timeBonus, noHit: noHitBonus }, score: this.run.score, time: this.levelTime,
    });
    if (last) this.unlock('quest');
    this.announce(last ? 'Victory! Every world is cleared.' : `${L.def.name} cleared! Project unlocked.`);
  }

  bonusEnd(won) {
    const caught = this.level.tokens.filter(t => t.taken).length;
    if (won) { this.run.score += 1000 + Math.floor(this.timeLeft * 20); this.unlock('bonus'); }
    this.saveBest();
    this.state = 'bonusend';
    this.audio?.play(won ? 'clear' : 'over');
    this.emit('bonusend', { won, caught, total: this.level.tokens.length, score: this.run.score, project: this.level.def.project });
    this.announce(won ? 'Observatory cleared!' : `Time attack over. ${caught} raindrops caught.`);
  }

  saveBest() { this.hooks.onScore?.(this.run.score); }

  // ---------- HUD ----------
  pushHud() {
    if (!this.run || !this.level || this.level.demo) return;
    const L = this.level;
    const hud = {
      level: L.def.bonus ? 'BONUS' : `${L.index + 1}/${LEVELS.length}`,
      name: L.def.name,
      hp: Math.max(0, this.hp), maxHp: this.maxHp,
      tokens: L.tokens.filter(t => t.taken).length, total: L.tokens.length,
      score: this.run.score, credits: this.run.credits,
      shield: Math.ceil(this.shield), speed: Math.ceil(this.speedBoost),
      time: this.timeLeft !== null ? Math.ceil(this.timeLeft) : null,
      portalOpen: L.tokens.every(t => t.taken),
    };
    const key = JSON.stringify(hud);
    if (key !== this.lastHud) { this.lastHud = key; this.hooks.onHud?.(hud); }
  }

  // ---------- rendering ----------
  renderTiles(def) {
    const c = document.createElement('canvas');
    c.width = WORLD_W; c.height = WORLD_H;
    const g = c.getContext('2d');
    const t = def.theme;
    const wall = (x, y) => x < 0 || y < 0 || x >= COLS || y >= ROWS || def.map[y][x] === '#';
    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        const ch = def.map[y][x], px = x * TILE, py = y * TILE;
        if (ch === '#') {
          g.fillStyle = t.wall; g.fillRect(px, py, TILE, TILE);
          g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(px, py + TILE - 3, TILE, 3);
          if (!wall(x, y - 1)) { g.fillStyle = t.wallTop; g.fillRect(px, py, TILE, 2); }
          if (t.decor === 'brick') { g.fillStyle = 'rgba(0,0,0,0.3)'; g.fillRect(px, py + 7, TILE, 1); g.fillRect(px + ((y % 2) ? 4 : 11), py + 2, 1, 5); g.fillRect(px + ((y % 2) ? 11 : 4), py + 8, 1, 6); }
          if (t.decor === 'circuit' && (x * 7 + y * 13) % 4 === 0) { g.fillStyle = t.accent; g.fillRect(px + 3, py + 8, 10, 1); g.fillRect(px + 12, py + 5, 1, 4); g.fillRect(px + 11, py + 4, 3, 2); }
          if (t.decor === 'awning' && !wall(x, y + 1)) { for (let s = 0; s < TILE; s += 4) { g.fillStyle = (s / 4) % 2 ? t.accent : t.enemy; g.fillRect(px + s, py + TILE - 4, 4, 4); } }
          if (t.decor === 'sandbag') { g.fillStyle = 'rgba(255,255,255,0.08)'; g.fillRect(px + 1, py + 4, 6, 4); g.fillRect(px + 9, py + 4, 6, 4); g.fillRect(px + 5, py + 10, 6, 3); }
          if (t.decor === 'cloud' && !wall(x, y - 1)) { g.fillStyle = '#d8def0'; g.fillRect(px + 2, py - 2, 5, 3); g.fillRect(px + 8, py - 3, 6, 4); }
          if (t.decor === 'stars' && (x + y) % 3 === 0) { g.fillStyle = t.accent; g.fillRect(px + 7, py + 7, 2, 2); }
        } else {
          g.fillStyle = (x + y) % 2 ? t.floor : t.floor2; g.fillRect(px, py, TILE, TILE);
          g.fillStyle = 'rgba(255,255,255,0.035)'; g.fillRect(px + 7, py + 7, 2, 2);
          if (ch === '~') { g.fillStyle = t.water; g.fillRect(px, py, TILE, TILE); }
          if (t.decor === 'stars' && (x * 5 + y * 3) % 11 === 0) { g.fillStyle = '#e8f2ff'; g.fillRect(px + 3, py + 4, 1, 1); }
        }
      }
    }
    return c;
  }

  draw() {
    const g = this.g, L = this.level, p = this.player, t = L.def.theme;
    g.setTransform(this.scale, 0, 0, this.scale, 0, 0);
    g.imageSmoothingEnabled = false;
    let sx = 0, sy = 0;
    if (this.shake > 0) { sx = Math.round((Math.random() - 0.5) * 4); sy = Math.round((Math.random() - 0.5) * 4); }
    const cx = Math.round(this.cam.x) - sx, cy = Math.round(this.cam.y) - sy;
    const anim = this.reducedMotion ? 0 : this.time;
    g.fillStyle = '#0b1020'; g.fillRect(0, 0, VIEW_W, VIEW_H);
    g.drawImage(this.tileLayer, -cx, -cy);

    // Animated water and wind lanes
    const x0 = Math.floor(cx / TILE), y0 = Math.floor(cy / TILE);
    for (let y = y0; y <= y0 + Math.ceil(VIEW_H / TILE); y++) {
      for (let x = x0; x <= x0 + Math.ceil(VIEW_W / TILE); x++) {
        const i = y * COLS + x;
        if (x >= COLS || y >= ROWS) continue;
        const px = x * TILE - cx, py = y * TILE - cy;
        if (L.water[i]) {
          g.fillStyle = 'rgba(143,211,255,0.35)';
          const o = Math.floor(anim * 6 + x * 3) % 8;
          g.fillRect(px + o, py + 4, 5, 1); g.fillRect(px + ((o + 4) % 8), py + 11, 5, 1);
        }
        if (L.wind[i]) {
          g.fillStyle = 'rgba(232,242,255,0.22)';
          const dir = L.wind[i];
          const o = ((Math.floor(anim * 14) % TILE) * dir + TILE) % TILE;
          const ax = px + o;
          g.fillRect(ax, py + 6, 1, 4); g.fillRect(ax + dir, py + 7, 1, 2);
        }
      }
    }

    // Checkpoint flag
    if (L.checkpointPos) {
      const c = L.checkpointPos, on = this.checkpoint && this.checkpoint.x === c.x;
      g.fillStyle = '#e8f2ff'; g.fillRect(c.x - cx - 4, c.y - cy - 7, 1, 14);
      g.fillStyle = on ? '#ffd166' : '#516684';
      g.fillRect(c.x - cx - 3, c.y - cy - 7, 8, 5);
      g.fillStyle = '#141d31'; g.fillRect(c.x - cx - 6, c.y - cy + 6, 5, 2);
    }

    // Portal
    if (L.portal) {
      const open = L.tokens.every(tk => tk.taken);
      const px = L.portal.x - cx, py = L.portal.y - cy;
      const pulse = open ? Math.floor(anim * 6) % 3 : 0;
      g.fillStyle = open ? '#a78bfa' : '#2b3550'; g.fillRect(px - 7, py - 8, 14, 16);
      g.fillStyle = open ? '#70f5a3' : '#141d31'; g.fillRect(px - 5 + pulse, py - 6 + pulse, 10 - pulse * 2, 12 - pulse * 2);
      g.fillStyle = open ? '#e8f2ff' : '#516684'; g.fillRect(px - 1, py - 2, 2, 4);
      if (!open) { g.fillStyle = '#ffd166'; g.fillRect(px - 2, py - 3, 4, 1); }
    }

    // Items, duck, tokens
    for (const it of L.items) if (!it.taken) g.drawImage(itemSprite(it.kind), Math.round(it.x - cx - 3), Math.round(it.y - cy - 3 + (anim ? Math.round(Math.sin(anim * 3 + it.x)) : 0)));
    if (L.duck && !L.duck.found) { g.globalAlpha = 0.55; g.drawImage(itemSprite('duck'), L.duck.x - cx - 3, L.duck.y - cy - 3); g.globalAlpha = 1; }
    const tok = tokenSprite(L.def.id, t);
    for (const tk of L.tokens) {
      if (tk.taken) continue;
      const bob = anim ? Math.round(Math.sin(anim * 4 + tk.x * 0.1)) : 0;
      g.drawImage(tok, Math.round(tk.x - cx - 3), Math.round(tk.y - cy - 3 + bob));
    }

    // Enemies
    const shape = L.def.enemyShape;
    for (const e of L.enemies) {
      const fr = Math.floor((anim || e.phase) * 5) % 2;
      g.drawImage(enemySprite(shape, fr, t), Math.round(e.x - cx - 5), Math.round(e.y - cy - 5));
    }

    // Player
    if (!L.demo) {
      const visible = this.invuln <= 0 || this.reducedMotion || Math.floor(this.time * 10) % 2 === 0;
      if (this.invuln > 0 && this.reducedMotion) g.globalAlpha = 0.5;
      if (visible) {
        const fr = p.moving ? Math.floor(p.anim * 8) % 2 : 0;
        g.drawImage(playerSprite(this.skin, fr, p.facingLeft), Math.round(p.x - cx - 6), Math.round(p.y - cy - 7));
      }
      g.globalAlpha = 1;
      if (this.shield > 0) {
        g.strokeStyle = '#8fd3ff'; g.lineWidth = 1;
        g.strokeRect(Math.round(p.x - cx - 8) + 0.5, Math.round(p.y - cy - 9) + 0.5, 15, 17);
      }
    }

    // Particles
    for (const pt of this.particles) { g.fillStyle = pt.color; g.fillRect(Math.round(pt.x - cx), Math.round(pt.y - cy), 2, 2); }

    // Darkness for the Incident Dungeon
    if (L.def.dark && !L.demo) {
      const f = this.fog.getContext('2d');
      f.globalCompositeOperation = 'source-over';
      f.clearRect(0, 0, VIEW_W, VIEW_H);
      f.fillStyle = `rgba(5,6,14,${this.assist ? 0.5 : 0.86})`;
      f.fillRect(0, 0, VIEW_W, VIEW_H);
      f.globalCompositeOperation = 'destination-out';
      const gx = p.x - cx, gy = p.y - cy;
      const grad = f.createRadialGradient(gx, gy, 20, gx, gy, 78);
      grad.addColorStop(0, 'rgba(0,0,0,1)'); grad.addColorStop(1, 'rgba(0,0,0,0)');
      f.fillStyle = grad; f.fillRect(0, 0, VIEW_W, VIEW_H);
      g.drawImage(this.fog, 0, 0);
    }

    // Off-screen portal pointer once it opens
    if (!L.demo && L.portal && L.tokens.every(tk => tk.taken)) {
      const px = L.portal.x - cx, py = L.portal.y - cy;
      if (px < 0 || py < 0 || px > VIEW_W || py > VIEW_H) {
        const ax = clamp(px, 8, VIEW_W - 8), ay = clamp(py, 8, VIEW_H - 8);
        g.fillStyle = '#70f5a3'; g.fillRect(ax - 3, ay - 3, 6, 6);
        g.fillStyle = '#0b1020'; g.fillRect(ax - 1, ay - 1, 2, 2);
      }
    }
  }

  // QA snapshot (only exposed when the page is opened with ?qa=1)
  snapshot() {
    const L = this.level;
    return {
      state: this.state, level: L.def.id, index: L.index, hp: this.hp, maxHp: this.maxHp,
      score: this.run?.score ?? 0, credits: this.run?.credits ?? 0,
      tokensLeft: L.tokens.filter(t => !t.taken).length, tokens: L.tokens.length,
      player: { x: this.player.x, y: this.player.y }, enemies: L.enemies.length,
      checkpoint: !!this.checkpoint, shield: this.shield, speedBoost: this.speedBoost,
      timeLeft: this.timeLeft, portal: L.portal, invuln: this.invuln,
    };
  }
}
