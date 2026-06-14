@echo off
chcp 65001 >nul
cd /d "%~dp0"
title G1 Legal AI - Web UI

echo.
echo ========================================
echo   G1 Legal AI - Web UI
echo ========================================
echo.

REM ── Locate a real Python (skip Windows Store stubs) ──
set "PYEXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYEXE if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PYEXE where py >nul 2>&1 && set "PYEXE=py"
if not defined PYEXE set "PYEXE=python"

echo   Python: %PYEXE%
echo.

REM ── Verify Flask is installed; install if missing ──
"%PYEXE%" -c "import flask" 2>nul
if errorlevel 1 (
    echo   Installing Flask...
    "%PYEXE%" -m pip install flask
    echo.
)

echo   Server starting on http://127.0.0.1:5000
echo   (browser will open in a moment)
echo.

REM ── Open the browser after a short delay so the server has time to bind ──
start "" /B cmd /c "timeout /t 2 /nobreak >nul && start """" ""http://127.0.0.1:5000"""

REM ── Run the Flask server (blocking) ──
"%PYEXE%" web\app.py

echo.
echo Server stopped.
pause
