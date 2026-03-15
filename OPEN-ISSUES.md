# OPEN ISSUES — CommandDeck

**Last Updated:** 2026-03-15

## 🔴 Blocked — User Action Required

- [ ] **Scheduled tasks not registered via Task Scheduler**
  - `services\register_tasks.bat` requires an admin terminal to register
  - Workaround in place: relay + agent shortcuts in Windows Startup folder
  - If Startup folder approach is insufficient, run bat as Administrator

## 🐛 Bugs / Known Issues

- [ ] claude --version returns no version string (only deprecation warnings) — cosmetic
- [ ] Claude status badge stays OFFLINE until agent.py sends first heartbeat — by design
- [ ] DO IT buttons hidden until Claude heartbeat < 60s — by design
- [ ] Agent date awareness — replies use training date, not real UTC (cosmetic)

## ✅ Resolved This Session (2026-03-11)

- [x] ANTHROPIC_API_KEY not set — fixed, set as Windows User env var
- [x] database is locked (SQLite) — fixed via busy_timeout=10 + PRAGMA busy_timeout=10000
- [x] requests module missing in Docker image — added to backend/requirements.txt
- [x] Relay + agent not auto-starting — fixed via Windows Startup folder shortcuts
- [x] End-to-end pipeline — confirmed working: push → agent picks up → API → response

## 📐 Architecture Notes

- CommandDeck UI + queue: appserv1 (192.168.4.148:8090) — Docker container
- Relay: devbox (192.168.4.47:8099) — serves git/file context to resume endpoint
- Agent: devbox — polls queue, calls Anthropic API, posts claude_to_user responses
- Auto-start: C:\Users\john_\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
  - CommandDeck-Relay.lnk → relay_launcher.vbs
  - CommandDeck-Agent.lnk → agent_launcher.vbs
- Agent model: claude-opus-4-5 (override via AGENT_MODEL env var)
- Agent log: C:\Users\john_\dev\CommandDeck\agent\agent.log

## 📋 Session Notes

### 2026-03-15
- Relay and agent were both down (not running since last reboot)
- Root cause: VBS Startup folder launchers depend on User env vars loaded at login
- Desktop Commander shell doesn't inherit User env vars — ANTHROPIC_API_KEY missing
- Manually started relay (localhost:8099 ✅) and agent (heartbeat confirmed idle ✅)
- Full pipeline restored: DO IT → agent → Claude API → response
- No code changes to CommandDeck this session — operational restart only

### 2026-03-11 (evening)
- Set ANTHROPIC_API_KEY as Windows User env var
- Discovered relay + agent scheduled tasks not registered (register_tasks.bat needs admin)
- Fixed SQLite db lock — added busy_timeout to connect() + PRAGMA busy_timeout
- Added requests to backend/requirements.txt; rebuilt Docker image on appserv1
- Created Startup folder shortcuts for relay + agent auto-start (no admin required)
- Ran end-to-end test: pushed queue item, agent processed it, response confirmed in queue
- Committed fixes (5cd3820), pushed to GitHub

### 2026-03-11 (afternoon)
- Identified relay + agent already built in prior session (uncommitted)
- Committed all: agent/, relay/, services/, Dockerfile, .env.example, updated main.py
- Pushed to GitHub (commit 72b64c6)
- Relay started and verified live: http://localhost:8099/health ✅
- Agent blocked on ANTHROPIC_API_KEY — resolved this session

### 2026-03-08
- Added JohnsSpares project (id=johnsspares, JS badge, rose #F43F5E, port 7700)
- Seeded 10 tasks from JohnsSpares PRODUCTION_QUEUE.md

### 2026-03-06
- Added Resume Session feature + smart start.bat + .gitignore

### 2026-03-05
- Built full stack in one session
- claude CLI confirmed at C:\Users\john_\AppData\Local\AnthropicClaude\app-1.1.4498\claude.exe
