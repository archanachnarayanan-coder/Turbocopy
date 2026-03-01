@echo off
cd /d "%~dp0"
py turbo_copy.py 2>nul || python turbo_copy.py
if errorlevel 1 pause
