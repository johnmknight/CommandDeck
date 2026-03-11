@echo off
:: CommandDeck Windows Services Installer
:: Installs CommandDeckRelay (port 8099) and CommandDeckAgent as Windows services via NSSM
:: Run as Administrator

title CommandDeck Service Installer
echo.
echo  +--------------------------------------------------+
echo  ^|  CommandDeck Service Installer                   ^|
echo  ^|  Relay: port 8099   Agent: polling loop          ^|
echo  +--------------------------------------------------+
echo.

:: Check for admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Run this script as Administrator.
    pause
    exit /b 1
)

:: Locate NSSM
where nssm >nul 2>&1
if %errorlevel% neq 0 (
    echo  NSSM not found. Installing via winget...
    winget install nssm --silent --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo  ERROR: Could not install NSSM. Install manually from https://nssm.cc
        pause
        exit /b 1
    )
    echo  NSSM installed.
)

set PYTHON=C:\Users\john_\AppData\Local\Microsoft\WindowsApps\python.exe
set CD_ROOT=C:\Users\john_\dev\CommandDeck
set LOG_DIR=%CD_ROOT%\logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: ── Relay Service ──────────────────────────────────────────────────────────
echo  Installing CommandDeckRelay...
nssm stop  CommandDeckRelay >nul 2>&1
nssm remove CommandDeckRelay confirm >nul 2>&1

nssm install CommandDeckRelay "%PYTHON%"
nssm set CommandDeckRelay AppParameters "-m uvicorn relay:app --host 0.0.0.0 --port 8099"
nssm set CommandDeckRelay AppDirectory "%CD_ROOT%\relay"
nssm set CommandDeckRelay DisplayName "CommandDeck Relay"
nssm set CommandDeckRelay Description "Serves git + file context from Windows repos to CommandDeck on appserv1"
nssm set CommandDeckRelay Start SERVICE_AUTO_START
nssm set CommandDeckRelay AppStdout "%LOG_DIR%\relay.log"
nssm set CommandDeckRelay AppStderr "%LOG_DIR%\relay-err.log"
nssm set CommandDeckRelay AppRotateFiles 1
nssm set CommandDeckRelay AppRotateSeconds 86400

:: ── Agent Service ──────────────────────────────────────────────────────────
echo  Installing CommandDeckAgent...
nssm stop  CommandDeckAgent >nul 2>&1
nssm remove CommandDeckAgent confirm >nul 2>&1

nssm install CommandDeckAgent "%PYTHON%"
nssm set CommandDeckAgent AppParameters "%CD_ROOT%\agent\agent.py"
nssm set CommandDeckAgent AppDirectory "%CD_ROOT%\agent"
nssm set CommandDeckAgent DisplayName "CommandDeck Agent"
nssm set CommandDeckAgent Description "Polls CommandDeck queue and calls Anthropic API for task automation"
nssm set CommandDeckAgent Start SERVICE_AUTO_START
nssm set CommandDeckAgent AppStdout "%LOG_DIR%\agent.log"
nssm set CommandDeckAgent AppStderr "%LOG_DIR%\agent-err.log"
nssm set CommandDeckAgent AppRotateFiles 1
nssm set CommandDeckAgent AppRotateSeconds 86400

:: ── Start Both ─────────────────────────────────────────────────────────────
echo  Starting services...
nssm start CommandDeckRelay
nssm start CommandDeckAgent

echo.
echo  Done. Check status with:
echo    nssm status CommandDeckRelay
echo    nssm status CommandDeckAgent
echo.
echo  Logs: %LOG_DIR%
echo.
pause
