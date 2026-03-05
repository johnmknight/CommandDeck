# OPEN ISSUES — CommandDeck

**Last Updated:** 2026-03-05

## 🐛 Bugs / Known Issues

- [ ] claude --version returns no version number (just deprecation warnings) — cosmetic
- [ ] Claude status badge stays OFFLINE until agent.py sends first heartbeat — by design, not a bug

## 🔄 Not Yet Built

- [ ] agent.py — the entire Claude ↔ queue loop. Next session priority.
- [ ] claude CLI --print / non-interactive mode — needs testing before agent.py

## 💡 Design Notes

- Queue direction: user_to_claude (DO IT button) / claude_to_user (agent replies) — both exist in schema, only user_to_claude used so far
- DO IT buttons only light up when Claude heartbeat < 60s — correct behavior
- Drag-drop reorder updates priority + status atomically via /api/tasks/reorder

## 📝 Session Notes

### 2026-03-05
- Built full stack in one session
- claude CLI confirmed installed at C:\Users\john_\AppData\Local\AnthropicClaude\app-1.1.4498\claude.exe
- Stopped before building agent.py — next session starts here
