#!/bin/bash
#
# Uninstall Git Hooks Script
# Removes Git hooks for the Automated Git Workflow Enforcer
#
# Usage: ./uninstall-hooks.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Error: Not in a Git repository${NC}"
    echo "Please run this script from within a Git repository"
    exit 1
fi

# Define paths
HOOKS_TARGET_DIR="$PROJECT_ROOT/.git/hooks"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Git Workflow Enforcer - Hook Uninstallation              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .git/hooks directory exists
if [ ! -d "$HOOKS_TARGET_DIR" ]; then
    echo -e "${RED}❌ Error: .git/hooks directory not found${NC}"
    exit 1
fi

# List of hooks to uninstall
HOOKS=("commit-msg" "pre-commit" "pre-push")

# Uninstall each hook
echo -e "${YELLOW}🗑️  Uninstalling Git hooks...${NC}"
echo ""

for HOOK in "${HOOKS[@]}"; do
    TARGET_FILE="$HOOKS_TARGET_DIR/$HOOK"
    BACKUP_FILE="$HOOKS_TARGET_DIR/$HOOK.backup"
    
    # Check if hook exists
    if [ ! -f "$TARGET_FILE" ]; then
        echo -e "${YELLOW}  ⚠ $HOOK - Not installed${NC}"
        continue
    fi
    
    # Remove hook
    rm "$TARGET_FILE"
    echo -e "${GREEN}  ✓ $HOOK - Removed${NC}"
    
    # Restore backup if it exists
    if [ -f "$BACKUP_FILE" ]; then
        mv "$BACKUP_FILE" "$TARGET_FILE"
        chmod +x "$TARGET_FILE"
        echo -e "${GREEN}    Restored backup${NC}"
    fi
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Uninstallation Complete!                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Git hooks have been uninstalled${NC}"
echo ""
echo "To reinstall hooks:"
echo "  ./install-hooks.sh"
echo ""
