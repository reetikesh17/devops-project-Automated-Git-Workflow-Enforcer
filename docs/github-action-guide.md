# GitHub Action Guide

## Overview

The Git Workflow Enforcer provides a reusable GitHub Action workflow that automatically validates branch names and commit messages in your CI/CD pipeline.

## Features

- ✅ **Automatic validation** of branch names and commit messages
- ✅ **Auto-detection** of current branch and latest commit
- ✅ **Reusable workflow** via `workflow_call`
- ✅ **PR comments** with validation results
- ✅ **Job summaries** with detailed reports
- ✅ **Artifact uploads** for validation reports
- ✅ **Customizable** Python version and config path
- ✅ **Status outputs** for downstream jobs

## Quick Start

### Option 1: Direct Usage

Add this workflow to your repository at `.github/workflows/validate.yml`:

```yaml
name: Validate Git Workflow

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Validate
        run: |
          python src/main/cli.py --ci validate-all
```

### Option 2: Reusable Workflow

Use the provided reusable workflow:

```yaml
name: Validate

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    uses: ./.github/workflows/validate.yml
```

## Workflow Inputs

The reusable workflow accepts the following inputs:

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `python-version` | Python version to use | No | `3.11` |
| `config-path` | Path to custom configuration file | No | `` (uses default) |

## Workflow Outputs

| Output | Description | Value |
|--------|-------------|-------|
| `validation-status` | Overall validation status | `pass` or `fail` |

## Usage Examples

### Example 1: Basic Usage

```yaml
name: Validate

on: [pull_request, push]

jobs:
  validate:
    uses: ./.github/workflows/validate.yml
```

### Example 2: Custom Python Version

```yaml
jobs:
  validate:
    uses: ./.github/workflows/validate.yml
    with:
      python-version: '3.12'
```

### Example 3: Custom Configuration

```yaml
jobs:
  validate:
    uses: ./.github/workflows/validate.yml
    with:
      config-path: 'config/custom-rules.json'
```

### Example 4: Use Validation Status

```yaml
jobs:
  validate:
    uses: ./.github/workflows/validate.yml
  
  deploy:
    needs: validate
    if: needs.validate.outputs.validation-status == 'pass'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "Deploying..."
```

### Example 5: Multiple Validations

```yaml
jobs:
  validate-strict:
    uses: ./.github/workflows/validate.yml
    with:
      config-path: 'config/strict-rules.json'
  
  validate-lenient:
    uses: ./.github/workflows/validate.yml
    with:
      config-path: 'config/lenient-rules.json'
```

## Workflow Steps

The workflow performs the following steps:

### 1. Checkout Code
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full history for commit validation
```

### 2. Setup Python
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # Cache pip dependencies
```

### 3. Install Dependencies
```yaml
- run: |
    python -m pip install --upgrade pip
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
```

### 4. Run Validation
```yaml
- run: python src/main/cli.py --ci validate-all
```

### 5. Generate Report
- Creates job summary with validation results
- Uploads validation report as artifact
- Comments on PR with results (if applicable)

## Features in Detail

### Auto-Detection

The workflow automatically detects:
- **Current branch** from Git or environment variables
- **Latest commit** from Git history

No need to manually pass branch names or commit messages!

### PR Comments

For pull requests, the workflow automatically:
- Posts a comment with validation results
- Updates the comment on subsequent runs
- Includes detailed JSON output

Example comment:
```
## ✅ Git Workflow Validation PASSED

**Branch:** `feature/JIRA-123-add-feature`
**Commit:** `abc123...`

📋 Validation Details
{
  "branch": { "valid": true, "type": "feature" },
  "commit": { "valid": true, "type": "feat" },
  "overall": { "valid": true }
}
```

### Job Summaries

Each run creates a job summary with:
- Validation status
- Branch and event information
- Detailed JSON output
- Easy-to-read format

### Artifact Upload

Validation reports are uploaded as artifacts:
- **Name:** `validation-report`
- **File:** `validation-output.json`
- **Retention:** 30 days

Download artifacts via:
- GitHub Actions UI
- GitHub API
- GitHub CLI

## Triggers

The workflow can be triggered by:

### Pull Requests
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
```

### Push Events
```yaml
on:
  push:
    branches: [main, develop]
```

### Manual Trigger
```yaml
on:
  workflow_dispatch:
```

### Scheduled
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
```

### Workflow Call (Reusable)
```yaml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: '3.11'
```

## Status Badges

Add a status badge to your README:

```markdown
![Validation](https://github.com/username/repo/actions/workflows/validate.yml/badge.svg)
```

## Troubleshooting

### Validation Fails in CI but Passes Locally

**Possible causes:**
1. Different Python versions
2. Missing dependencies
3. Environment-specific issues

**Solutions:**
```yaml
# Match local Python version
with:
  python-version: '3.11'

# Install all dependencies
- run: pip install -r requirements.txt
```

### Cannot Detect Branch Name

**Possible causes:**
1. Detached HEAD state
2. Shallow clone

**Solutions:**
```yaml
# Fetch full history
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

### PR Comments Not Working

**Possible causes:**
1. Missing permissions
2. Fork PRs (security restriction)

**Solutions:**
```yaml
# Add permissions
permissions:
  pull-requests: write
  contents: read
```

### Validation Report Not Uploaded

**Possible causes:**
1. Validation failed before report generation
2. File path incorrect

**Solutions:**
```yaml
# Always upload, even on failure
- uses: actions/upload-artifact@v4
  if: always()
```

## Advanced Configuration

### Custom Validation Rules

Create a custom configuration file:

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

Use in workflow:
```yaml
with:
  config-path: 'config/custom-rules.json'
```

### Matrix Strategy

Validate with multiple configurations:

```yaml
jobs:
  validate:
    strategy:
      matrix:
        config: [strict, lenient, experimental]
    uses: ./.github/workflows/validate.yml
    with:
      config-path: 'config/${{ matrix.config }}-rules.json'
```

### Conditional Execution

Run validation only for specific branches:

```yaml
jobs:
  validate:
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/feature/')
    uses: ./.github/workflows/validate.yml
```

### Parallel Validation

Run multiple validations in parallel:

```yaml
jobs:
  validate-branch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python src/main/cli.py --ci validate-branch
  
  validate-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python src/main/cli.py --ci validate-commit
```

## Integration with Other Actions

### Slack Notifications

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ Validation failed for ${{ github.ref }}"
      }
```

### Teams Notifications

```yaml
- name: Notify Teams
  if: failure()
  uses: aliencube/microsoft-teams-actions@v0.8.0
  with:
    webhook_uri: ${{ secrets.TEAMS_WEBHOOK }}
    title: Validation Failed
```

### Email Notifications

```yaml
- name: Send Email
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    subject: Validation Failed
    body: Validation failed for ${{ github.ref }}
```

## Best Practices

1. **Always fetch full history** for commit validation
2. **Use caching** for pip dependencies
3. **Upload artifacts** for debugging
4. **Add status badges** to README
5. **Use reusable workflows** for consistency
6. **Set appropriate permissions** for PR comments
7. **Handle failures gracefully** with proper error messages
8. **Document custom configurations** in your repository

## Security Considerations

### Fork PRs

For security, GitHub restricts certain actions on fork PRs:
- Cannot write comments
- Cannot access secrets
- Limited permissions

**Solution:** Use `pull_request_target` with caution:
```yaml
on:
  pull_request_target:  # Use with caution!
```

### Secrets

Never expose secrets in validation output:
```yaml
- run: python src/main/cli.py --ci validate-all
  env:
    SECRET_TOKEN: ${{ secrets.TOKEN }}  # Not exposed in output
```

## Performance Optimization

### Cache Dependencies

```yaml
- uses: actions/setup-python@v5
  with:
    cache: 'pip'  # Cache pip packages
```

### Shallow Clone

For branch-only validation:
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 1  # Faster checkout
```

### Conditional Steps

Skip unnecessary steps:
```yaml
- name: Validate commits
  if: github.event_name == 'pull_request'
  run: python src/main/cli.py --ci validate-commit
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Project Repository](https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer)

## Support

For issues with the GitHub Action:
1. Check this documentation
2. Review workflow logs
3. Test locally with `--ci` flag
4. Check project issues on GitHub
5. Contact the development team
