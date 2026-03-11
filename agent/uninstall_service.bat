@echo off
schtasks /end /tn "CommandDeck-Agent" 2>nul
schtasks /delete /tn "CommandDeck-Agent" /f 2>nul
taskkill /f /fi "WINDOWTITLE eq agent*" 2>nul
echo [agent] Uninstalled.
