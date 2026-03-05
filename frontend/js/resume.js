// resume.js — Resume Session modal

let currentPrompt = '';
let currentColor  = '#475569';

const overlay  = document.getElementById('resumeOverlay');
const badge    = document.getElementById('modalBadge');
const title    = document.getElementById('modalTitle');
const meta     = document.getElementById('modalMeta');
const body     = document.getElementById('modalBody');
const btnCopy  = document.getElementById('btnCopy');
const btnCopyOpen = document.getElementById('btnCopyOpen');

// ── Open modal ────────────────────────────────────────────────────────────────
async function openResume(pid, projName, shortName, color) {
  currentColor = color;
  currentPrompt = '';

  // style
  badge.textContent = shortName;
  badge.style.background = color;
  title.textContent = `RESUME — ${projName}`;
  btnCopy.style.background = color;
  overlay.classList.add('open');

  // loading state
  meta.innerHTML = '';
  body.innerHTML = '<div class="modal-loading"><span class="spin">⟳</span> BUILDING CONTEXT...</div>';

  try {
    const data = await API.get(`/api/projects/${pid}/resume`);
    currentPrompt = data.prompt;

    // meta bar
    const gitClean = !data.git_status || data.git_status.trim() === '';
    meta.innerHTML = `
      <span>ACTIVE <strong>${data.active_count}</strong></span>
      <span>UP NEXT <strong>${data.next_count}</strong></span>
      <span>GIT <strong style="color:${gitClean ? '#22c55e' : '#f59e0b'}">${gitClean ? 'CLEAN' : 'DIRTY'}</strong></span>
      <span style="margin-left:auto;font-size:9px;color:var(--text-dim)">
        ${new Date().toUTCString().split(' ').slice(1,5).join(' ')} UTC
      </span>`;

    // prompt display
    body.innerHTML = `<div class="prompt-box" id="promptBox">${escHtml(data.prompt)}</div>`;

  } catch(e) {
    body.innerHTML = `<div class="modal-loading" style="color:#ef4444">ERROR BUILDING CONTEXT</div>`;
  }
}

// ── Close ─────────────────────────────────────────────────────────────────────
function closeResume() {
  overlay.classList.remove('open');
}

document.getElementById('modalClose').addEventListener('click', closeResume);
overlay.addEventListener('click', e => { if (e.target === overlay) closeResume(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeResume(); });

// ── Copy ──────────────────────────────────────────────────────────────────────
btnCopy.addEventListener('click', async () => {
  if (!currentPrompt) return;
  await navigator.clipboard.writeText(currentPrompt);
  btnCopy.textContent = '✓ COPIED';
  btnCopy.classList.add('copied');
  setTimeout(() => {
    btnCopy.textContent = '⎘ COPY PROMPT';
    btnCopy.classList.remove('copied');
  }, 2500);
});

// ── Copy + Open Claude ────────────────────────────────────────────────────────
btnCopyOpen.addEventListener('click', async () => {
  if (!currentPrompt) return;
  await navigator.clipboard.writeText(currentPrompt);
  window.open('https://claude.ai/new', '_blank');
  btnCopyOpen.textContent = '✓ COPIED — PASTE IN CLAUDE';
  setTimeout(() => { btnCopyOpen.textContent = '⎘ COPY + OPEN CLAUDE'; }, 3000);
});

// ── Util ──────────────────────────────────────────────────────────────────────
function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// expose for dashboard.js
window.openResume = openResume;
