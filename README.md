# Automated Git Workflow Enforcer

A Python tool that enforces Git workflow standards by validating branch names and commit messages — across Git hooks, Docker, GitHub Actions, Kubernetes, and Terraform.

## What it does

- Validates commit messages against [Conventional Commits](https://www.conventionalcommits.org/) format
- Validates branch names against defined patterns (feature, bugfix, hotfix, release)
- Blocks bad commits at the source via Git hooks
- Runs the same validation in Docker containers and CI/CD pipelines

## Quick Start

```bash
git clone https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer.git
cd devops-project-Automated-Git-Workflow-Enforcer
pip install -r requirements.txt
```

Install Git hooks:
```bash
install-hooks.bat        # Windows
./install-hooks.sh       # Linux/macOS
```

## CLI Usage

```bash
# Validate a commit message
python -m src.main.cli validate-commit "feat: add user authentication"

# Validate a branch name
python -m src.main.cli validate-branch "feature/JIRA-123-add-login"
```

## Validation Rules

**Commit format:** `<type>: <description>`

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `test` | Tests |
| `chore` | Maintenance |
| `ci` | CI/CD changes |

Rules: description 10–100 chars, lowercase start, no trailing period.

**Branch format:**

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<TICKET>-<desc>` | `feature/JIRA-123-user-auth` |
| Bugfix | `bugfix/<TICKET>-<desc>` | `bugfix/PROJ-456-fix-login` |
| Hotfix | `hotfix/<TICKET>` | `hotfix/URGENT-789` |
| Release | `release/v<version>` | `release/v1.2.0` |

Protected branches: `main`, `master`, `develop`

## Running Tests

```bash
# Unit tests (40 total)
python examples/test_commit_validator.py
python examples/test_branch_validator.py

# Full 8-category test suite
cmd /c Final-test.bat
```

## Web Dashboard

```bash
python ui/app.py
# Open http://localhost:5000
```

Login with `admin / admin123` or `demo / demo123`.

## Project Structure

```
src/
├── validators/          # Commit and branch validators
├── config/              # rules.json + config loader
└── main/cli.py          # CLI entry point
hooks/                   # Git hook scripts
infrastructure/
├── kubernetes/          # K8s job, configmap, deployment
└── terraform/           # AWS infrastructure (IaC)
.github/workflows/       # GitHub Actions CI/CD
ui/                      # Flask web dashboard
examples/                # Test scripts
```

## Enforcement Layers

```
Git Hooks → Docker → GitHub Actions → Kubernetes → Terraform
```

Each layer runs the same validators, ensuring consistent enforcement from local dev to production.

## Configuration

Edit `src/config/rules.json` to customize rules:

```json
{
  "commits": {
    "types": ["feat", "fix", "chore", "docs", "refactor", "test", "ci"],
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

## License

MIT — see [LICENSE](LICENSE)
