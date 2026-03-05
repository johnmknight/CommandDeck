@echo off
title CommandDeck
cls
echo.
echo  ^+------------------------------------------^+
echo  ^|   COMMANDDECK  ^|  OPS DASHBOARD v1.0     ^|
echo  ^+------------------------------------------^+
echo.

cd /d C:\Users\john_\dev\CommandDeck\backend

:: Only install if fastapi not present
python -c "import fastapi" 2>nul || (
    echo  Installing dependencies...
    pip install -r requirements.txt -q
    echo  Done.
    echo.
)

echo  Starting on http://localhost:8090
echo  Press Ctrl+C to stop.
echo.

uvicorn main:app --host 0.0.0.0 --port 8090 --reload
