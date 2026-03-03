@echo off
REM Quick test script for Windows

echo ========================================
echo Testing Git Workflow Enforcer
echo ========================================
echo.

echo [1/5] Testing Commit Validator...
python examples\test_commit_validator.py
if %errorlevel% neq 0 (
    echo FAILED: Commit validator test
    exit /b 1
)
echo PASSED ✓
echo.

echo [2/5] Testing Branch Validator...
python examples\test_branch_validator.py
if %errorlevel% neq 0 (
    echo FAILED: Branch validator test
    exit /b 1
)
echo PASSED ✓
echo.

echo [3/5] Testing CLI - Commit Validation...
python -m src.main.cli validate-commit "feat: test feature"
if %errorlevel% neq 0 (
    echo FAILED: CLI commit validation
    exit /b 1
)
echo PASSED ✓
echo.

echo [4/5] Testing CLI - Branch Validation...
python -m src.main.cli validate-branch "feature/test-branch"
if %errorlevel% neq 0 (
    echo FAILED: CLI branch validation
    exit /b 1
)
echo PASSED ✓
echo.

echo [5/5] Testing CLI - Invalid Input Handling...
python -m src.main.cli validate-commit "bad commit" >nul 2>&1
if %errorlevel% equ 0 (
    echo FAILED: Should reject invalid commit
    exit /b 1
)
echo PASSED ✓
echo.

echo ========================================
echo All Core Tests Passed! ✅
echo ========================================
echo.
echo Next steps:
echo - Test Docker: docker build -t git-workflow-enforcer:test .
echo - Test Hooks: install-hooks.bat
echo - Test Kubernetes: kubectl apply -f infrastructure/kubernetes/
echo.
