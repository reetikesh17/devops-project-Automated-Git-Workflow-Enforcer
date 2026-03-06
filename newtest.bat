@echo off
title Git Workflow Enforcer - Test Suite

set TOTAL=0
set PASSED=0
set FAILED=0

echo ==================================================
echo        Git Workflow Enforcer - Test Suite
echo ==================================================
echo.

set PYTHONIOENCODING=utf-8
chcp 65001 >nul

call :run_test 1 "Commit Validator Tests" python examples\test_commit_validator.py
call :run_test 2 "Branch Validator Tests" python examples\test_branch_validator.py
call :run_test 3 "CLI Commit Validation" python -m src.main.cli validate-commit "feat: add user authentication"
call :run_test_inv 4 "CLI Invalid Commit Test" python -m src.main.cli validate-commit "bad message"
call :run_test 5 "CLI Branch Validation" python -m src.main.cli validate-branch "feature/PROJ-123-add-login"
call :run_test_inv 6 "CLI Invalid Branch Test" python -m src.main.cli validate-branch "random-branch"
call :run_test 7 "CLI Help" python -m src.main.cli --help
call :run_test 8 "Docker Build" docker build -t git-workflow-enforcer:test .
call :run_test 9 "Docker Container Validation" docker run --rm git-workflow-enforcer:test python -m src.main.cli validate-commit "feat: docker test"
call :run_test_inv 10 "Docker Invalid Input Test" docker run --rm git-workflow-enforcer:test python -m src.main.cli validate-commit "bad"
call :run_test 11 "Kubernetes ConfigMap" kubectl apply -f infrastructure\kubernetes\configmap.yaml
call :run_test 12 "Kubernetes Job" kubectl apply -f infrastructure\kubernetes\job.yaml
call :run_test 13 "Kubernetes Job Status" kubectl get jobs
call :run_test 14 "Kubernetes Logs" kubectl logs -l job-name=git-workflow-enforcer-job
call :run_test 15 "Kubernetes Cleanup" kubectl delete job git-workflow-enforcer-job

cd infrastructure\terraform
call :run_test 16 "Terraform Validation" terraform validate
cd ..\..

call :run_test 17 "Install Git Hooks" install-hooks.bat
call :run_test_inv 18 "Invalid Commit Hook Test" git commit -m "bad"
call :run_test 19 "Valid Commit Hook Test" git commit -m "feat: test git hooks"
call :run_test 20 "Uninstall Hooks" uninstall-hooks.bat
call :run_test 21 "Project Verification" python -m src.main.cli validate-commit "feat: test"

echo.
echo ==================================================
echo TEST SUMMARY
echo ==================================================
echo Total Tests : %TOTAL%
echo Passed      : %PASSED%
echo Failed      : %FAILED%

if %FAILED%==0 (
 echo STATUS : ALL TESTS PASSED
) else (
 echo STATUS : SOME TESTS FAILED
)

echo ==================================================
pause
exit /b

:run_test
set /a TOTAL+=1
%3 %4 %5 %6 %7 %8 >nul 2>&1
if %ERRORLEVEL%==0 (
 echo [%1] %2 : PASS
 set /a PASSED+=1
) else (
 echo [%1] %2 : FAIL
 set /a FAILED+=1
)
exit /b

:run_test_inv
set /a TOTAL+=1
%3 %4 %5 %6 %7 %8 >nul 2>&1
if %ERRORLEVEL% neq 0 (
 echo [%1] %2 : PASS
 set /a PASSED+=1
) else (
 echo [%1] %2 : FAIL
 set /a FAILED+=1
)
exit /b