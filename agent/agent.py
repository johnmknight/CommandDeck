"""
CommandDeck Agent — runs on Windows dev box.
Polls the CommandDeck queue on appserv1, calls Anthropic API, posts responses.

Environment variables (set in System Properties > Environment Variables):
  ANTHROPIC_API_KEY        — required
  COMMANDDECK_URL          — default: http://192.168.4.148:8090
  COMMANDDECK_RELAY_URL    — default: http://192.168.4.47:8099
  AGENT_POLL_INTERVAL      — seconds between polls, default: 10
  AGENT_MODEL              — default: claude-opus-4-5
"""
import time, json, os, sys, logging
from datetime import datetime, timezone
import requests
from anthropic import Anthropic

# ── Config ────────────────────────────────────────────────────────────────────
QUEUE_URL     = os.environ.get("COMMANDDECK_URL",       "http://192.168.4.148:8090")
RELAY_URL     = os.environ.get("COMMANDDECK_RELAY_URL", "http://192.168.4.47:8099")
POLL_INTERVAL = int(os.environ.get("AGENT_POLL_INTERVAL", "10"))
MODEL         = os.environ.get("AGENT_MODEL", "claude-opus-4-5")
LOG_FILE      = os.path.join(os.path.dirname(__file__), "agent.log")

SYSTEM_PROMPT = """You are an autonomous development assistant working on a project.
Produce concrete, actionable output — code, commands, file edits, or analysis.
Be direct and specific. When writing code, include the full relevant file path.
When giving commands, give exact shell commands that can be copy-pasted."""

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("agent")

client = Anthropic()  # reads ANTHROPIC_API_KEY from env


# ── Helpers ───────────────────────────────────────────────────────────────────
def heartbeat(status="idle", task=None, note=None):
    try:
        requests.post(f"{QUEUE_URL}/api/claude/heartbeat", json={
            "status": status,
            "current_task": task,
            "note": note,
        }, timeout=5)
    except Exception as e:
        log.warning(f"Heartbeat failed: {e}")


def get_resume_context(project_id: str) -> str:
    """Fetch the resume prompt from CommandDeck (which now calls relay for git/files)."""
    if not project_id:
        return ""
    try:
        r = requests.get(f"{QUEUE_URL}/api/projects/{project_id}/resume", timeout=15)
        return r.json().get("prompt", "")
    except Exception as e:
        log.warning(f"Resume fetch failed for {project_id}: {e}")
        return ""


def call_claude(context: str, task_text: str) -> str:
    user_msg = task_text
    if context:
        user_msg = f"{context}\n\n---\nTASK: {task_text}"
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return msg.content[0].text


def push_response(project_id: str, task_id, response_text: str):
    requests.post(f"{QUEUE_URL}/api/queue", json={
        "direction": "claude_to_user",
        "project_id": project_id,
        "task_id": task_id,
        "type": "response",
        "payload": {"text": response_text},
    }, timeout=10)


def process_item(item: dict):
    qid        = item["id"]
    project_id = item.get("project_id", "")
    task_id    = item.get("task_id")
    raw        = item.get("payload", "{}")
    payload    = json.loads(raw) if isinstance(raw, str) else raw
    task_text  = payload.get("text") or payload.get("title") or str(payload)

    log.info(f"Processing queue item {qid}: {task_text[:80]}")
    heartbeat("working", task_text[:80])

    context  = get_resume_context(project_id)
    response = call_claude(context, task_text)

    push_response(project_id, task_id, response)
    requests.patch(f"{QUEUE_URL}/api/queue/{qid}", json={"status": "done"}, timeout=5)
    log.info(f"Completed {qid}")
    heartbeat("idle")


# ── Main loop ─────────────────────────────────────────────────────────────────
def run():
    log.info(f"CommandDeck Agent starting")
    log.info(f"  Queue:  {QUEUE_URL}")
    log.info(f"  Relay:  {RELAY_URL}")
    log.info(f"  Model:  {MODEL}")
    log.info(f"  Poll:   {POLL_INTERVAL}s")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.error("ANTHROPIC_API_KEY not set. Exiting.")
        sys.exit(1)

    while True:
        try:
            heartbeat("idle")
            r = requests.get(f"{QUEUE_URL}/api/queue/next", timeout=5)
            item = r.json()
            if item and item.get("id"):
                process_item(item)
            else:
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            log.info("Shutting down.")
            heartbeat("offline")
            break
        except Exception as e:
            log.error(f"Loop error: {e}")
            heartbeat("error", note=str(e)[:120])
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
