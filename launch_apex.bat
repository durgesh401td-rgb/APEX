@echo off
title APEX Desktop Assistant
cd /d "%~dp0"
echo Starting APEX...
".venv\Scripts\python.exe" run.py
pause
