@echo off
cd /d "%~dp0"

set PYTHON=venv\Scripts\python.exe

%PYTHON% backend\run_servers.py %*
