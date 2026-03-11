@echo off
REM ── CommandDeck Agent — Install as Windows Scheduled Task ─────────────────
REM Registers agent as a logon task (runs at Windows login, hidden window).
REM ANTHROPIC_API_KEY must be set as a System or User environment variable.

SET TASK_NAME=CommandDeck-Agent
SET LAUNCHER=C:\Users\john_\dev\CommandDeck\agent\agent_launcher.vbs

echo [agent] Checking ANTHROPIC_API_KEY...
if "%ANTHROPIC_API_KEY%"=="" (
    echo [agent] WARNING: ANTHROPIC_API_KEY is not set in this session.
    echo [agent] Set it as a User environment variable before the agent will work.
    echo [agent] System Properties ^> Environment Variables ^> User variables ^> New
    echo.
)

echo [agent] Registering scheduled task: %TASK_NAME%
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe \"%LAUNCHER%\"" /sc onlogon /f /rl HIGHEST
if %ERRORLEVEL% NEQ 0 (
    echo [agent] ERROR: Failed to create task. Try running as Administrator.
    pause
    exit /b 1
)

echo [agent] Starting task now...
schtasks /run /tn "%TASK_NAME%"
timeout /t 3 /nobreak >nul

echo [agent] Done. Agent will auto-start at next login.
echo [agent] Log: C:\Users\john_\dev\CommandDeck\agent\agent.log
echo [agent] To stop: schtasks /end /tn "%TASK_NAME%"
echo [agent] To uninstall: agent\uninstall_service.bat
pause
