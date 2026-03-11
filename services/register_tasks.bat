@echo off
schtasks.exe /create /tn "CommandDeck-Relay" /tr "wscript.exe \"C:\Users\john_\dev\CommandDeck\relay\relay_launcher.vbs\"" /sc ONLOGON /f /rl HIGHEST
schtasks.exe /create /tn "CommandDeck-Agent" /tr "wscript.exe \"C:\Users\john_\dev\CommandDeck\agent\agent_launcher.vbs\"" /sc ONLOGON /f /rl HIGHEST
echo Tasks registered.
schtasks.exe /run /tn "CommandDeck-Relay"
timeout /t 3 /nobreak >nul
schtasks.exe /run /tn "CommandDeck-Agent"
echo Done.
