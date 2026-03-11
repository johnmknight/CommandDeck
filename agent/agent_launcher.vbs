Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\john_\dev\CommandDeck\agent"
WshShell.Run "cmd /c python agent.py >> ""C:\Users\john_\dev\CommandDeck\agent\agent.log"" 2>&1", 0, False
