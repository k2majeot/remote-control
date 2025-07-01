@echo off
cd /d "%~dp0"

set PYTHON=venv\Scripts\python.exe

%PYTHON% src\run_servers.py
