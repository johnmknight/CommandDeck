"""
CommandDeck Relay — runs on Windows dev box (192.168.4.47:8099)
Exposes local git + file data to CommandDeck running on appserv1.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import subprocess, os
from pathlib import Path
from datetime import datetime, timezone

app = FastAPI(title="CommandDeck Relay", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

RELAY_PORT = int(os.environ.get("RELAY_PORT", "8099"))


def run_git(repo: str, args: list) -> str:
    try:
        r = subprocess.run(
            ["git"] + args, cwd=repo,
            capture_output=True, text=True, timeout=8
        )
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return f"(git error: {e})"


def read_doc(repo: str, filename: str, maxlines: int = 80) -> str:
    p = Path(repo) / filename
    if not p.exists():
        return "(not found)"
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    out = "\n".join(lines[:maxlines])
    if len(lines) > maxlines:
        out += f"\n... ({len(lines) - maxlines} more lines)"
    return out


@app.get("/health")
def health():
    return {
        "ok": True,
        "host": "devbox",
        "time": datetime.now(timezone.utc).isoformat()
    }


@app.get("/relay/git")
def git_info(repo: str = Query(..., description="Absolute repo path on Windows")):
    if not Path(repo).exists():
        return {"log": "(repo not found)", "status": "", "branch": ""}
    return {
        "log":    run_git(repo, ["log", "--oneline", "-7"]),
        "status": run_git(repo, ["status", "--short"]),
        "branch": run_git(repo, ["branch", "--show-current"]),
    }


@app.get("/relay/file")
def read_file(
    repo: str = Query(...),
    name: str = Query(...),
    maxlines: int = Query(80)
):
    return {"content": read_doc(repo, name, maxlines)}


@app.get("/relay/exists")
def repo_exists(repo: str = Query(...)):
    return {"exists": Path(repo).exists()}
