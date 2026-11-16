// Original pixel-art sprites, defined as character maps and pre-rendered once.
// Each map character indexes a palette; '.' is transparent.

const PLAYER_FRAMES = [
  [
    '....HHHH....',
    '...HHHHHHH..',
    '...HSSSSSH..',
    '...SSESSES..',
    '...SSSSSSS..',
    '....SSMSS...',
    '..CCCCCCCC..',
    '.SCCLLLLCCS.',
    '.SCCLLLLCCS.',
    '..CCCCCCCC..',
    '...PP..PP...',
    '...BB..BB...',
  ],
  [
    '....HHHH....',
    '...HHHHHHH..',
    '...HSSSSSH..',
    '...SSESSES..',
    '...SSSSSSS..',
    '....SSMSS...',
    '..CCCCCCCC..',
    '.SCCLLLLCCS.',
    '.SCCLLLLCCS.',
    '..CCCCCCCC..',
    '..PP....PP..',
    '..BB....BB..',
  ],
];

export const SKINS = {
  dev: { label: 'DEV GREEN', desc: 'Default hoodie. Ships on Fridays (carefully).', palette: { H: '#2b1d14', S: '#f1c27d', E: '#0b1020', M: '#b5651d', C: '#70f5a3', L: '#e8f2ff', P: '#3b4a7a', B: '#141d31' } },
  hacker: { label: 'PIXEL PURPLE', desc: 'Night-shift debugger. Dark mode by default.', palette: { H: '#141d31', S: '#e0ac69', E: '#0b1020', M: '#8d5524', C: '#a78bfa', L: '#70f5a3', P: '#253b52', B: '#0b1020' } },
  founder: { label: 'ARCADE GOLD', desc: 'Founder fit. Pitch deck in the backpack.', palette: { H: '#3d2817', S: '#f1c27d', E: '#0b1020', M: '#b5651d', C: '#ffd166', L: '#141d31', P: '#2b2440', B: '#141d31' } },
  glitch: { label: 'GLITCH (SECRET)', desc: 'Unlocked with an old cheat code. Probably a feature.', secret: true, palette: { H: '#e8f2ff', S: '#ff6b9e', E: '#0b1020', M: '#0b1020', C: '#0b1020', L: '#ff6b9e', P: '#70f5a3', B: '#a78bfa' } },
};

const ENEMY_SHAPES = {
  bug: [
    ['.A......A.', '..A....A..', '..BBBBBB..', '.BBWBBWBB.', 'LBBEBBEBBL', '.BBBBBBBB.', 'LBBBBBBBBL', '.BBBBBBBB.', '..BBBBBB..', '.L..L..L..'],
    ['.A......A.', '..A....A..', '..BBBBBB..', '.BBWBBWBB.', '.BBEBBEBB.', 'LBBBBBBBBL', '.BBBBBBBB.', 'LBBBBBBBBL', '..BBBBBB..', '..L..L..L.'],
  ],
  spark: [
    ['....BB....', '...BWWB...', '..BWWWWB..', '.BWEWWEWB.', 'BBWWWWWWBB', '..BWWWWB..', '...BWWB...', '..B.BB.B..', '.B..B...B.', '....B.....'],
    ['....B.....', '.B.BWWB.B.', '..BWWWWB..', '.BWEWWEWB.', 'BBWWWWWWBB', '..BWWWWB..', '..BBWWBB..', '.B..BB..B.', '....B.B...', '.....B....'],
  ],
  glitch: [
    ['BBBB..BBBB', 'BWWB..BWWB', 'BBBBBBBBBB', '..BEBBEB..', 'BBBBBBBBBB', 'B.BBBBBB.B', 'BBBBLLBBBB', '..BB..BB..', '.BBB..BBB.', 'BB......BB'],
    ['.BBBB..BBB', '.BWWB..BWW', 'BBBBBBBBBB', '.BEBBEB...', 'BBBBBBBBBB', 'BB.BBBB.BB', 'BBBLLBBBBB', '.BB..BB...', 'BBB..BBB..', '.BB....BB.'],
  ],
  blob: [
    ['...BBBB...', '..BBBBBB..', '.BBWBBWBB.', '.BBEBBEBB.', 'BBBBBBBBBB', 'BBBBLLBBBB', 'BBBBBBBBBB', '.BBBBBBBB.', 'B.BB.BB.B.', '..........'],
    ['..........', '...BBBB...', '..BBBBBB..', '.BBWBBWBB.', 'BBBEBBEBBB', 'BBBBBBBBBB', 'BBBBLLBBBB', 'BBBBBBBBBB', '.BBBBBBBB.', '.B.BB.BB.B'],
  ],
  cloud: [
    ['...WWWW...', '..WWWWWWW.', '.WWWWWWWWW', 'WWWEWWEWWW', 'WWWWWWWWWW', '.BBBBBBBB.', '..A..A..A.', '.A..A..A..', '..........', '..........'],
    ['....WWWW..', '.WWWWWWW..', 'WWWWWWWWW.', 'WWWEWWEWWW', 'WWWWWWWWWW', '.BBBBBBBB.', '.A..A..A..', '..A..A..A.', '..........', '..........'],
  ],
};

const ITEMS = {
  heal: { map: ['.RR.RR.', 'RWRRRRR', 'RRRRRRR', 'RRRRRRR', '.RRRRR.', '..RRR..', '...R...'], pal: { R: '#ff6b9e', W: '#ffe3ee' } },
  shield: { map: ['.BBBBB.', 'BWBBBBB', 'BWBBBBB', 'BBBBBBB', '.BBBBB.', '..BBB..', '...B...'], pal: { B: '#8fd3ff', W: '#e8f2ff' } },
  speed: { map: ['....YY.', '...YY..', '..YYYYY', '.YYYYY.', '...YY..', '..YY...', '.Y.....'], pal: { Y: '#ffd166' } },
  duck: { map: ['..YY...', '.YYEY..', '.YYYYOO', '..YY...', 'YYYYYY.', 'YYYYYY.', '.YYYY..'], pal: { Y: '#ffd166', E: '#0b1020', O: '#ff9e6b' } },
};

function render(map, palette, scale = 1, flip = false) {
  const h = map.length, w = Math.max(...map.map(r => r.length));
  const c = document.createElement('canvas');
  c.width = w * scale; c.height = h * scale;
  const g = c.getContext('2d');
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const ch = map[y][x];
      if (!ch || ch === '.' || !palette[ch]) continue;
      g.fillStyle = palette[ch];
      g.fillRect((flip ? w - 1 - x : x) * scale, y * scale, scale, scale);
    }
  }
  return c;
}

const cache = new Map();
function cached(key, make) {
  if (!cache.has(key)) cache.set(key, make());
  return cache.get(key);
}

export function playerSprite(skin, frame, facingLeft) {
  const s = SKINS[skin] || SKINS.dev;
  return cached(`p:${skin}:${frame}:${facingLeft}`, () => render(PLAYER_FRAMES[frame % 2], s.palette, 1, facingLeft));
}

export function enemySprite(shape, frame, theme) {
  const pal = { B: theme.enemy, W: '#e8f2ff', E: '#0b1020', L: theme.enemyDark, A: theme.enemyDark };
  if (shape === 'cloud') { pal.W = '#d8def0'; pal.B = theme.enemy; pal.A = '#8fd3ff'; }
  if (shape === 'spark') { pal.W = '#fff4c2'; pal.B = theme.enemy; }
  return cached(`e:${shape}:${frame}:${theme.enemy}`, () => render(ENEMY_SHAPES[shape][frame % 2], pal));
}

export function itemSprite(kind) {
  return cached(`i:${kind}`, () => render(ITEMS[kind].map, ITEMS[kind].pal));
}

// Tokens are drawn per level so each world has its own collectible.
const TOKEN_MAPS = {
  merchant: ['.DDDD.', 'DYYYYD', 'DYDDYD', 'DYDDYD', 'DYYYYD', '.DDDD.'],
  energy: ['..YY..', '.YYY..', 'YYYYYY', '..YYY.', '..YY..', '.Y....'],
  incident: ['YYYYD.', 'YDDYYD', 'YYYYYY', 'YDDDDY', 'YYYYYY', 'YYYYYY'],
  flood: ['.YYYY.', 'YYDDYY', 'YYDDYY', '.YYYY.', '..YY..', '..YY..'],
  weather: ['.YYYY.', 'YYWYYY', 'YWYYYY', 'YYYYYY', 'YYYYYY', '.YYYY.'],
  observatory: ['..YY..', '..YY..', '.YYYY.', 'YYWYYY', 'YYYYYY', '.YYYY.'],
};

export function tokenSprite(levelId, theme) {
  const dark = levelId === 'incident' ? '#6c5aa8' : '#7a5a12';
  return cached(`t:${levelId}`, () => render(TOKEN_MAPS[levelId] || TOKEN_MAPS.merchant, { Y: theme.token, D: dark, W: '#ffffff' }));
}

// Small skin preview for the menu (scaled up, crisp).
export function skinPreview(skin) {
  return render(PLAYER_FRAMES[0], (SKINS[skin] || SKINS.dev).palette, 4, false);
}
