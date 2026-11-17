// Portfolio facts used by the arcade (terminal, quest log, unlock cards).
// Sources: the profile README in this repository and the owner's portfolio site
// data (rolex-esto.vercel.app). Do not add claims that neither source states.
// Game XP, levels and in-game achievements are gamification only.

export const PROFILE = {
  name: 'Rolex J. Esto',
  handle: 'rolex-esto',
  className: 'Software Developer / AI Builder',
  specializations: ['Software', 'AI', 'Data', 'Cloud', 'Cybersecurity'],
  education: 'BSIT, STI College Fairview (September 2023 – July 2027)',
  quest: 'Building real-world software solutions — BizPilot, TAPME client sites, Microsoft Fabric data pipelines',
  links: {
    portfolio: 'https://rolex-esto.vercel.app/',
    github: 'https://github.com/rolex-esto',
    linkedin: 'https://linkedin.com/in/rolex-esto-1b33b2391/',
    email: 'mailto:rolexesto0001@gmail.com',
    profile: 'https://github.com/rolex-esto/rolex-esto',
    source: 'https://github.com/rolex-esto/rolex-esto/tree/main/arcade',
  },
};

export const PROJECTS = [
  {
    id: 'bizpilot', world: 'Merchant Kingdom', name: 'BizPilot',
    role: 'Founder & Developer', status: 'Active development · private repository',
    summary: 'One place for Filipino online sellers to manage customer messages, orders, stock, and daily operations, with an AI sales assistant and a shared operations calendar.',
    stack: ['Unified inbox', 'AI sales assistant', 'Conversational ordering', 'Operations calendar'],
    links: [{ label: 'Live site', url: 'https://biz-pilot-msme.vercel.app/' }],
  },
  {
    id: 'smartwatts', world: 'Energy Realm', name: 'SmartWatts',
    role: 'Lead Developer · Team KuryenTech', status: 'Top 10 Finalist — Meralco IDOL Hackathon',
    summary: 'Helps households understand electricity use with bill scanning, appliance tracking, usage trends, estimates, and practical suggestions, plus an AI advisor in English and Tagalog.',
    stack: ['Bill scanning', 'Appliance tracking', 'Usage estimates', 'AI advisor (EN/TL)'],
    links: [],
  },
  {
    id: 'opspilot', world: 'Incident Dungeon', name: 'OpsPilot',
    role: 'Solo Developer', status: 'Top 2 Winner — DevKada × ClankerCloud Build Challenge',
    summary: 'An AI DevOps incident investigator that helps tech teams find the cause of outages from evidence, and makes clear when a cause is not yet confirmed.',
    stack: ['AI agent design', 'Incident response', 'Evidence-based reasoning', 'Cloud observability'],
    links: [{ label: 'Repository', url: 'https://github.com/rolex-esto/opspilot' }, { label: 'ClankerCloud marketplace', url: 'https://market.clankercloud.ai/' }],
  },
  {
    id: 'baharoute', world: 'Floodlands', name: 'BahaRoute',
    role: 'Lead Developer', status: 'Top 36 Team · Top 10 Climate Change Track — BuildOvernights KiroxHackaton',
    summary: 'Flood-aware routing for Metro Manila across 17 cities and 1,710 barangays, using Project NOAH flood history, live rainfall forecasts, and spoken hazard alerts.',
    stack: ['Project NOAH flood data', 'Rainfall forecasts', 'Voice hazard alerts'],
    links: [{ label: 'Repository', url: 'https://github.com/rolex-esto/KiroxQuick_Flood_CTRL' }, { label: 'Live demo', url: 'https://baha-route.vercel.app/' }],
  },
  {
    id: 'wwl', world: 'Weather World', name: 'Weather Weather Lang',
    role: 'AI Orchestrator', status: '3rd Place — KiroVerse Hack Sprint (AWS & RevenueCat)',
    summary: 'A chat-style weather companion that gives people weather updates in a friendly, conversational way.',
    stack: ['React 18', 'TypeScript', 'Vite', 'DuckDB-WASM', 'Parquet', 'Recharts', 'Open-Meteo API', 'Playwright'],
    links: [{ label: 'Team repository', url: 'https://github.com/rolex-esto/Kirovers-Hack-Sprint-Shipaton-Edition' }, { label: 'Live demo', url: 'https://kiroverse-hack-sprint-shipaton-edition.vercel.app/' }],
  },
  {
    id: 'ulanba', world: 'Rain Observatory', name: 'Ulan Ba?',
    role: 'Creator & Frontend Developer', status: 'Solo project',
    summary: 'A Philippine rain forecast dashboard with hourly rain and severity forecasts for 17 regions and 150+ cities, plus automatic location detection.',
    stack: ['React', 'TypeScript', 'Vite', 'Recharts', 'Open-Meteo API', 'Geolocation'],
    links: [{ label: 'Repository', url: 'https://github.com/rolex-esto/kiro-phWeather' }],
  },
  {
    id: 'classic', world: 'Commerce City', name: 'Classic Flagship Store',
    role: 'Lead Developer', status: 'E-commerce capstone · private repository',
    summary: 'An online store with separate admin, cashier, and customer dashboards, secure Google sign-in, and inventory tools.',
    stack: ['PHP', 'MySQL', 'PDO', 'Google OAuth', 'PHPMailer'],
    links: [{ label: 'Live site', url: 'https://classicflagshipstore.com/' }],
  },
  {
    id: 'tapme', world: 'Guild Hall', name: 'TAPME',
    role: 'Freelance Web Developer · 2025 – Present', status: 'Client work',
    summary: 'Builds NFC tap pages (calling cards, review and social pages, menus, brochures) and client websites, making sure every tap or QR scan opens cleanly on any phone.',
    stack: ['NFC pages', 'Client websites', 'Admin tools'],
    links: [{ label: 'Website', url: 'https://tapmeph.com/' }],
  },
];

export const ACHIEVEMENTS = [
  'Top 2 Winner — DevKada × ClankerCloud Build Challenge (Aug 2026) · OpsPilot',
  '3rd Place — KiroVerse Hack Sprint, AWS & RevenueCat (Jun–Aug 2026) · Weather Weather Lang',
  'Top 10 Finalist — Meralco IDOL Hackathon (Nov 2026) · Team KuryenTech / SmartWatts',
  'Top 36 Team · Top 10 Climate Change Track — BuildOvernights KiroxHackaton (Oct 2026) · BahaRoute',
];

export const CREDENTIALS = [
  'Microsoft Certified: Fabric Data Engineer Associate (DP-700) — Nov 2026, valid until Nov 10, 2027',
  'ISC2 Certified in Cybersecurity (CC) — Mar 2026',
  'DICT-Recognized Cybersecurity Professional, Category 2 (Intermediate) — Sep 2026 (professional recognition)',
  'Appkademiya Certified Cybersecurity Professional (CCP) — Aug 2026',
  'Red Team Leaders Certified Threat Intelligence & Governance Analyst (CTIGA) — Jan 2026',
  'Google AI Professional Certificate — Aug 2026',
  'DataCamp Certified Associate Data Engineer — Jul 2026',
  'DataCamp Certified Associate Data Analyst — May 2026',
  'DataCamp Certified SQL Associate — Apr 2026',
  'DataCamp Certified in Data Literacy — Jul 2026',
  'Training: AWS SimuLearn Cloud Practitioner (Jul 2026) · Microsoft DP-900 (Jul 2026), DP-700 (Aug 2026) and PL-300 (Oct 2026) curriculum tracks · DICT Region V Data Privacy Protection, 20 hours (Jun 2026)',
];

export const FELLOWSHIPS = [
  'Eskwelabs Innovation Fellowship (EIF), Cohort 11 — Data Innovation Fellow (Aug–Nov 2026)',
  'GCI World 2026 — Data Science & AI, Matsuo-Iwasawa Laboratory, University of Tokyo (Sep–Nov 2026)',
];

export const LEADERSHIP = [
  'Founding President — Microsoft Student Community, STI Fairview',
  'AWS Learning Club Lead — AWS Student User Group Philippines',
  'Delegate — Data Engineering Pilipinas × Echelon 2026 (Aug 2026)',
  'Venue Partnerships Associate — Seekers Guild (Aug–Nov 2026)',
];

export const SKILLS = {
  Programming: ['JavaScript', 'TypeScript', 'Python', 'PHP', 'SQL'],
  Frontend: ['React', 'Next.js', 'Vite', 'HTML', 'CSS', 'Recharts'],
  Backend: ['Node.js', 'FastAPI', 'OAuth'],
  'Data & Databases': ['MySQL', 'PostgreSQL', 'Power BI', 'DuckDB', 'Pandas', 'NumPy', 'Parquet', 'Excel'],
  'Cloud & DevOps': ['AWS', 'Azure', 'Google Cloud', 'Vercel', 'Microsoft Fabric'],
  'AI & Automation': ['Claude Code', 'Codex', 'Cursor', 'Kiro', 'Antigravity'],
  Cybersecurity: ['IAM', 'ISC2 CC', 'Threat intelligence (CTIGA)'],
  'Developer Tools': ['Git', 'GitHub', 'Playwright'],
};
