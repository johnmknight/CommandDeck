@echo off
schtasks /end /tn "CommandDeck-Relay" 2>nul
schtasks /delete /tn "CommandDeck-Relay" /f 2>nul
taskkill /f /im uvicorn.exe 2>nul
echo [relay] Uninstalled.
