from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, json, os, uuid, subprocess, requests as req_lib
from datetime import datetime, timezone
from pathlib import Path

# Relay: Windows dev box serves git + file context (Option A architecture)
RELAY_URL = os.environ.get("RELAY_URL", "")  # e.g. http://192.168.4.47:8099

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "commanddeck.db")
FRONT    = os.path.join(BASE_DIR, "..", "frontend")

app = FastAPI(title="CommandDeck", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=FRONT), name="static")

# ── DB ────────────────────────────────────────────────────────────────────────
def db():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=10000")
    c.execute("PRAGMA foreign_keys=ON")
    return c

def r2d(row): return dict(row) if row else None
def now():    return datetime.now(timezone.utc).isoformat()

def init_db():
    conn = db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, short_name TEXT NOT NULL,
            description TEXT, color TEXT NOT NULL, repo_path TEXT,
            port INTEGER, github_url TEXT, created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
            title TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'backlog',
            priority INTEGER NOT NULL DEFAULT 0, category TEXT,
            automatable INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS queue_items (
            id TEXT PRIMARY KEY,
            direction TEXT NOT NULL DEFAULT 'user_to_claude',
            project_id TEXT REFERENCES projects(id),
            task_id TEXT REFERENCES tasks(id),
            type TEXT NOT NULL DEFAULT 'task',
            payload TEXT NOT NULL DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS claude_status (
            id INTEGER PRIMARY KEY DEFAULT 1, status TEXT NOT NULL DEFAULT 'offline',
            current_task TEXT, last_heartbeat TEXT, note TEXT
        );
        INSERT OR IGNORE INTO claude_status (id, status) VALUES (1, 'offline');
    """)
    conn.commit()
    if r2d(conn.execute("SELECT COUNT(*) n FROM projects").fetchone())["n"] == 0:
        seed(conn)
    conn.close()

def seed(conn):
    c = conn.cursor()
    c.executemany("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,datetime('now'))", [
        ("artemisops","ArtemisOps","AO","NASA mission control — ISS tracking, Artemis countdown, kiosk","#F97316",r"C:\Users\john_\dev\ArtemisOps",8085,"https://github.com/johnmknight/ArtemisOps"),
        ("marchog","MarchogSystemsOps","MSO","Star Wars themed multi-screen display control system","#EAB308",r"C:\Users\john_\dev\MarchogSystemsOps",8082,""),
        ("captainmurphys","CaptainMurphys","CM","Themed home office 3D room planner","#A855F7",r"C:\Users\john_\dev\CaptainMurphys",8081,""),
        ("findajob","FindAJob","FAJ","Career ops — job scraping, contact intel, application tracking","#0EA5E9",r"C:\Users\john_\dev\FindAJob",8100,""),
        ("smartlablauncher","SmartLabLauncher","SLL","Cinematic 2001-style app launcher for all SmartLab production services","#64748B",r"C:\Users\john_\dev\SmartLabLauncher",80,"https://github.com/johnmknight/smartlab-launcher"),
        ("tikibar","TikiBarOnTheMoon","TBM","Sci-fi novel — The First Tiki Bar on the Moon","#10B981",r"C:\Users\john_\dev\TikiBarOnTheMoon",None,"https://github.com/johnmknight/TikiBarOnTheMoon"),
    ])
    c.executemany("INSERT INTO tasks (id,project_id,title,status,priority,category,automatable) VALUES (?,?,?,?,?,?,?)", [
        # ArtemisOps
        ("ao-1","artemisops","Fix Mission page border — ao-frame-page corners not rendering","active",1,"Bug",0),
        ("ao-2","artemisops","Maximize countdown clock on Mission page per design intent","active",2,"UI/UX",0),
        ("ao-3","artemisops","Add video feeds back to ISS tracking page","active",3,"Feature",0),
        ("ao-4","artemisops","Sci-fi frames around panels — beveled/angled borders, corner accents","active",4,"UI/UX",0),
        ("ao-5","artemisops","Implement full theming system — switchable palettes, fonts, border styles","active",5,"Feature",0),
        ("ao-6","artemisops","Control page: Data/API tab — API calls, timestamps, polling intervals","next",1,"Feature",0),
        ("ao-7","artemisops","Phase 6: Mobile UI Mode — bottom nav, swipe, touch-optimized","next",2,"Phase",0),
        ("ao-8","artemisops","Phase 7: Offline Support / PWA — service worker, IndexedDB","next",3,"Phase",0),
        ("ao-9","artemisops","Raspberry Pi kiosk deployment guide","backlog",1,"Ops",1),
        # MarchogSystemsOps
        ("mso-1","marchog","Local/network video playback — MP4/WebM URLs, USB-mounted media","active",1,"Feature",0),
        ("mso-2","marchog","Data integration: News ticker page (incoming transmissions style)","active",2,"Feature",0),
        ("mso-3","marchog","Page parameter presets — save named configs for parameterized pages","active",3,"Feature",0),
        ("mso-4","marchog","Fix clock digits wiggling — fixed-width spans per digit","active",4,"Bug",1),
        ("mso-5","marchog","Phase 6: ESP32 virtual device simulator — Python MQTT proxy","next",1,"Phase",0),
        ("mso-6","marchog","Scene scheduling — cron-like time-based scene switching","next",2,"Phase",0),
        ("mso-7","marchog","Mobile-optimized config panel — responsive redesign","next",3,"Phase",0),
        ("mso-8","marchog","Docker Compose one-command deployment","backlog",1,"Ops",1),
        ("mso-9","marchog","Geo data regionalization — break monolithic GeoJSON into regional files","backlog",2,"Perf",1),
        # CaptainMurphys
        ("cm-1","captainmurphys","3D room planner core — Three.js scene with drag/drop furniture","active",1,"Feature",0),
        ("cm-2","captainmurphys","Furniture library — themed props catalog with 3D models","active",2,"Content",0),
        ("cm-3","captainmurphys","Save/load room layouts to SQLite","next",1,"Feature",0),
        ("cm-4","captainmurphys","Theme preset library — StarWars, TikiBar, NasaMissionControl","next",2,"Feature",0),
        ("cm-5","captainmurphys","Export room as image or shareable link","backlog",1,"Feature",0),
        # FindAJob
        ("faj-1","findajob","Disney Imagineer / Creative Technologist job scraper","active",1,"Scraper",1),
        ("faj-2","findajob","Themed entertainment companies contact intelligence module","active",2,"Feature",0),
        ("faj-3","findajob","Application tracking — status pipeline (applied/screening/interview/offer)","next",1,"Feature",0),
        ("faj-4","findajob","LinkedIn optimization suggestions based on target roles","next",2,"Feature",1),
        ("faj-5","findajob","Weekly digest email — new matching positions","backlog",1,"Feature",1),
        # TikiBarOnTheMoon
        ("tbm-1","tikibar","Review Ch6-10 cuts — identify what needs to be added back","active",1,"Revision",0),
        ("tbm-2","tikibar","A-Pass: Brendan voice consistency throughout Ch1-10","active",2,"Revision",1),
        ("tbm-3","tikibar","A-Pass: Secondary character development pass","active",3,"Revision",1),
        ("tbm-4","tikibar","A-Pass: Tiki detail layer (drinks, atmosphere, culture)","next",1,"Revision",1),
        ("tbm-5","tikibar","Outline Ch11+ story beats","next",2,"Draft",0),
        ("tbm-6","tikibar","Research: Lunar gravity effects on liquids/bartending","next",3,"Research",1),
        ("tbm-7","tikibar","Fix Ch7 pacing — bridge scenes needed after revision cuts","backlog",1,"Bug",0),
        ("tbm-8","tikibar","Fix Ch9 Brendan motivation — restore context after trimming","backlog",2,"Bug",0),
        ("tbm-9","tikibar","World-building doc: Moon colony social structure","backlog",3,"Research",1),
    ])
    conn.commit()

# ── WebSocket Manager ─────────────────────────────────────────────────────────
class WS:
    def __init__(self): self.conns: list[WebSocket] = []
    async def connect(self, ws):
        await ws.accept(); self.conns.append(ws)
    def disconnect(self, ws):
        if ws in self.conns: self.conns.remove(ws)
    async def broadcast(self, data):
        msg = json.dumps(data)
        dead = []
        for ws in self.conns:
            try: await ws.send_text(msg)
            except: dead.append(ws)
        for ws in dead: self.disconnect(ws)

ws_mgr = WS()

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
async def root(): return FileResponse(os.path.join(FRONT, "index.html"))

@app.get("/project/{pid}")
async def proj_page(pid: str): return FileResponse(os.path.join(FRONT, "project.html"))

@app.get("/api/projects")
async def get_projects():
    conn = db()
    rows = [r2d(r) for r in conn.execute("SELECT * FROM projects ORDER BY name").fetchall()]
    for p in rows:
        s = r2d(conn.execute("""SELECT COUNT(*) total,
            SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) active,
            SUM(CASE WHEN status='next' THEN 1 ELSE 0 END) next_up,
            SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) done,
            SUM(CASE WHEN automatable=1 AND status!='done' THEN 1 ELSE 0 END) automatable
            FROM tasks WHERE project_id=?""", (p["id"],)).fetchone())
        p["stats"] = s
        p["top_task"] = r2d(conn.execute(
            "SELECT title FROM tasks WHERE project_id=? AND status='active' ORDER BY priority LIMIT 1", (p["id"],)).fetchone())
    conn.close(); return rows

@app.get("/api/projects/{pid}")
async def get_project(pid: str):
    conn = db()
    p = r2d(conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone())
    conn.close()
    if not p: raise HTTPException(404)
    return p

@app.get("/api/projects/{pid}/tasks")
async def get_tasks(pid: str):
    conn = db()
    rows = [r2d(r) for r in conn.execute(
        "SELECT * FROM tasks WHERE project_id=? ORDER BY CASE status WHEN 'active' THEN 0 WHEN 'next' THEN 1 WHEN 'backlog' THEN 2 ELSE 3 END, priority",
        (pid,)).fetchall()]
    conn.close(); return rows

@app.patch("/api/tasks/{tid}")
async def update_task(tid: str, req: Request):
    data = await req.json()
    conn = db()
    fields = []
    vals = []
    for k in ("status","priority","title","category","automatable"):
        if k in data:
            fields.append(f"{k}=?")
            vals.append(data[k])
    if not fields:
        conn.close(); raise HTTPException(400, "no fields")
    vals += [now(), tid]
    conn.execute(f"UPDATE tasks SET {','.join(fields)}, updated_at=? WHERE id=?", vals)
    conn.commit()
    row = r2d(conn.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone())
    conn.close()
    await ws_mgr.broadcast({"type":"task_updated","task":row})
    return row

@app.post("/api/tasks")
async def create_task(req: Request):
    data = await req.json()
    tid = "t-" + uuid.uuid4().hex[:8]
    conn = db()
    conn.execute(
        "INSERT INTO tasks (id,project_id,title,status,priority,category,automatable) VALUES (?,?,?,?,?,?,?)",
        (tid, data["project_id"], data["title"], data.get("status","backlog"),
         data.get("priority",99), data.get("category",""), data.get("automatable",0)))
    conn.commit()
    row = r2d(conn.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone())
    conn.close()
    await ws_mgr.broadcast({"type":"task_created","task":row})
    return row

@app.post("/api/tasks/reorder")
async def reorder_tasks(req: Request):
    data = await req.json()  # [{id, priority, status}, ...]
    conn = db()
    for item in data:
        conn.execute("UPDATE tasks SET priority=?, status=?, updated_at=? WHERE id=?",
                     (item["priority"], item["status"], now(), item["id"]))
    conn.commit(); conn.close()
    await ws_mgr.broadcast({"type":"tasks_reordered","project_id":data[0].get("project_id") if data else None})
    return {"ok": True}

# ── Message Queue ─────────────────────────────────────────────────────────────
@app.get("/api/queue")
async def get_queue(status: str = "pending"):
    conn = db()
    rows = [r2d(r) for r in conn.execute(
        "SELECT * FROM queue_items WHERE status=? ORDER BY created_at", (status,)).fetchall()]
    conn.close(); return rows

@app.post("/api/queue")
async def push_queue(req: Request):
    data = await req.json()
    qid = "q-" + uuid.uuid4().hex[:8]
    conn = db()
    conn.execute(
        "INSERT INTO queue_items (id,direction,project_id,task_id,type,payload,status) VALUES (?,?,?,?,?,?,?)",
        (qid, data.get("direction","user_to_claude"), data.get("project_id"),
         data.get("task_id"), data.get("type","task"),
         json.dumps(data.get("payload",{})), "pending"))
    conn.commit()
    row = r2d(conn.execute("SELECT * FROM queue_items WHERE id=?", (qid,)).fetchone())
    conn.close()
    await ws_mgr.broadcast({"type":"queue_push","item":row})
    return row

@app.get("/api/queue/next")
async def queue_next():
    conn = db()
    row = r2d(conn.execute(
        "SELECT * FROM queue_items WHERE status='pending' AND direction='user_to_claude' ORDER BY created_at LIMIT 1"
    ).fetchone())
    if row:
        conn.execute("UPDATE queue_items SET status='in_progress', updated_at=? WHERE id=?", (now(), row["id"]))
        conn.commit()
        row["status"] = "in_progress"
    conn.close()
    await ws_mgr.broadcast({"type":"queue_next","item":row})
    return row or {}

@app.patch("/api/queue/{qid}")
async def update_queue(qid: str, req: Request):
    data = await req.json()
    conn = db()
    conn.execute("UPDATE queue_items SET status=?, updated_at=? WHERE id=?",
                 (data.get("status","done"), now(), qid))
    conn.commit()
    row = r2d(conn.execute("SELECT * FROM queue_items WHERE id=?", (qid,)).fetchone())
    conn.close()
    await ws_mgr.broadcast({"type":"queue_update","item":row})
    return row

# ── Claude Status ─────────────────────────────────────────────────────────────
@app.get("/api/claude/status")
async def get_claude_status():
    conn = db()
    row = r2d(conn.execute("SELECT * FROM claude_status WHERE id=1").fetchone())
    conn.close(); return row

@app.post("/api/claude/heartbeat")
async def claude_heartbeat(req: Request):
    data = await req.json()
    conn = db()
    conn.execute("UPDATE claude_status SET status=?, current_task=?, last_heartbeat=?, note=? WHERE id=1",
                 (data.get("status","idle"), data.get("current_task"),
                  now(), data.get("note")))
    conn.commit(); conn.close()
    await ws_mgr.broadcast({"type":"claude_status","status":data.get("status","idle"),
                             "note":data.get("note"), "last_heartbeat":now()})
    return {"ok": True}

# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_mgr.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        ws_mgr.disconnect(ws)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup(): init_db()

# ── Resume Session Endpoint ───────────────────────────────────────────────────
def run_git(repo: str, args: list) -> str:
    try:
        r = subprocess.run(
            ["git"] + args, cwd=repo,
            capture_output=True, text=True, timeout=8
        )
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return f"(git error: {e})"

def read_doc(repo: str, filename: str, maxlines: int = 60) -> str:
    p = Path(repo) / filename
    if not p.exists():
        return "(not found)"
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    out = "\n".join(lines[:maxlines])
    if len(lines) > maxlines:
        out += f"\n... ({len(lines) - maxlines} more lines)"
    return out

@app.get("/api/projects/{pid}/resume")
async def resume_session(pid: str):
    conn = db()
    proj = r2d(conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone())
    tasks = [r2d(r) for r in conn.execute(
        "SELECT * FROM tasks WHERE project_id=? AND status IN ('active','next') ORDER BY status, priority",
        (pid,)).fetchall()]
    issues_raw = [r2d(r) for r in conn.execute(
        "SELECT * FROM tasks WHERE project_id=? AND status='backlog' ORDER BY priority LIMIT 5",
        (pid,)).fetchall()]
    conn.close()

    if not proj:
        raise HTTPException(404)

    repo = proj.get("repo_path", "")

    # Try relay first (Option A: Windows dev box has the repos)
    relay_ctx = None
    if RELAY_URL and repo:
        try:
            r = req_lib.post(f"{RELAY_URL}/relay/resume", json={"repo_path": repo}, timeout=5)
            if r.status_code == 200:
                relay_ctx = r.json()
        except Exception:
            pass  # fall through to local

    if relay_ctx:
        git_log    = relay_ctx.get("git_log", "(relay error)")
        git_status = relay_ctx.get("git_status", "(relay error)")
        git_branch = relay_ctx.get("git_branch", "main")
        pq         = relay_ctx.get("pq", "(not found)")
        oi         = relay_ctx.get("oi", "(not found)")
    else:
        has_repo = repo and Path(repo).exists()
        git_log    = run_git(repo, ["log", "--oneline", "-7"]) if has_repo else "(no repo)"
        git_status = run_git(repo, ["status", "--short"])      if has_repo else "(no repo)"
        git_branch = run_git(repo, ["branch", "--show-current"]) if has_repo else ""
        pq   = read_doc(repo, "PRODUCTION_QUEUE.md", 80)
        oi   = read_doc(repo, "OPEN-ISSUES.md", 60)

    # build active task list
    active_lines = []
    for i, t in enumerate([x for x in tasks if x["status"] == "active"], 1):
        auto = " ⚡" if t["automatable"] else ""
        cat  = f" [{t['category']}]" if t.get("category") else ""
        active_lines.append(f"  {i}. {t['title']}{cat}{auto}")

    next_lines = []
    for i, t in enumerate([x for x in tasks if x["status"] == "next"], 1):
        cat = f" [{t['category']}]" if t.get("category") else ""
        next_lines.append(f"  {i}. {t['title']}{cat}")

    port_str = f", port {proj['port']}" if proj.get("port") else ""
    github_str = f"\nGitHub: {proj['github_url']}" if proj.get("github_url") else ""
    branch_str = f" ({git_branch})" if git_branch else ""

    prompt = f"""We're resuming work on **{proj['name']}**.

PROJECT
  Repo: {repo}{port_str}{github_str}
  Branch: {git_branch or 'main'}{branch_str}

RECENT COMMITS
{git_log}

GIT STATUS
{git_status if git_status else '(clean)'}

ACTIVE TASKS
{chr(10).join(active_lines) if active_lines else '  (none)'}

UP NEXT
{chr(10).join(next_lines) if next_lines else '  (none)'}

PRODUCTION QUEUE (summary)
{pq}

OPEN ISSUES
{oi}

---
Load the project context and pick up where we left off. Start by reviewing the active tasks and git status above, then ask me which to tackle first or suggest the highest-leverage move.
"""

    return {
        "project": proj,
        "prompt": prompt.strip(),
        "git_log": git_log,
        "git_status": git_status,
        "active_count": len([t for t in tasks if t["status"] == "active"]),
        "next_count": len([t for t in tasks if t["status"] == "next"]),
    }
