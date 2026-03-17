# Usage Guide

## CLI Commands

```bash
# Validate a commit message
python -m src.main.cli validate-commit "feat: add new feature"

# Validate a branch name
python -m src.main.cli validate-branch "feature/JIRA-123-description"

# Validate both at once
python -m src.main.cli validate-all

# Options
python -m src.main.cli --config custom-rules.json validate-commit "feat: test"
python -m src.main.cli --verbose validate-branch "feature/TEST-001-example"
```

## Git Hooks

After running `install-hooks.bat` (or `install-hooks.sh`), hooks run automatically:

- `pre-commit` — validates branch name before every commit
- `commit-msg` — validates commit message before every commit
- `pre-push` — validates branch name before every push

To bypass (not recommended):
```bash
git commit --no-verify -m "message"
```

## Docker

```bash
docker run --rm git-workflow-enforcer:latest \
  python -m src.main.cli validate-commit "feat: test"
```

## Kubernetes

```bash
# Deploy and run validation job
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl apply -f infrastructure/kubernetes/job.yaml

# Check logs
kubectl logs -l job-name=git-workflow-enforcer-job

# Cleanup
kubectl delete job git-workflow-enforcer-job
```

## Configuration

Edit `src/config/rules.json`:

```json
{
  "commits": {
    "types": ["feat", "fix", "docs", "chore"],
    "descriptionLength": { "min": 10, "max": 100 }
  },
  "branches": {
    "patterns": {
      "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$"
    },
    "protected": ["main", "master", "develop"]
  }
}
```
