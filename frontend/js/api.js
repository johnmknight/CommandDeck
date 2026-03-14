// api.js — shared API + WebSocket helpers

// Auto-detect reverse proxy prefix (e.g. '/deck' behind nginx, '' on direct port)
const BASE = (() => {
  const seg = window.location.pathname.split('/')[1] || '';
  if (!seg || seg.includes('.') || ['api','static','project','ws'].includes(seg)) return '';
  return '/' + seg;
})();

const API = {
  async get(url)       { const r = await fetch(BASE + url); return r.json(); },
  async post(url, d)   { const r = await fetch(BASE + url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}); return r.json(); },
  async patch(url, d)  { const r = await fetch(BASE + url,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}); return r.json(); },

  projects:       ()       => API.get('/api/projects'),
  project:        id       => API.get(`/api/projects/${id}`),
  tasks:          pid      => API.get(`/api/projects/${pid}/tasks`),
  createTask:     d        => API.post('/api/tasks', d),
  updateTask:     (id, d)  => API.patch(`/api/tasks/${id}`, d),
  reorderTasks:   items    => API.post('/api/tasks/reorder', items),
  claudeStatus:   ()       => API.get('/api/claude/status'),
  queue:          ()       => API.get('/api/queue'),
  pushQueue:      d        => API.post('/api/queue', d),
};

// project color map
const COLORS = {
  artemisops: '#F97316', marchog: '#EAB308',
  captainmurphys: '#A855F7', findajob: '#0EA5E9', tikibar: '#10B981'
};
function projColor(id) { return COLORS[id] || '#475569'; }

// UTC clock
function startClock(el) {
  const tick = () => {
    const d = new Date();
    el.textContent = d.toUTCString().replace('GMT','UTC').split(' ').slice(1,5).join(' ');
  };
  tick(); setInterval(tick, 1000);
}

// Claude status badge
let claudeOnline = false;
async function pollClaudeStatus(dotEl, labelEl) {
  const update = async () => {
    try {
      const s = await API.claudeStatus();
      const age = s.last_heartbeat
        ? (Date.now() - new Date(s.last_heartbeat).getTime()) / 1000
        : 9999;
      claudeOnline = age < 60 && s.status !== 'offline';
      const st = claudeOnline ? s.status : 'offline';
      dotEl.className = 'badge-dot ' + st;
      labelEl.textContent = claudeOnline
        ? `CLAUDE: ${(s.status||'idle').toUpperCase()}`
        : 'CLAUDE OFFLINE';
      // update all Do It buttons
      document.querySelectorAll('.btn-do-it').forEach(b => {
        b.classList.toggle('visible', claudeOnline);
      });
    } catch {}
  };
  update(); setInterval(update, 15000);
}

// WebSocket
function connectWS(onMessage) {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${proto}://${location.host}${BASE}/ws`);
  ws.onmessage = e => { try { onMessage(JSON.parse(e.data)); } catch {} };
  ws.onclose   = () => setTimeout(() => connectWS(onMessage), 3000);
  return ws;
}
