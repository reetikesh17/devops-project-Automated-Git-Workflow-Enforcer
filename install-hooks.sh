#!/bin/bash
#
# Install Git Hooks Script
# Installs Git hooks for the Automated Git Workflow Enforcer
#
# Usage: ./install-hooks.sh

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
HOOKS_SOURCE_DIR="$PROJECT_ROOT/hooks"
HOOKS_TARGET_DIR="$PROJECT_ROOT/.git/hooks"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Git Workflow Enforcer - Hook Installation                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if hooks source directory exists
if [ ! -d "$HOOKS_SOURCE_DIR" ]; then
    echo -e "${RED}❌ Error: Hooks directory not found${NC}"
    echo "Expected location: $HOOKS_SOURCE_DIR"
    exit 1
fi

# Check if .git/hooks directory exists
if [ ! -d "$HOOKS_TARGET_DIR" ]; then
    echo -e "${RED}❌ Error: .git/hooks directory not found${NC}"
    echo "This doesn't appear to be a valid Git repository"
    exit 1
fi

# Check if Python is available
echo -e "${YELLOW}🔍 Checking Python installation...${NC}"
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python is not installed or not in PATH${NC}"
    echo "Please install Python 3.8+ before installing hooks"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# List of hooks to install
HOOKS=("commit-msg" "pre-commit" "pre-push")

# Install each hook
echo -e "${YELLOW}📦 Installing Git hooks...${NC}"
echo ""

for HOOK in "${HOOKS[@]}"; do
    SOURCE_FILE="$HOOKS_SOURCE_DIR/$HOOK"
    TARGET_FILE="$HOOKS_TARGET_DIR/$HOOK"
    BACKUP_FILE="$HOOKS_TARGET_DIR/$HOOK.backup"
    
    # Check if source hook exists
    if [ ! -f "$SOURCE_FILE" ]; then
        echo -e "${RED}  ✗ $HOOK - Source file not found${NC}"
        continue
    fi
    
    # Backup existing hook if it exists
    if [ -f "$TARGET_FILE" ]; then
        echo -e "${YELLOW}  ⚠ $HOOK - Backing up existing hook${NC}"
        cp "$TARGET_FILE" "$BACKUP_FILE"
        echo -e "    Backup saved to: $HOOK.backup"
    fi
    
    # Copy hook to .git/hooks
    cp "$SOURCE_FILE" "$TARGET_FILE"
    
    # Make hook executable
    chmod +x "$TARGET_FILE"
    
    echo -e "${GREEN}  ✓ $HOOK - Installed successfully${NC}"
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Installation Complete!                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Git hooks have been installed successfully${NC}"
echo ""
echo "Installed hooks:"
for HOOK in "${HOOKS[@]}"; do
    echo "  • $HOOK"
done
echo ""
echo "What happens now:"
echo "  • commit-msg: Validates commit messages on every commit"
echo "  • pre-commit: Validates branch name before committing"
echo "  • pre-push: Validates branch name before pushing"
echo ""
echo "To test the hooks:"
echo "  git commit -m \"test: validate commit message\""
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "To uninstall hooks:"
echo "  ./uninstall-hooks.sh"
echo ""
