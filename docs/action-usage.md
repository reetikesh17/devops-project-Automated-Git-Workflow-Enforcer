# GitHub Action Usage Guide

## Overview

The Git Workflow Enforcer is available as a reusable composite GitHub Action that can be used in any repository to validate branch names and commit messages.

## Quick Start

### Basic Usage

Add this step to your workflow:

```yaml
- name: Validate Git Workflow
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
```

This will:
- Auto-detect current branch
- Auto-detect latest commit message
- Validate both against configured rules
- Fail the workflow if validation fails

### Complete Example

```yaml
name: Validate

on: [pull_request, push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Validate Git Workflow
        uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `config-path` | Path to custom configuration file | No | `` |
| `python-version` | Python version to use | No | `3.11` |
| `validate-branch` | Validate branch name | No | `true` |
| `validate-commit` | Validate commit message | No | `true` |
| `branch-name` | Branch name to validate | No | Auto-detected |
| `commit-message` | Commit message to validate | No | Auto-detected |
| `fail-on-error` | Fail action if validation fails | No | `true` |

## Outputs

| Output | Description | Value |
|--------|-------------|-------|
| `validation-status` | Overall validation status | `pass` or `fail` |
| `branch-valid` | Branch validation result | `true` or `false` |
| `commit-valid` | Commit validation result | `true` or `false` |
| `validation-output` | Full validation output | JSON string |

## Usage Examples

### Example 1: Validate Branch Only

```yaml
- name: Validate Branch
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    validate-commit: false
```

### Example 2: Validate Commit Only

```yaml
- name: Validate Commit
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    validate-branch: false
```

### Example 3: Custom Configuration

```yaml
- name: Validate with Custom Rules
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    config-path: 'config/strict-rules.json'
```

### Example 4: Specific Branch and Commit

```yaml
- name: Validate Specific Values
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    branch-name: 'feature/JIRA-123-test'
    commit-message: 'feat: add new feature'
```

### Example 5: Custom Python Version

```yaml
- name: Validate with Python 3.12
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    python-version: '3.12'
```

### Example 6: Don't Fail on Error

```yaml
- name: Validate (Warning Only)
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    fail-on-error: false
```

### Example 7: Use Outputs

```yaml
- name: Validate
  id: validate
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1

- name: Check Results
  run: |
    echo "Status: ${{ steps.validate.outputs.validation-status }}"
    echo "Branch Valid: ${{ steps.validate.outputs.branch-valid }}"
    echo "Commit Valid: ${{ steps.validate.outputs.commit-valid }}"

- name: Deploy if Valid
  if: steps.validate.outputs.validation-status == 'pass'
  run: echo "Deploying..."
```

### Example 8: Matrix Testing

```yaml
jobs:
  validate:
    strategy:
      matrix:
        config: [strict, lenient]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate with ${{ matrix.config }} rules
        uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
        with:
          config-path: 'config/${{ matrix.config }}-rules.json'
```

### Example 9: Pull Request Validation

```yaml
name: PR Validation

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Validate PR
        uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
        with:
          branch-name: ${{ github.head_ref }}
          commit-message: ${{ github.event.pull_request.title }}
```

### Example 10: Multiple Validations

```yaml
jobs:
  validate-branch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate Branch
        uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
        with:
          validate-commit: false
  
  validate-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate Commit
        uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
        with:
          validate-branch: false
```

## Version Pinning

### Use Specific Version

```yaml
uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1.0.0
```

### Use Major Version (Recommended)

```yaml
uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
```

### Use Specific Commit

```yaml
uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@abc123
```

### Use Branch (Not Recommended for Production)

```yaml
uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@main
```

## Configuration

### Default Configuration

The action uses default rules if no config is provided:

**Branch Patterns:**
- `feature/<TICKET-ID>-<description>`
- `bugfix/<TICKET-ID>-<description>`
- `hotfix/<TICKET-ID>`
- `release/v<version>`

**Commit Types:**
- `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`

**Commit Format:**
- `<type>: <description>`
- Description: 10-100 characters
- Lowercase, no period at end

### Custom Configuration

Create a configuration file in your repository:

```json
{
  "branches": {
    "patterns": {
      "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$",
      "bugfix": "^bugfix/[A-Z]+-[0-9]+-[a-z0-9-]+$",
      "hotfix": "^hotfix/[A-Z]+-[0-9]+$",
      "release": "^release/v[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "protected": ["main", "master", "develop"]
  },
  "commits": {
    "types": ["feat", "fix", "chore", "docs", "refactor", "test", "ci"],
    "descriptionLength": {
      "min": 10,
      "max": 100
    }
  }
}
```

Use in action:

```yaml
- uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    config-path: '.github/validation-rules.json'
```

## Troubleshooting

### Action Fails to Find Python

**Solution:** Ensure checkout step comes before the action:

```yaml
- uses: actions/checkout@v4
- uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
```

### Cannot Detect Branch/Commit

**Solution:** Fetch full history:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

### Custom Config Not Found

**Solution:** Ensure config file is in repository and path is correct:

```yaml
with:
  config-path: '.github/rules.json'  # Relative to repo root
```

### Validation Passes Locally but Fails in CI

**Possible causes:**
1. Different Python versions
2. Different configurations
3. Environment-specific issues

**Solution:** Test locally with same Python version:

```bash
python3.11 src/main/cli.py --ci validate-all
```

## Best Practices

1. **Always checkout code first**
   ```yaml
   - uses: actions/checkout@v4
   - uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
   ```

2. **Fetch full history for commit validation**
   ```yaml
   - uses: actions/checkout@v4
     with:
       fetch-depth: 0
   ```

3. **Pin to major version**
   ```yaml
   uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
   ```

4. **Use outputs for conditional logic**
   ```yaml
   - id: validate
     uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
   
   - if: steps.validate.outputs.validation-status == 'pass'
     run: echo "Valid!"
   ```

5. **Store custom configs in `.github/` directory**
   ```
   .github/
   ├── workflows/
   └── validation-rules.json
   ```

## Integration Examples

### With Slack Notifications

```yaml
- name: Validate
  id: validate
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  continue-on-error: true

- name: Notify Slack
  if: steps.validate.outputs.validation-status == 'fail'
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ Validation failed for ${{ github.ref }}"
      }
```

### With Branch Protection

```yaml
name: Required Validation

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
```

Then configure branch protection to require this check.

### With Auto-Fix PR

```yaml
- name: Validate
  id: validate
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  continue-on-error: true

- name: Create Fix PR
  if: steps.validate.outputs.validation-status == 'fail'
  run: |
    # Create a PR with suggested fixes
    echo "Creating fix PR..."
```

## Support

For issues or questions:
1. Check this documentation
2. Review [GitHub Action Guide](github-action-guide.md)
3. Check [project issues](https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer/issues)
4. Create a new issue with:
   - Workflow file
   - Error messages
   - Expected vs actual behavior

## Resources

- [Action Marketplace](https://github.com/marketplace)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Project Repository](https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer)
