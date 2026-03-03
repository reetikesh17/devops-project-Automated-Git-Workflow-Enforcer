# Usage Guide

## CLI Commands

### Validate Commit Message

```bash
python -m src.main.cli validate-commit "feat: add new feature"
```

### Validate Branch Name

```bash
python -m src.main.cli validate-branch "feature/JIRA-123-description"
```

### Validate All

```bash
python -m src.main.cli validate-all
```

### Options

```bash
--config PATH    # Custom config file
--verbose        # Verbose output
--no-color       # Disable colors
--ci             # CI/CD mode
```

## Git Hooks

Hooks are automatically installed in `.git/hooks/`:

- **pre-commit**: Validates before commit
- **commit-msg**: Validates commit message
- **pre-push**: Validates branch name

## Configuration

Edit `src/config/rules.json` to customize validation rules:

```json
{
  "commits": {
    "types": ["feat", "fix", "docs", "chore"],
    "descriptionLength": {
      "min": 10,
      "max": 100
    }
  },
  "branches": {
    "patterns": {
      "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$"
    }
  }
}
```

## Docker Usage

```bash
# Run validation
docker run --rm git-workflow-enforcer:latest \
  python -m src.main.cli validate-commit "feat: test"

# With volume mount
docker run --rm -v $(pwd):/workspace \
  git-workflow-enforcer:latest \
  python -m src.main.cli validate-all
```

## Kubernetes Usage

```bash
# Deploy
kubectl apply -f infrastructure/kubernetes/

# Check logs
kubectl logs -l app=git-workflow-enforcer

# Update ConfigMap
kubectl edit configmap git-enforcer-config
kubectl rollout restart deployment git-workflow-enforcer
```

## Examples

See `examples/` directory for test scripts:
- `test_commit_validator.py`
- `test_branch_validator.py`
