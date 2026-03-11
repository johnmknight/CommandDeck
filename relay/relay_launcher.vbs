Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\john_\dev\CommandDeck\relay"
WshShell.Run "cmd /c python -m uvicorn relay:app --host 0.0.0.0 --port 8099 >> ""C:\Users\john_\dev\CommandDeck\relay\relay.log"" 2>&1", 0, False
