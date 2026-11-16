// Tiny original 8-bit sound effects synthesized with the Web Audio API.
// No audio files, no autoplay: the AudioContext is only created after a user gesture.

const SFX = {
  token: [[660, 0.05], [990, 0.07]],
  power: [[523, 0.05], [659, 0.05], [784, 0.05], [1047, 0.09]],
  hit: [[220, 0.08, 'sawtooth'], [140, 0.12, 'sawtooth']],
  portal: [[392, 0.06], [523, 0.06], [784, 0.12]],
  checkpoint: [[784, 0.06], [988, 0.1]],
  clear: [[523, 0.08], [659, 0.08], [784, 0.08], [1047, 0.12], [784, 0.06], [1047, 0.2]],
  over: [[392, 0.12], [330, 0.12], [262, 0.12], [196, 0.3]],
  select: [[880, 0.04]],
  secret: [[1047, 0.05], [1319, 0.05], [1568, 0.05], [2093, 0.12]],
};

export class Audio8 {
  constructor(muted) {
    this.muted = !!muted;
    this.ctx = null;
  }

  // Must be called from inside a user-initiated event handler.
  unlock() {
    if (this.ctx || this.muted) return;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    try { this.ctx = new AC(); } catch { this.ctx = null; }
  }

  setMuted(m) {
    this.muted = !!m;
    if (!this.muted) this.unlock();
  }

  play(name) {
    if (this.muted || !this.ctx || !SFX[name]) return;
    if (this.ctx.state === 'suspended') this.ctx.resume().catch(() => {});
    let t = this.ctx.currentTime;
    for (const [freq, dur, type = 'square'] of SFX[name]) {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, t);
      gain.gain.setValueAtTime(0.06, t);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc.connect(gain).connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + dur + 0.02);
      t += dur * 0.9;
    }
  }
}
