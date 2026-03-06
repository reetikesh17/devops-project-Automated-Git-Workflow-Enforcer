@echo off
title Git Workflow Enforcer - Test Suite

echo ==========================================
echo   Git Workflow Enforcer - Test Runner
echo ==========================================
echo.

REM Set encoding for Python output
set PYTHONIOENCODING=utf-8
chcp 65001 >nul

echo ------------------------------------------
echo 1. Running Commit Validator Tests
echo ------------------------------------------
python examples\test_commit_validator.py

if %ERRORLEVEL% neq 0 (
    echo Commit Validator Tests FAILED
    pause
    exit /b 1
)

echo.
echo ------------------------------------------
echo 2. Running Branch Validator Tests
echo ------------------------------------------
python examples\test_branch_validator.py

if %ERRORLEVEL% neq 0 (
    echo Branch Validator Tests FAILED
    pause
    exit /b 1
)

echo.
echo ------------------------------------------
echo 3. CLI Commit Validation (Valid Case)
echo ------------------------------------------
python -m src.main.cli validate-commit "feat: automated test"

echo.
echo ------------------------------------------
echo 4. CLI Commit Validation (Invalid Case)
echo ------------------------------------------
python -m src.main.cli validate-commit "bad message"

echo.
echo ------------------------------------------
echo 5. CLI Branch Validation (Valid Case)
echo ------------------------------------------
python -m src.main.cli validate-branch "feature/PROJ-101-test"

echo.
echo ------------------------------------------
echo 6. CLI Branch Validation (Invalid Case)
echo ------------------------------------------
python -m src.main.cli validate-branch "random-branch"

echo.
echo ------------------------------------------
echo 7. Docker Build Test
echo ------------------------------------------
docker build -t git-workflow-enforcer:test .

if %ERRORLEVEL% neq 0 (
    echo Docker Build FAILED
    pause
    exit /b 1
)

echo.
echo ------------------------------------------
echo 8. Docker Container Test
echo ------------------------------------------
docker run --rm git-workflow-enforcer:test python -m src.main.cli validate-commit "feat: docker test"

echo.
echo ------------------------------------------
echo 9. Terraform Validation
echo ------------------------------------------
cd infrastructure\terraform
terraform validate

cd ..\..

echo.
echo ------------------------------------------
echo 10. Project Structure Check
echo ------------------------------------------
dir /b src\validators
dir /b hooks
dir /b infrastructure\kubernetes

echo.
echo ==========================================
echo ALL TESTS COMPLETED
echo ==========================================
echo.

pause