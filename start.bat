@echo off
title CommandDeck
cd /d C:\Users\john_\dev\CommandDeck\backend
echo Installing dependencies...
pip install -r requirements.txt -q
echo.
echo Starting CommandDeck on http://localhost:8090
echo.
uvicorn main:app --host 0.0.0.0 --port 8090 --reload
