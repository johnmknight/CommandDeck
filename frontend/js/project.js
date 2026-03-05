// project.js — project detail / kanban board

const pid = location.pathname.split('/').pop();
let currentColor = '#475569';
let claudeReady = false;

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  startClock(document.getElementById('utcClock'));
  pollClaudeStatus(document.getElementById('claudeDot'), document.getElementById('claudeLabel'));

  const proj = await API.project(pid);
  currentColor = projColor(proj.id);
  document.title = `CommandDeck — ${proj.name}`;
  document.getElementById('projName').textContent = proj.name;
  const badge = document.getElementById('projBadge');
  badge.textContent = proj.short_name;
  badge.style.background = currentColor;

  // set CSS var for add button color
  document.querySelector('.add-btn').style.background = currentColor;

  // set proj-color var globally
  document.documentElement.style.setProperty('--proj-color', currentColor);

  await loadTasks();
  setupDragDrop();
  setupAddTask();
}

// ── Tasks ─────────────────────────────────────────────────────────────────────
async function loadTasks() {
  const tasks = await API.tasks(pid);
  ['active','next','backlog','done'].forEach(s => {
    document.getElementById('col-' + s).innerHTML = '';
  });
  tasks.forEach(t => renderTask(t));
}

function renderTask(t) {
  const col = document.getElementById('col-' + t.status);
  if (!col) return;
  const card = document.createElement('div');
  card.className = 'task-card' + (t.automatable ? ' automatable' : '');
  card.draggable = true;
  card.dataset.id = t.id;
  card.dataset.status = t.status;
  card.dataset.priority = t.priority;
  card.innerHTML = `
    <div class="task-title">${t.title}</div>
    <div class="task-meta">
      ${t.category ? `<span class="task-cat">${t.category}</span>` : ''}
      <button class="btn-do-it${claudeReady ? ' visible' : ''}"
        onclick="doIt(event,'${t.id}','${encodeURIComponent(t.title)}')">⚡ DO IT</button>
    </div>`;
  col.appendChild(card);
  setupCardDrag(card);
}

// ── Do It (send to queue) ─────────────────────────────────────────────────────
async function doIt(e, taskId, titleEnc) {
  e.stopPropagation();
  const title = decodeURIComponent(titleEnc);
  await API.pushQueue({
    direction: 'user_to_claude',
    project_id: pid,
    task_id: taskId,
    type: 'task',
    payload: { message: title, task_id: taskId }
  });
  const btn = e.target;
  btn.textContent = '✓ QUEUED';
  btn.style.color = '#22c55e';
  setTimeout(() => { btn.textContent = '⚡ DO IT'; btn.style.color = ''; }, 3000);
}

// ── Add Task ──────────────────────────────────────────────────────────────────
function setupAddTask() {
  const input = document.getElementById('newTaskInput');
  const statusSel = document.getElementById('newTaskStatus');
  const autoCb = document.getElementById('newTaskAuto');
  const btn = document.getElementById('addTaskBtn');

  const submit = async () => {
    const title = input.value.trim();
    if (!title) return;
    btn.textContent = '...'; btn.disabled = true;
    const tasks = await API.tasks(pid);
    const sameStatus = tasks.filter(t => t.status === statusSel.value);
    const priority = sameStatus.length ? Math.max(...sameStatus.map(t => t.priority)) + 1 : 1;
    const t = await API.createTask({
      project_id: pid, title,
      status: statusSel.value,
      priority,
      automatable: autoCb.checked ? 1 : 0
    });
    renderTask(t);
    input.value = '';
    btn.textContent = 'ADD'; btn.disabled = false;
    input.focus();
  };

  btn.addEventListener('click', submit);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') submit(); });
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────
let dragId = null;

function setupDragDrop() {
  document.querySelectorAll('.col-tasks').forEach(col => {
    col.addEventListener('dragover', e => {
      e.preventDefault();
      const dragging = document.querySelector('.dragging');
      const after = getDragAfterElement(col, e.clientY);
      // clear all drag-over
      document.querySelectorAll('.task-card').forEach(c => c.classList.remove('drag-over'));
      if (after) after.classList.add('drag-over');
      if (dragging) {
        if (after) col.insertBefore(dragging, after);
        else col.appendChild(dragging);
      }
    });
    col.addEventListener('drop', async e => {
      e.preventDefault();
      document.querySelectorAll('.task-card').forEach(c => c.classList.remove('drag-over'));
      if (!dragId) return;
      const newStatus = col.closest('.board-col').dataset.status;
      const cards = [...col.querySelectorAll('.task-card')];
      const reorderPayload = cards.map((c, i) => ({
        id: c.dataset.id,
        status: newStatus,
        priority: i + 1,
        project_id: pid
      }));
      await API.reorderTasks(reorderPayload);
      // update data attrs
      cards.forEach((c, i) => { c.dataset.status = newStatus; c.dataset.priority = i + 1; });
      dragId = null;
    });
  });
}

function setupCardDrag(card) {
  card.addEventListener('dragstart', e => {
    dragId = card.dataset.id;
    card.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
  });
  card.addEventListener('dragend', () => {
    card.classList.remove('dragging');
    document.querySelectorAll('.task-card').forEach(c => c.classList.remove('drag-over'));
  });
}

function getDragAfterElement(container, y) {
  const cards = [...container.querySelectorAll('.task-card:not(.dragging)')];
  return cards.reduce((closest, card) => {
    const box = card.getBoundingClientRect();
    const offset = y - box.top - box.height / 2;
    if (offset < 0 && offset > closest.offset) return { offset, element: card };
    return closest;
  }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
connectWS(msg => {
  if (msg.type === 'task_updated' || msg.type === 'task_created') {
    const t = msg.task;
    if (t && t.project_id === pid) {
      // remove existing card if present, re-render
      const existing = document.querySelector(`.task-card[data-id="${t.id}"]`);
      if (existing) existing.remove();
      renderTask(t);
    }
  }
  if (msg.type === 'tasks_reordered') {
    if (msg.project_id === pid) loadTasks();
  }
  if (msg.type === 'claude_status') {
    claudeReady = (msg.status === 'idle' || msg.status === 'working');
    document.querySelectorAll('.btn-do-it').forEach(b =>
      b.classList.toggle('visible', claudeReady));
  }
});

// ── Boot ──────────────────────────────────────────────────────────────────────
init();
