# OPEN ISSUES — CommandDeck

**Last Updated:** 2026-03-08

## 🐛 Bugs / Known Issues

- [ ] claude --version returns no version string (only deprecation warnings) — cosmetic, no impact
- [ ] Claude status badge stays OFFLINE until agent.py sends first heartbeat — by design
- [ ] DO IT buttons hidden until Claude heartbeat < 60s — by design

## 🔄 Not Yet Built

- [ ] agent.py — the entire Claude ↔ queue loop. Next session priority #1.
- [ ] claude CLI non-interactive mode — needs --print flag testing before agent.py

## 💡 Design Notes

- Queue directions: user_to_claude (DO IT button) / claude_to_user (agent replies)
  Both exist in schema; only user_to_claude used so far.
- Drag-drop reorder updates priority + status atomically via POST /api/tasks/reorder
- Resume modal pulls live git log + status from repo path stored in projects table
- COPY + OPEN CLAUDE opens https://claude.ai/new — user pastes prompt, zero ramp-up
- Projects table schema: id, name, short_name, description, color, repo_path, port,
  github_url, created_at, host

## 📝 Session Notes

### 2026-03-08
- Added JohnsSpares project to dashboard (id=johnsspares, JS badge, rose #F43F5E, port 7700)
- Seeded 10 tasks from JohnsSpares PRODUCTION_QUEUE.md:
  - 3 active (porthole bar bug, endcap symmetry, shading band)
  - 2 next (KSP test, IVA stub)
  - 5 backlog (normal map, logo art, triangulate, MM patch, hab_250_30l)
- JohnsSpares card live on dashboard showing 3/2/10/0 stats

### 2026-03-06
- Added Resume Session feature — modal with live git context, active tasks, docs
- Added smart start.bat — skips pip install if fastapi already present
- Added .gitignore — excludes db and __pycache__
- Committed all changes to master branch
- Stopped before building agent.py — next session starts here

### 2026-03-05
- Built full stack in one session
- claude CLI confirmed at C:\Users\john_\AppData\Local\AnthropicClaude\app-1.1.4498\claude.exe
