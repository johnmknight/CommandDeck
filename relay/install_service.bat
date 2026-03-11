@echo off
REM ── CommandDeck Relay — Install as Windows Scheduled Task ──────────────────
REM Registers relay as a logon task (runs at Windows login, hidden window).
REM Re-run this script to update the task after changing settings.

SET TASK_NAME=CommandDeck-Relay
SET LAUNCHER=C:\Users\john_\dev\CommandDeck\relay\relay_launcher.vbs

echo [relay] Registering scheduled task: %TASK_NAME%
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe \"%LAUNCHER%\"" /sc onlogon /f /rl HIGHEST
if %ERRORLEVEL% NEQ 0 (
    echo [relay] ERROR: Failed to create task. Try running as Administrator.
    pause
    exit /b 1
)

echo [relay] Starting task now...
schtasks /run /tn "%TASK_NAME%"
timeout /t 2 /nobreak >nul

echo [relay] Verifying...
curl -s http://localhost:8099/health
echo.
echo [relay] Done. Relay will auto-start at next login.
echo [relay] Log: C:\Users\john_\dev\CommandDeck\relay\relay.log
echo [relay] To stop: schtasks /end /tn "%TASK_NAME%"
echo [relay] To uninstall: relay\uninstall_service.bat
pause
