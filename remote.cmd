@echo off
cd /d "%~dp0"

set PYTHON=venv\Scripts\python.exe

%PYTHON% run_servers.py
