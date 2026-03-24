# CommandDeck

Unified operations dashboard for SmartLab project management and service orchestration.

## Purpose

CommandDeck serves two primary functions:

1. **Project Management Dashboard** — Track tasks, manage kanban boards, and coordinate development across all SmartLab projects
2. **App Manifest Provider** — Powers SmartLabLauncher by providing dynamic app configuration via REST API

## Architecture

### Local Development
- **Frontend:** Vanilla JavaScript (no build step)
- **Backend:** FastAPI + SQLite
- **Port:** 8090
- **Database:** `backend/commanddeck.db` (SQLite)
- **Start:** `start.bat` (runs uvicorn on port 8090)

### Production Deployment
- **Host:** appserv1 (192.168.4.148)
- **Container:** Docker (built from GitHub via GitHub Actions)
- **Registry:** `ghcr.io/johnmknight/commanddeck:latest`
- **nginx route:** `/deck/` (reverse proxy to port 8090)
- **URL:** `http://192.168.4.148/deck/`

### Database Architecture
The database is **baked into the Docker image** (not volume-mounted).

**To deploy database changes:**
```bash
# 1. Update database locally
# 2. Copy to appserv1
scp backend/commanddeck.db john@192.168.4.148:~/smartlab/commanddeck/backend/

# 3. Copy into running container
ssh john@192.168.4.148
docker cp ~/smartlab/commanddeck/backend/commanddeck.db commanddeck:/app/backend/commanddeck.db

# 4. Restart container
cd ~/smartlab && docker compose restart commanddeck
```

## SmartLabLauncher Integration

CommandDeck provides the app manifest that powers SmartLabLauncher's dynamic button generation.

### API Endpoint: `/api/apps`

Returns deployed apps for the launcher:

```json
{
  "app_server_url": "http://192.168.4.148",
  "apps": [
    {
      "id": "smarttoolbox",
      "code": "STB",
      "name": "SmartToolbox",
      "color": "#1A42CC",
      "port": 8091,
      "route_path": "/toolbox/",
      "glyph_svg": "<svg>...</svg>",
      "bg_js": "initSTB"
    }
  ]
}
```

### Database Schema (Relevant Fields)

```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    short_name TEXT NOT NULL,          -- 3-letter code (STB, CDK, AO, MSO, SLNO)
    name TEXT NOT NULL,                 -- Full app name
    color TEXT NOT NULL,                -- Hex color (#1A42CC)
    port INTEGER,                       -- App port (8091, 8090, etc.)
    is_deployed INTEGER DEFAULT 0,     -- 1 = show in launcher, 0 = hide
    sort_order INTEGER,                 -- Button display order
    route_path TEXT,                    -- nginx route (/toolbox/, /deck/)
    glyph_svg TEXT,                     -- Inline SVG for Cobb glyph
    bg_js TEXT                          -- Three.js background function name
);
```

**Key columns for launcher:**
- `is_deployed = 1` — App appears in launcher
- `sort_order` — Left-to-right button order
- `route_path` — Combined with `app_server_url` to build button link
- `glyph_svg` — Inserted into Cobb octagonal border
- `bg_js` — Three.js initialization function (initSTB, initCDK, etc.)

### Adding New Apps to Launcher

1. Insert project into `projects` table with `is_deployed = 1`
2. Set `route_path` (nginx route), `glyph_svg`, `bg_js`
3. Deploy database changes (see Database Architecture above)
4. Add nginx route to `smartlab-infra/nginx.conf`
5. Launcher auto-loads new button on next page load

See [SmartLabLauncher README](../SmartLabLauncher/README.md) for client-side integration.

## Environment Variables

Configured in `.env`:

```bash
# SmartLab Launcher — production app server base URL
APP_SERVER_URL=http://192.168.4.148

# Relay — Windows dev box for git + file context (optional)
RELAY_URL=http://192.168.4.47:8099
```

## Development

```bash
# Start local server
start.bat

# Access dashboard
http://localhost:8090

# Test /api/apps endpoint
curl http://localhost:8090/api/apps
```

## Repository

- **Local:** `C:\Users\john_\dev\CommandDeck`
- **GitHub:** `https://github.com/johnmknight/CommandDeck` (private)
