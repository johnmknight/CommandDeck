# PRODUCTION QUEUE — CommandDeck

**Last Updated:** 2026-03-11

## ✅ Recently Completed

- [x] FastAPI backend — projects, tasks, queue, claude status, WebSocket
- [x] SQLite schema — projects, tasks, queue_items, claude_status
- [x] Dashboard — 5 project cards with stats, top task, color per project
- [x] Kanban board — 4-column drag-drop per project
- [x] Message queue panel — bottom-right, live via WebSocket
- [x] DO IT button — pushes task to queue
- [x] UTC clock, Claude status badge
- [x] Resume Session modal — per project, live git context + active tasks
- [x] COPY + OPEN CLAUDE button — one click to start a zero-ramp session
- [x] JohnsSpares project added
- [x] **Option A architecture — relay + agent + services (2026-03-11)**
  - relay/relay.py: FastAPI on devbox:8099, exposes git + file data to appserv1
  - agent/agent.py: Claude agent loop — polls queue, calls Anthropic API, posts responses
  - backend/main.py: resume endpoint wired to relay for live git/file context
  - Windows scheduled task installers for relay + agent (onlogon, hidden window)
  - Committed + pushed to GitHub (commit 72b64c6)

## 🔴 Blocked — User Action Required

- [ ] Set ANTHROPIC_API_KEY as Windows user environment variable
  - System Properties → Advanced → Environment Variables → User variables → New
  - Name: ANTHROPIC_API_KEY  Value: sk-ant-...
  - Then run: services\register_tasks.bat (as Administrator)
  - This registers relay + agent as onlogon scheduled tasks (persistent across reboots)

## 🔜 Up Next

- [ ] Wire claude CLI --print flag for non-interactive execution (optional v2)
- [ ] Agent context builder — inject PRODUCTION_QUEUE.md + OPEN-ISSUES.md per project
- [ ] agent.py error handling + retry logic
- [ ] Dashboard: show queue history (done items)
- [ ] Dashboard: Claude current task display in topbar

## 🗂 Backlog

- [ ] GitHub integration — sync tasks from repo issues
- [ ] Auto-sync PRODUCTION_QUEUE.md on task status change
- [ ] Multi-user / mobile view
- [ ] Notification sounds on queue events
