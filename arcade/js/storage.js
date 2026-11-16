// Local, non-sensitive game progress only (best score, unlocks, settings).
// Every access is guarded: private windows or blocked storage just disable saving.

const KEY = 'rolex-exe:save:v1';

const DEFAULTS = {
  best: 0,
  highestLevel: 0,        // index of the furthest main level reached
  cleared: [],            // level ids cleared at least once
  unlockedProjects: [],   // project ids unlocked through play
  achievements: [],       // in-game achievement ids
  skins: ['dev', 'hacker', 'founder'],
  skin: 'dev',
  settings: { muted: false, reducedMotion: null, assist: false },
};

export function loadSave() {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return structuredClone(DEFAULTS);
    const data = JSON.parse(raw);
    return {
      ...structuredClone(DEFAULTS),
      ...data,
      settings: { ...DEFAULTS.settings, ...(data.settings || {}) },
    };
  } catch {
    return structuredClone(DEFAULTS);
  }
}

export function writeSave(save) {
  try { window.localStorage.setItem(KEY, JSON.stringify(save)); return true; } catch { return false; }
}

export function resetSave() {
  try { window.localStorage.removeItem(KEY); } catch { /* storage unavailable */ }
  return structuredClone(DEFAULTS);
}

export function addUnique(list, value) {
  if (!list.includes(value)) { list.push(value); return true; }
  return false;
}
