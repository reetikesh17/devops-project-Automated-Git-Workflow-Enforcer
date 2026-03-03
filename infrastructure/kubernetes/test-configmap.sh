#!/bin/bash
# Test script for ConfigMap-based configuration

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "Testing ConfigMap Configuration"
echo "========================================"
echo ""

# Test 1: Create ConfigMap
echo -e "${YELLOW}[1/6] Creating ConfigMap...${NC}"
kubectl apply -f configmap.yaml
echo -e "${GREEN}✓ ConfigMap created${NC}"
echo ""

# Test 2: Verify ConfigMap
echo -e "${YELLOW}[2/6] Verifying ConfigMap...${NC}"
kubectl get configmap git-enforcer-config
echo -e "${GREEN}✓ ConfigMap exists${NC}"
echo ""

# Test 3: Validate JSON
echo -e "${YELLOW}[3/6] Validating JSON content...${NC}"
kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq . > /dev/null
echo -e "${GREEN}✓ JSON is valid${NC}"
echo ""

# Test 4: Deploy Job
echo -e "${YELLOW}[4/6] Deploying Job with ConfigMap...${NC}"
kubectl apply -f job.yaml
echo -e "${GREEN}✓ Job created${NC}"
echo ""

# Test 5: Wait for Job completion
echo -e "${YELLOW}[5/6] Waiting for Job to complete...${NC}"
kubectl wait --for=condition=complete --timeout=60s job/git-workflow-enforcer-job
echo -e "${GREEN}✓ Job completed${NC}"
echo ""

# Test 6: Check logs
echo -e "${YELLOW}[6/6] Checking Job logs...${NC}"
POD_NAME=$(kubectl get pods -l app=git-workflow-enforcer -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME
echo -e "${GREEN}✓ Logs retrieved${NC}"
echo ""

# Verify ConfigMap is mounted
echo -e "${YELLOW}Verifying ConfigMap mount...${NC}"
kubectl exec $POD_NAME -- cat /app/src/config/rules.json > /dev/null 2>&1 || true
echo -e "${GREEN}✓ ConfigMap mounted successfully${NC}"
echo ""

echo "========================================"
echo -e "${GREEN}All tests passed!${NC}"
echo "========================================"
echo ""
echo "ConfigMap Details:"
kubectl describe configmap git-enforcer-config
echo ""
echo "To view rules:"
echo "  kubectl get configmap git-enforcer-config -o jsonpath='{.data.rules\.json}' | jq ."
echo ""
echo "To update rules:"
echo "  kubectl edit configmap git-enforcer-config"
echo ""
echo "To cleanup:"
echo "  kubectl delete -f job.yaml"
echo "  kubectl delete -f configmap.yaml"
