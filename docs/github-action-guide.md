# GitHub Actions Guide

## Workflow

The workflow at `.github/workflows/validate.yml` runs automatically on push to `main`/`develop` and on pull requests.

It validates:
- Branch name
- Commit message

## Trigger it manually

Push any commit to `main` or `develop`, or open a pull request.

## Workflow file

```yaml
name: Validate Git Workflow

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

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

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate branch
        run: python -m src.main.cli validate-branch "${{ github.ref_name }}"

      - name: Validate commit
        run: python -m src.main.cli validate-commit "${{ github.event.head_commit.message }}"
```

## Reusable workflow

```yaml
jobs:
  validate:
    uses: ./.github/workflows/validate.yml
```

## Status badge

```markdown
![Validate](https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer/actions/workflows/validate.yml/badge.svg)
```
