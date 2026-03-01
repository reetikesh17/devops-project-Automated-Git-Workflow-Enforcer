@echo off
REM Uninstall Git Hooks Script for Windows
REM Removes Git hooks for the Automated Git Workflow Enforcer

setlocal enabledelayedexpansion

echo ================================================================
echo   Git Workflow Enforcer - Hook Uninstallation (Windows)
echo ================================================================
echo.

REM Get the project root directory
for /f "delims=" %%i in ('git rev-parse --show-toplevel 2^>nul') do set PROJECT_ROOT=%%i

if "%PROJECT_ROOT%"=="" (
    echo [ERROR] Not in a Git repository
    echo Please run this script from within a Git repository
    exit /b 1
)

REM Convert forward slashes to backslashes for Windows
set PROJECT_ROOT=%PROJECT_ROOT:/=\%

REM Define paths
set HOOKS_TARGET_DIR=%PROJECT_ROOT%\.git\hooks

REM Check if .git/hooks directory exists
if not exist "%HOOKS_TARGET_DIR%" (
    echo [ERROR] .git\hooks directory not found
    exit /b 1
)

REM Uninstall hooks
echo [INFO] Uninstalling Git hooks...
echo.

REM List of hooks to uninstall
set HOOKS=commit-msg pre-commit pre-push

for %%H in (%HOOKS%) do (
    set TARGET_FILE=%HOOKS_TARGET_DIR%\%%H
    set BACKUP_FILE=%HOOKS_TARGET_DIR%\%%H.backup
    
    if not exist "!TARGET_FILE!" (
        echo   [WARN] %%H - Not installed
    ) else (
        REM Remove hook
        del "!TARGET_FILE!"
        echo   [OK] %%H - Removed
        
        REM Restore backup if it exists
        if exist "!BACKUP_FILE!" (
            move /Y "!BACKUP_FILE!" "!TARGET_FILE!" >nul
            echo        Restored backup
        )
    )
)

echo.
echo ================================================================
echo   Uninstallation Complete!
echo ================================================================
echo.
echo [OK] Git hooks have been uninstalled
echo.
echo To reinstall hooks:
echo   install-hooks.bat
echo.

endlocal
