# PRODUCTION QUEUE — CommandDeck

**Last Updated:** 2026-03-15

## 🔴 Active / In Progress

_(nothing — session complete)_

## 🟡 Up Next

- [ ] Dashboard: show queue history (done items)
- [ ] Dashboard: Claude current task display in topbar
- [ ] Wire relay health indicator into CommandDeck topbar
- [ ] Register scheduled tasks (needs admin terminal — `services\register_tasks.bat`)

## ✅ Recently Completed

- [x] FastAPI backend — projects, tasks, queue, claude status, WebSocket
- [x] SQLite schema — projects, tasks, queue_items, claude_status
- [x] Seed data from all 5 project PRODUCTION_QUEUE.md / OPEN-ISSUES.md
- [x] Dashboard — 5 project cards with stats, top task, color per project
- [x] Kanban board — 4-column drag-drop per project
- [x] Message queue panel — bottom-right, live via WebSocket
- [x] ▶ DO IT button — pushes task to queue
- [x] UTC clock, Claude status badge
- [x] Resume Session modal — per project, full git context + tasks + docs
- [x] COPY + OPEN CLAUDE button — one click to start a zero-ramp session
- [x] Smart start.bat — skips pip install if deps already present
- [x] JohnsSpares project added
- [x] Option A architecture: relay.py on Windows devbox (192.168.4.47:8099)
- [x] agent.py — full Claude API polling loop
- [x] relay.py — running live, health endpoint confirmed
- [x] SQLite busy_timeout + WAL mode — fixed db lock contention
- [x] requests added to Docker requirements
- [x] ANTHROPIC_API_KEY set as Windows User env var
- [x] Auto-start: relay + agent shortcuts in Windows Startup folder
- [x] End-to-end test PASSED — DO IT → agent picks up → API call → response posted
- [x] All committed and pushed to GitHub

## 🗂 Backlog

- [ ] GitHub integration — sync tasks from repo issues
- [ ] Auto-sync PRODUCTION_QUEUE.md on task status change
- [ ] Multi-user / mobile view
- [ ] Notification sounds on queue events
