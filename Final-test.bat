@echo off
title Git Workflow Enforcer - Complete Test Suite

set TOTAL=0
set PASSED=0
set FAILED=0

echo ======================================================
echo        Git Workflow Enforcer - Automated Tests
echo ======================================================
echo.

set PYTHONIOENCODING=utf-8
chcp 65001 >nul

REM -----------------------------
REM 1 Commit Validator Tests
REM -----------------------------
echo [1] Commit Validator Tests
set /a TOTAL+=1
python examples\test_commit_validator.py
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 2 Branch Validator Tests
REM -----------------------------
echo [2] Branch Validator Tests
set /a TOTAL+=1
python examples\test_branch_validator.py
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 3 CLI Commit Validation
REM -----------------------------
echo [3] CLI Commit Validation
set /a TOTAL+=1
python -m src.main.cli validate-commit "feat: add user authentication"
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 4 CLI Invalid Commit
REM -----------------------------
echo [4] CLI Invalid Commit Test
set /a TOTAL+=1
python -m src.main.cli validate-commit "bad message"
if %ERRORLEVEL% neq 0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 5 CLI Branch Validation
REM -----------------------------
echo [5] CLI Branch Validation
set /a TOTAL+=1
python -m src.main.cli validate-branch "feature/PROJ-123-add-login"
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 6 CLI Invalid Branch
REM -----------------------------
echo [6] CLI Invalid Branch Test
set /a TOTAL+=1
python -m src.main.cli validate-branch "random-branch"
if %ERRORLEVEL% neq 0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 7 CLI Help
REM -----------------------------
echo [7] CLI Help
set /a TOTAL+=1
python -m src.main.cli --help
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 8 Docker Build
REM -----------------------------
echo [8] Docker Build
set /a TOTAL+=1
docker build -t git-workflow-enforcer:test .
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 9 Docker Container Test
REM -----------------------------
echo [9] Docker Container Validation
set /a TOTAL+=1
docker run --rm git-workflow-enforcer:test python -m src.main.cli validate-commit "feat: docker test"
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 10 Docker Invalid Input
REM -----------------------------
echo [10] Docker Invalid Input Test
set /a TOTAL+=1
docker run --rm git-workflow-enforcer:test python -m src.main.cli validate-commit "bad"
if %ERRORLEVEL% neq 0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 11 Kubernetes ConfigMap
REM -----------------------------
echo [11] Kubernetes ConfigMap
set /a TOTAL+=1
kubectl apply -f infrastructure\kubernetes\configmap.yaml
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 12 Kubernetes Job
REM -----------------------------
echo [12] Kubernetes Job
set /a TOTAL+=1
kubectl apply -f infrastructure\kubernetes\job.yaml
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 13 Kubernetes Job Status
REM -----------------------------
echo [13] Kubernetes Job Status
set /a TOTAL+=1
kubectl get jobs
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 14 Kubernetes Logs
REM -----------------------------
echo [14] Kubernetes Logs
set /a TOTAL+=1
kubectl logs -l job-name=git-workflow-enforcer-job
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 15 Kubernetes Cleanup
REM -----------------------------
echo [15] Kubernetes Cleanup
set /a TOTAL+=1
kubectl delete job git-workflow-enforcer-job
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 16 Terraform Validation
REM -----------------------------
echo [16] Terraform Validation
set /a TOTAL+=1
cd infrastructure\terraform
terraform validate
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
cd ..\..
echo.

REM -----------------------------
REM 17 Install Git Hooks
REM -----------------------------
echo [17] Install Git Hooks
set /a TOTAL+=1
install-hooks.bat
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 18 Invalid Commit Hook Test
REM -----------------------------
echo [18] Invalid Commit Hook Test
set /a TOTAL+=1
git commit -m "bad"
if %ERRORLEVEL% neq 0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 19 Valid Commit Hook Test
REM -----------------------------
echo [19] Valid Commit Hook Test
set /a TOTAL+=1
git commit -m "feat: test git hooks"
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 20 Uninstall Hooks
REM -----------------------------
echo [20] Uninstall Hooks
set /a TOTAL+=1
uninstall-hooks.bat
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

REM -----------------------------
REM 21 Project Verification
REM -----------------------------
echo [21] Project Verification Checks
set /a TOTAL+=1
python -m src.main.cli validate-commit "feat: test"
if %ERRORLEVEL%==0 (
 echo [PASS]
 set /a PASSED+=1
) else (
 echo [FAIL]
 set /a FAILED+=1
)
echo.

echo ======================================================
echo                    TEST SUMMARY
echo ======================================================
echo Total Tests : %TOTAL%
echo Passed      : %PASSED%
echo Failed      : %FAILED%

if %FAILED%==0 (
 echo STATUS : ALL TESTS PASSED
) else (
 echo STATUS : SOME TESTS FAILED
)

echo ======================================================
pause