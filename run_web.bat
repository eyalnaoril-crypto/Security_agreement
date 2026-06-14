@echo off
chcp 65001 >nul
cd /d "%~dp0"
title G1 Legal AI - Web UI

echo.
echo ========================================
echo   G1 Legal AI - Web UI
echo ========================================
echo.
echo   Starting server on http://127.0.0.1:5000
echo.

start "" "http://127.0.0.1:5000"

python web\app.py

echo.
echo Server stopped.
pause
