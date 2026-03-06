# PRODUCTION QUEUE — CommandDeck

**Last Updated:** 2026-03-06

## 🔥 Active / In Progress

- [ ] Build agent.py — Claude Code polling loop
  - Polls GET /api/queue/next every N seconds
  - Shells out to claude CLI with task context + repo path
  - Posts heartbeat to /api/claude/heartbeat
  - Updates queue item status on completion
  - claude CLI at: C:\Users\john_\AppData\Local\AnthropicClaude\app-1.1.4498\claude.exe

## 📋 Up Next

- [ ] Wire claude CLI --print flag for non-interactive execution
- [ ] Agent context builder — inject PRODUCTION_QUEUE.md + OPEN-ISSUES.md per project
- [ ] agent.py error handling + retry logic
- [ ] Dashboard: show queue history (done items)
- [ ] Dashboard: Claude current task display in topbar

## ✅ Recently Completed

- [x] FastAPI backend — projects, tasks, queue, claude status, WebSocket
- [x] SQLite schema — projects, tasks, queue_items, claude_status
- [x] Seed data from all 5 project PRODUCTION_QUEUE.md / OPEN-ISSUES.md
- [x] Dashboard — 5 project cards with stats, top task, color per project
- [x] Kanban board — 4-column drag-drop per project
- [x] Message queue panel — bottom-right, live via WebSocket
- [x] ⚡ DO IT button — pushes task to queue (activates when Claude online)
- [x] UTC clock, Claude status badge
- [x] Resume Session modal — per project, builds context prompt from live git log,
      git status, active tasks, PRODUCTION_QUEUE.md, OPEN-ISSUES.md
- [x] COPY + OPEN CLAUDE button — one click to start a zero-ramp session
- [x] Smart start.bat — skips pip install if deps already present
- [x] .gitignore — excludes db and __pycache__

## 📌 Backlog

- [ ] GitHub integration — sync tasks from repo issues
- [ ] Auto-sync PRODUCTION_QUEUE.md on task status change
- [ ] Multi-user / mobile view
- [ ] Notification sounds on queue events
