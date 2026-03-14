// dashboard.js — main dashboard page

const grid = document.getElementById('dashboardGrid');
const queueItems = document.getElementById('queueItems');
const queueCount = document.getElementById('queueCount');

// project card template
function buildCard(p) {
  const color = projColor(p.id);
  const s = p.stats || {};
  const card = document.createElement('div');
  card.className = 'proj-card';
  card.style.setProperty('--proj-color', color);
  card.dataset.id = p.id;
  card.innerHTML = `
    <div class="card-header">
      <div class="card-title-row">
        <span class="card-badge">${p.short_name}</span>
        <span class="card-name">${p.name}</span>
      </div>
      ${p.port ? `<span class="card-port">${p.host && p.host !== 'localhost' ? p.host : ''}:${p.port}</span>` : ''}
    </div>
    <div class="card-stats">
      <div class="stat"><span class="stat-val active">${s.active||0}</span><span class="stat-lbl">Active</span></div>
      <div class="stat"><span class="stat-val">${s.next_up||0}</span><span class="stat-lbl">Next</span></div>
      <div class="stat"><span class="stat-val">${s.total||0}</span><span class="stat-lbl">Total</span></div>
      <div class="stat"><span class="stat-val">${s.done||0}</span><span class="stat-lbl">Done</span></div>
    </div>
    <div class="card-body">
      ${p.top_task ? `<div class="next-task-label">NEXT UP</div>
      <div class="next-task">${p.top_task.title}</div>` : '<div class="next-task" style="color:var(--text-dim)">No active tasks</div>'}
      <div class="card-actions">
        <button class="btn-resume" onclick="openResume('${p.id}','${p.name}','${p.short_name}','${color}')" style="--proj-color:${color}">▶ RESUME</button>
        <button class="btn-view" onclick="location.href=BASE+'/project/${p.id}'">BOARD</button>
        ${p.port ? `<button class="btn-launch" onclick="window.open('http://${p.host||'localhost'}:${p.port}','_blank')">LAUNCH</button>` : ''}
        ${(s.automatable||0) > 0 ? `<span class="automatable-count"><span class="auto-dot"></span>${s.automatable}</span>` : ''}
      </div>
    </div>`;
  return card;
}

async function loadDashboard() {
  const projects = await API.projects();
  grid.innerHTML = '';
  projects.forEach(p => grid.appendChild(buildCard(p)));
}

// queue panel
async function loadQueue() {
  const items = await API.queue();
  queueItems.innerHTML = '';
  queueCount.textContent = items.filter(i => i.status !== 'done').length;
  items.slice(-10).reverse().forEach(item => {
    const pl = typeof item.payload === 'string' ? JSON.parse(item.payload) : item.payload;
    const div = document.createElement('div');
    div.className = 'queue-item';
    div.innerHTML = `
      <div class="qi-project">${item.project_id || 'SYSTEM'} · ${item.type}</div>
      <div class="qi-payload">${pl.message || pl.title || JSON.stringify(pl)}</div>
      <div class="qi-status ${item.status}">${item.status.toUpperCase()}</div>`;
    queueItems.appendChild(div);
  });
}

// WebSocket handler
connectWS(msg => {
  if (msg.type === 'task_updated' || msg.type === 'task_created' || msg.type === 'tasks_reordered') loadDashboard();
  if (msg.type === 'queue_push' || msg.type === 'queue_update') loadQueue();
  if (msg.type === 'claude_status') {
    // handled by pollClaudeStatus interval
  }
});

// boot
startClock(document.getElementById('utcClock'));
pollClaudeStatus(document.getElementById('claudeDot'), document.getElementById('claudeLabel'));
loadDashboard();
loadQueue();
