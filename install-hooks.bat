@echo off
REM Install Git Hooks Script for Windows
REM Installs Git hooks for the Automated Git Workflow Enforcer

setlocal enabledelayedexpansion

echo ================================================================
echo   Git Workflow Enforcer - Hook Installation (Windows)
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
set HOOKS_SOURCE_DIR=%PROJECT_ROOT%\hooks
set HOOKS_TARGET_DIR=%PROJECT_ROOT%\.git\hooks

REM Check if hooks source directory exists
if not exist "%HOOKS_SOURCE_DIR%" (
    echo [ERROR] Hooks directory not found
    echo Expected location: %HOOKS_SOURCE_DIR%
    exit /b 1
)

REM Check if .git/hooks directory exists
if not exist "%HOOKS_TARGET_DIR%" (
    echo [ERROR] .git\hooks directory not found
    echo This doesn't appear to be a valid Git repository
    exit /b 1
)

REM Check if Python is available
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ before installing hooks
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Install hooks
echo [INFO] Installing Git hooks...
echo.

REM List of hooks to install
set HOOKS=commit-msg pre-commit pre-push

for %%H in (%HOOKS%) do (
    set SOURCE_FILE=%HOOKS_SOURCE_DIR%\%%H
    set TARGET_FILE=%HOOKS_TARGET_DIR%\%%H
    set BACKUP_FILE=%HOOKS_TARGET_DIR%\%%H.backup
    
    if not exist "!SOURCE_FILE!" (
        echo   [SKIP] %%H - Source file not found
    ) else (
        REM Backup existing hook if it exists
        if exist "!TARGET_FILE!" (
            echo   [WARN] %%H - Backing up existing hook
            copy /Y "!TARGET_FILE!" "!BACKUP_FILE!" >nul
            echo          Backup saved to: %%H.backup
        )
        
        REM Copy hook to .git/hooks
        copy /Y "!SOURCE_FILE!" "!TARGET_FILE!" >nul
        
        echo   [OK] %%H - Installed successfully
    )
)

echo.
echo ================================================================
echo   Installation Complete!
echo ================================================================
echo.
echo [OK] Git hooks have been installed successfully
echo.
echo Installed hooks:
echo   * commit-msg
echo   * pre-commit
echo   * pre-push
echo.
echo What happens now:
echo   * commit-msg: Validates commit messages on every commit
echo   * pre-commit: Validates branch name before committing
echo   * pre-push: Validates branch name before pushing
echo.
echo To test the hooks:
echo   git commit -m "test: validate commit message"
echo.
echo To bypass hooks (not recommended):
echo   git commit --no-verify
echo   git push --no-verify
echo.
echo To uninstall hooks:
echo   uninstall-hooks.bat
echo.

endlocal
