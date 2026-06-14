@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo === G1 Legal AI - Web UI ===
echo.
python web\app.py
pause
