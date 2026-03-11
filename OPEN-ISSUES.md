# OPEN ISSUES — CommandDeck

**Last Updated:** 2026-03-11

## 🔴 Blocked — User Action Required

- [ ] **ANTHROPIC_API_KEY not set as Windows user env var**
  - Without this, agent.py exits immediately on start
  - Fix: System Properties → Advanced → Environment Variables → User variables → New
    - Name: `ANTHROPIC_API_KEY`
    - Value: your key from https://console.anthropic.com/settings/keys
  - After setting, run `services\register_tasks.bat` as Administrator to install
    relay + agent as onlogon scheduled tasks

## 🐛 Bugs / Known Issues

- [ ] claude --version returns no version string (only deprecation warnings) — cosmetic
- [ ] Claude status badge stays OFFLINE until agent.py sends first heartbeat — by design
- [ ] DO IT buttons hidden until Claude heartbeat < 60s — by design
- [ ] Resume modal shows "(no repo)" / "(not found)" if relay is not running — expected
  - Relay must be live at http://192.168.4.47:8099 for git + file context to populate

## ✅ Resolved This Session (2026-03-11)

- [x] Resume modal "(no repo)" / "(not found)" — root cause identified: appserv1 can't
      access Windows paths. Fixed via Option A relay architecture (relay.py on devbox:8099)
- [x] agent.py — built, committed, and running (pending API key env var)
- [x] relay.py — built, committed, running live at http://192.168.4.47:8099
- [x] Windows scheduled task installers — built (register_tasks.bat, install_service.bat)

## 📐 Design Notes

- Architecture: Option A — CommandDeck on appserv1:8090, relay on devbox:8099
  - appserv1 handles UI + queue + WebSocket
  - devbox relay serves git log, git status, file contents to appserv1 resume endpoint
  - devbox agent polls queue, calls Anthropic API, posts claude_to_user responses
- Queue directions: user_to_claude (DO IT) / claude_to_user (agent replies)
- Relay endpoints: GET /relay/git, GET /relay/file, GET /relay/exists, GET /health
- Agent model: claude-opus-4-5 (override via AGENT_MODEL env var)
- Agent log: C:\Users\john_\dev\CommandDeck\agent\agent.log

## 📋 Session Notes

### 2026-03-11
- Identified relay + agent already built in prior session (uncommitted)
- Committed all: agent/, relay/, services/, Dockerfile, .env.example, updated main.py
- Pushed to GitHub (commit 72b64c6)
- Relay started and verified live: http://localhost:8099/health ✅
- Agent blocked on ANTHROPIC_API_KEY — needs user to set Windows env var

### 2026-03-08
- Added JohnsSpares project (id=johnsspares, JS badge, rose #F43F5E, port 7700)
- Seeded 10 tasks from JohnsSpares PRODUCTION_QUEUE.md

### 2026-03-06
- Added Resume Session feature + smart start.bat + .gitignore
- Stopped before building agent.py

### 2026-03-05
- Built full stack in one session
- claude CLI confirmed at C:\Users\john_\AppData\Local\AnthropicClaude\app-1.1.4498\claude.exe
