# Git Hooks Guide

## Available Hooks

| Hook | Trigger | Validates |
|------|---------|-----------|
| `pre-commit` | `git commit` | Branch name |
| `commit-msg` | `git commit` | Commit message |
| `pre-push` | `git push` | Branch name |

## Install

```bash
install-hooks.bat    # Windows
./install-hooks.sh   # Linux/macOS
```

## Uninstall

```bash
uninstall-hooks.bat
./uninstall-hooks.sh
```

## How it works

**Valid commit (passes):**
```bash
git checkout -b feature/JIRA-123-add-login
git commit -m "feat: add user login functionality"
# ✓ Branch name is valid
# ✓ Commit message is valid
```

**Invalid commit message (blocked):**
```bash
git commit -m "Add login feature"
# ❌ INVALID COMMIT MESSAGE
# Error: Invalid commit message format
# Expected: <type>: <description>
```

**Invalid branch name (blocked):**
```bash
git checkout -b add-login-feature
git commit -m "feat: add login"
# ❌ INVALID BRANCH NAME
# Error: Branch name does not match any allowed pattern
```

## Bypass (emergency only)

```bash
git commit --no-verify -m "emergency fix"
git push --no-verify
```

## Notes

- Merge commits and revert commits are skipped automatically
- Protected branches (`main`, `master`, `develop`) always pass branch validation
- Rules are loaded from `src/config/rules.json`
