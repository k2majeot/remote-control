@echo off
cd /d "%~dp0"

set PYTHON=venv\Scripts\python.exe

start "" /B %PYTHON% src\http_server.py
%PYTHON% src\remote_server.py
