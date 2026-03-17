# Docker Guide

## Build

```bash
docker build -t git-workflow-enforcer:latest .
```

## Run Validation

```bash
# Validate a commit message
docker run --rm git-workflow-enforcer:latest \
  python -m src.main.cli validate-commit "feat: add feature"

# Validate a branch name
docker run --rm git-workflow-enforcer:latest \
  python -m src.main.cli validate-branch "feature/JIRA-123-test"
```

## Docker Compose

```bash
docker-compose up enforcer        # Run validation
docker-compose run --rm enforcer-dev  # Interactive shell
```

## CI/CD Usage

**GitHub Actions:**
```yaml
- name: Validate commit
  run: |
    docker run --rm git-workflow-enforcer:latest \
      python -m src.main.cli validate-commit "${{ github.event.head_commit.message }}"
```

**GitLab CI:**
```yaml
validate:
  image: git-workflow-enforcer:latest
  script:
    - python -m src.main.cli validate-commit "$CI_COMMIT_MESSAGE"
```

## Image Details

- Base: `python:3.11-slim`
- Multi-stage build for smaller size
- Runs as non-root user (`enforcer`)
- Git included for branch detection
