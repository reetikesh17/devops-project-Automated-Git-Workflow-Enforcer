# Git Hooks Guide

## Overview

This guide explains how to install and use Git hooks for the Automated Git Workflow Enforcer. Git hooks automatically validate your commits and branches before they are created or pushed.

## Available Hooks

### commit-msg
Validates commit messages against Conventional Commits format.

- **Triggered by:** `git commit`
- **Validates:** Commit message format
- **Blocks:** Invalid commit messages
- **Skips:** Merge commits and revert commits

### pre-commit
Validates branch name before allowing commits.

- **Triggered by:** `git commit`
- **Validates:** Current branch name
- **Blocks:** Commits on invalid branch names

### pre-push
Validates branch name before pushing to remote.

- **Triggered by:** `git push`
- **Validates:** Current branch name
- **Blocks:** Pushes from invalid branch names

## Installation

### Linux/macOS

```bash
# Make the install script executable
chmod +x install-hooks.sh

# Run the installation script
./install-hooks.sh
```

### Windows

```cmd
# Run the installation script
install-hooks.bat
```

### Manual Installation

If the automated scripts don't work, you can install hooks manually:

```bash
# Copy hooks to .git/hooks/
cp hooks/commit-msg .git/hooks/commit-msg
cp hooks/pre-commit .git/hooks/pre-commit
cp hooks/pre-push .git/hooks/pre-push

# Make them executable (Linux/macOS only)
chmod +x .git/hooks/commit-msg
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

## Uninstallation

### Linux/macOS

```bash
# Make the uninstall script executable
chmod +x uninstall-hooks.sh

# Run the uninstallation script
./uninstall-hooks.sh
```

### Windows

```cmd
# Run the uninstallation script
uninstall-hooks.bat
```

### Manual Uninstallation

```bash
# Remove hooks
rm .git/hooks/commit-msg
rm .git/hooks/pre-commit
rm .git/hooks/pre-push

# Restore backups if they exist
mv .git/hooks/commit-msg.backup .git/hooks/commit-msg
mv .git/hooks/pre-commit.backup .git/hooks/pre-commit
mv .git/hooks/pre-push.backup .git/hooks/pre-push
```

## Usage Examples

### Valid Commit (Passes All Hooks)

```bash
# On a valid branch
git checkout -b feature/JIRA-123-add-login

# With a valid commit message
git commit -m "feat: add user login functionality"

# Push to remote
git push origin feature/JIRA-123-add-login
```

Output:
```
🔍 Validating branch name: feature/JIRA-123-add-login
✓ Branch name is valid
🔍 Validating commit message...
✓ Commit message is valid
```

### Invalid Commit Message (Blocked by commit-msg)

```bash
git commit -m "Add login feature"
```

Output:
```
🔍 Validating commit message...

======================================================================
❌ INVALID COMMIT MESSAGE
======================================================================

Your message:
  Add login feature

Error: Invalid commit message format

Expected format:
  <type>: <description>

Suggestions:
  • feat: add user authentication module
  • fix: resolve null pointer in login handler
  ...

======================================================================

❌ Commit message validation failed

Your commit has been blocked because the commit message does not follow
the required format. Please fix your commit message and try again.

To amend your commit message:
  git commit --amend

To bypass this hook (not recommended):
  git commit --no-verify
```

### Invalid Branch Name (Blocked by pre-commit)

```bash
# On an invalid branch
git checkout -b add-login-feature

# Try to commit
git commit -m "feat: add login functionality"
```

Output:
```
🔍 Validating branch name: add-login-feature

======================================================================
❌ INVALID BRANCH NAME
======================================================================

Your branch:
  add-login-feature

Error: Branch name does not match any allowed pattern

Allowed patterns:
  • Feature: feature/<TICKET-ID>-<description>
  • Bugfix: bugfix/<TICKET-ID>-<description>
  • Hotfix: hotfix/<TICKET-ID>
  • Release: release/v<version>

Examples:
  ✓ feature/JIRA-123-user-authentication
  ✓ bugfix/PROJ-456-fix-login-error
  ...

======================================================================

❌ Branch name validation failed

Your commit has been blocked because the branch name does not follow
the required naming convention.

To rename your branch:
  git branch -m <new-branch-name>

To bypass this hook (not recommended):
  git commit --no-verify
```

## Bypassing Hooks

Sometimes you may need to bypass hooks (e.g., for emergency fixes). Use the `--no-verify` flag:

```bash
# Bypass commit hooks
git commit --no-verify -m "emergency fix"

# Bypass push hooks
git push --no-verify
```

**Warning:** Bypassing hooks is not recommended as it defeats the purpose of validation. Use only when absolutely necessary.

## Hook Behavior

### Merge Commits

Merge commits are automatically skipped by the commit-msg hook:

```bash
git merge feature-branch
# Merge commit message is not validated
```

### Revert Commits

Revert commits are automatically skipped by the commit-msg hook:

```bash
git revert abc123
# Revert commit message is not validated
```

### Protected Branches

Protected branches (main, master, develop) are always considered valid:

```bash
git checkout main
git commit -m "feat: add feature"
# Branch validation passes
```

## Troubleshooting

### Hook Not Running

**Problem:** Hook doesn't execute when committing

**Solutions:**
1. Check if hook file exists:
   ```bash
   ls -la .git/hooks/commit-msg
   ```

2. Ensure hook is executable (Linux/macOS):
   ```bash
   chmod +x .git/hooks/commit-msg
   ```

3. Verify hook has correct shebang:
   ```bash
   head -n 1 .git/hooks/commit-msg
   # Should show: #!/bin/bash
   ```

### Python Not Found

**Problem:** Hook reports "Python is not installed"

**Solutions:**
1. Install Python 3.8+:
   - Linux: `sudo apt install python3`
   - macOS: `brew install python3`
   - Windows: Download from python.org

2. Ensure Python is in PATH:
   ```bash
   python --version
   # or
   python3 --version
   ```

3. Update hook to use correct Python command

### Hook Fails with Import Error

**Problem:** Hook fails with "ModuleNotFoundError"

**Solutions:**
1. Ensure you're in the project root:
   ```bash
   git rev-parse --show-toplevel
   ```

2. Verify project structure:
   ```bash
   ls src/main/cli.py
   ls src/config/rules.json
   ```

3. Check Python path in hook script

### Hook Blocks Valid Commit

**Problem:** Hook blocks a commit that should be valid

**Solutions:**
1. Test validation manually:
   ```bash
   python src/main/cli.py validate-commit "your message"
   python src/main/cli.py validate-branch "your-branch"
   ```

2. Check configuration:
   ```bash
   cat src/config/rules.json
   ```

3. Review validation rules in documentation

### Windows Line Ending Issues

**Problem:** Hooks don't work on Windows due to line endings

**Solutions:**
1. Configure Git to handle line endings:
   ```bash
   git config core.autocrlf false
   ```

2. Re-checkout hooks:
   ```bash
   rm .git/hooks/*
   ./install-hooks.bat
   ```

3. Use Windows batch scripts instead:
   ```cmd
   install-hooks.bat
   ```

## Customization

### Modifying Validation Rules

Edit `src/config/rules.json` to customize validation rules:

```json
{
  "branches": {
    "patterns": {
      "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$",
      "custom": "^custom/.*$"
    }
  },
  "commits": {
    "types": ["feat", "fix", "custom"],
    "descriptionLength": {
      "min": 5,
      "max": 150
    }
  }
}
```

### Adding Custom Hooks

Create new hook files in the `hooks/` directory:

```bash
# Create custom hook
cat > hooks/pre-rebase << 'EOF'
#!/bin/bash
echo "Running pre-rebase validation..."
# Add your validation logic here
EOF

# Install it
cp hooks/pre-rebase .git/hooks/pre-rebase
chmod +x .git/hooks/pre-rebase
```

### Disabling Specific Hooks

Remove individual hooks without uninstalling all:

```bash
# Disable commit-msg hook
rm .git/hooks/commit-msg

# Disable pre-push hook
rm .git/hooks/pre-push
```

## Team Setup

### Repository Setup

Add hooks to your repository:

```bash
# Hooks are already in the repository
git clone <repository-url>
cd <repository>

# Install hooks
./install-hooks.sh  # or install-hooks.bat on Windows
```

### Enforcing Hook Installation

Add to README.md:

```markdown
## Setup

After cloning the repository, install Git hooks:

\`\`\`bash
./install-hooks.sh  # Linux/macOS
# or
install-hooks.bat   # Windows
\`\`\`
```

### CI/CD Validation

Even with hooks installed, validate in CI/CD:

```yaml
# .github/workflows/validate.yml
name: Validate

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate branch name
        run: |
          python src/main/cli.py validate-branch ${{ github.ref_name }}
      
      - name: Validate commit messages
        run: |
          for commit in $(git rev-list origin/main..${{ github.sha }}); do
            git log --format=%B -n 1 $commit | \
              python src/main/cli.py validate-commit -
          done
```

## Best Practices

1. **Install hooks immediately** after cloning the repository
2. **Don't bypass hooks** unless absolutely necessary
3. **Keep hooks updated** by pulling latest changes
4. **Test hooks** before committing important work
5. **Document custom rules** in team documentation
6. **Use CI/CD validation** as a backup to client-side hooks
7. **Educate team members** about validation rules

## Advanced Usage

### Testing Hooks

Test hooks without making actual commits:

```bash
# Test commit-msg hook
echo "feat: test message" | .git/hooks/commit-msg /dev/stdin

# Test pre-commit hook
.git/hooks/pre-commit

# Test pre-push hook
.git/hooks/pre-push
```

### Debugging Hooks

Enable debug output:

```bash
# Add to hook script
set -x  # Enable debug mode

# Run hook
git commit -m "test"
```

### Hook Performance

Measure hook execution time:

```bash
# Add to hook script
START_TIME=$(date +%s%N)
# ... hook logic ...
END_TIME=$(date +%s%N)
ELAPSED=$((($END_TIME - $START_TIME) / 1000000))
echo "Hook execution time: ${ELAPSED}ms"
```

## Resources

- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Project README](../README.md)
- [Design Document](design-document.md)

## Support

If you encounter issues with Git hooks:

1. Check this documentation
2. Review troubleshooting section
3. Test validation manually
4. Check project issues on GitHub
5. Contact the development team
