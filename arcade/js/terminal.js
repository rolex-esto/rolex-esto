// ROLEX.EXE terminal: a fixed command table that prints portfolio facts.
// Output is built with DOM nodes + textContent only (no innerHTML, no eval).
import { PROFILE, PROJECTS, ACHIEVEMENTS, CREDENTIALS, FELLOWSHIPS, LEADERSHIP, SKILLS } from './data.js';

const SAFE_URL = /^(https:\/\/|mailto:)/;

export class Terminal {
  constructor({ output, form, input, actions }) {
    this.out = output;
    this.input = input;
    this.actions = actions;
    this.history = [];
    this.hIndex = 0;
    form.addEventListener('submit', e => {
      e.preventDefault();
      const cmd = input.value;
      input.value = '';
      this.run(cmd);
    });
    input.addEventListener('keydown', e => {
      if (e.key === 'ArrowUp' && this.history.length) { e.preventDefault(); this.hIndex = Math.max(0, this.hIndex - 1); input.value = this.history[this.hIndex] || ''; }
      if (e.key === 'ArrowDown' && this.history.length) { e.preventDefault(); this.hIndex = Math.min(this.history.length, this.hIndex + 1); input.value = this.history[this.hIndex] || ''; }
    });
    this.commands = {
      help: () => this.help(),
      about: () => this.about(),
      projects: () => this.projects(),
      skills: () => this.skills(),
      achievements: () => this.achievements(),
      contact: () => this.contact(),
      play: () => { this.line('Booting BUG HUNTER… good luck, player 01.', 'ok'); this.actions.play(); },
      clear: () => { this.out.replaceChildren(); },
      // Easter eggs (harmless)
      whoami: () => this.line(`${PROFILE.name.toLowerCase().replace(/\W+/g, '-')} — player 01, class: ${PROFILE.className}`),
      sudo: () => { this.line('Permission denied: this incident will be reported to the rubber duck.', 'warn'); this.actions.unlock('sudo'); },
      coffee: () => { this.line('    ( (\n     ) )\n  ........\n  |      |]\n  \\      /\n   `----\'\nBrewing… +1 focus. Hidden achievement unlocked.', 'ok'); this.actions.unlock('coffee'); },
      ls: () => this.line('about.txt  projects/  skills.json  achievements.log  contact.vcf  bug_hunter.exe'),
      bonus: () => this.actions.bonus(),
      joke: () => this.line('Why do programmers prefer dark mode? Because light attracts bugs.'),
      reset: () => this.actions.reset(),
      exit: () => this.line('There is no escape from the arcade. Try `play` instead.'),
    };
    this.line('ROLEX.EXE terminal v1.0 — type `help` and press Enter.', 'dim');
  }

  run(raw) {
    const cmd = String(raw || '').trim().toLowerCase().slice(0, 40);
    if (!cmd) return;
    this.history.push(cmd);
    this.hIndex = this.history.length;
    this.line(`player01@rolex.exe:~$ ${cmd}`, 'cmd');
    const name = cmd.split(/\s+/)[0];
    const fn = this.commands[name];
    if (fn) fn();
    else this.line(`command not found: ${name} — type \`help\` for the list.`, 'warn');
    this.out.scrollTop = this.out.scrollHeight;
  }

  line(text, cls = '') {
    const p = document.createElement('p');
    if (cls) p.className = `t-${cls}`;
    p.textContent = text;
    this.out.append(p);
    return p;
  }

  link(label, url) {
    const p = document.createElement('p');
    p.append('  ↳ ');
    if (!SAFE_URL.test(url)) { p.append(label); this.out.append(p); return; }
    const a = document.createElement('a');
    a.href = url;
    a.textContent = label;
    if (url.startsWith('https://')) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    p.append(a);
    this.out.append(p);
  }

  heading(text) { this.line(`== ${text} ==`, 'head'); }

  help() {
    this.heading('COMMANDS');
    [
      ['help', 'show this list'],
      ['about', 'player profile'],
      ['projects', 'project worlds and links'],
      ['skills', 'skill inventory'],
      ['achievements', 'hackathons, certifications, fellowships, leadership'],
      ['contact', 'ways to reach Rolex'],
      ['play', 'start BUG HUNTER'],
      ['clear', 'clear the screen'],
    ].forEach(([c, d]) => this.line(`  ${c.padEnd(13)} ${d}`));
    this.line('Some commands are hidden. Real developers check the docs… or just try things.', 'dim');
  }

  about() {
    this.heading('PLAYER PROFILE');
    this.line(`PLAYER ........ ${PROFILE.name}`);
    this.line(`CLASS ......... ${PROFILE.className}`);
    this.line(`SPECIALIZING .. ${PROFILE.specializations.join(' · ')}`);
    this.line(`EDUCATION ..... ${PROFILE.education}`);
    this.line(`CURRENT QUEST . ${PROFILE.quest}`);
    FELLOWSHIPS.forEach(f => this.line(`FELLOWSHIP .... ${f}`));
  }

  projects() {
    this.heading('PROJECT WORLDS');
    PROJECTS.forEach(p => {
      this.line(`◆ ${p.world.toUpperCase()} — ${p.name}`, 'ok');
      this.line(`  ${p.summary}`);
      this.line(`  role: ${p.role} · ${p.status}`, 'dim');
      p.links.forEach(l => this.link(l.label, l.url));
    });
  }

  skills() {
    this.heading('SKILL INVENTORY');
    Object.entries(SKILLS).forEach(([k, v]) => this.line(`  ${k.padEnd(18)} ${v.join(', ')}`));
  }

  achievements() {
    this.heading('HACKATHONS');
    ACHIEVEMENTS.forEach(a => this.line(`  ★ ${a}`));
    this.heading('CERTIFICATIONS & RECOGNITION');
    CREDENTIALS.forEach(c => this.line(`  ▸ ${c}`));
    this.link('Verify DP-700 on Microsoft Learn', 'https://learn.microsoft.com/en-us/users/rolexesto-7021/credentials/certification/fabric-data-engineer-associate?tab=credentials-tab');
    this.heading('LEADERSHIP');
    LEADERSHIP.forEach(l => this.line(`  ▸ ${l}`));
    this.line('These are real-world credentials. In-game XP and badges are separate and just for fun.', 'dim');
  }

  contact() {
    this.heading('CONTACT');
    this.link('Portfolio — rolex-esto.vercel.app', PROFILE.links.portfolio);
    this.link('LinkedIn', PROFILE.links.linkedin);
    this.link('GitHub — @rolex-esto', PROFILE.links.github);
    this.link('Email', PROFILE.links.email);
  }
}
