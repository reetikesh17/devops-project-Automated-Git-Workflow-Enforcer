#!/bin/bash
# Quick test script for Linux/Mac

set -e

echo "========================================"
echo "Testing Git Workflow Enforcer"
echo "========================================"
echo ""

echo "[1/5] Testing Commit Validator..."
python examples/test_commit_validator.py
echo "PASSED ✓"
echo ""

echo "[2/5] Testing Branch Validator..."
python examples/test_branch_validator.py
echo "PASSED ✓"
echo ""

echo "[3/5] Testing CLI - Commit Validation..."
python -m src.main.cli validate-commit "feat: test feature"
echo "PASSED ✓"
echo ""

echo "[4/5] Testing CLI - Branch Validation..."
python -m src.main.cli validate-branch "feature/test-branch"
echo "PASSED ✓"
echo ""

echo "[5/5] Testing CLI - Invalid Input Handling..."
if python -m src.main.cli validate-commit "bad commit" > /dev/null 2>&1; then
    echo "FAILED: Should reject invalid commit"
    exit 1
fi
echo "PASSED ✓"
echo ""

echo "========================================"
echo "All Core Tests Passed! ✅"
echo "========================================"
echo ""
echo "Next steps:"
echo "- Test Docker: docker build -t git-workflow-enforcer:test ."
echo "- Test Hooks: ./install-hooks.sh"
echo "- Test Kubernetes: kubectl apply -f infrastructure/kubernetes/"
echo ""
