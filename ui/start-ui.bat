@echo off
chcp 65001 > nul
echo.
echo ══════════════════════════════════════════════════
echo   Git Workflow Enforcer - Starting Dashboard
echo ══════════════════════════════════════════════════
echo.

REM Install Flask if not installed
pip show flask > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing Flask...
    pip install flask
)

echo   Starting server...
echo   Open browser at: http://localhost:5000
echo.
echo   Press Ctrl+C to stop
echo ══════════════════════════════════════════════════
echo.

cd /d %~dp0..
python ui/app.py
