# Git Workflow Enforcer - GitHub Action

[![GitHub Action](https://img.shields.io/badge/action-marketplace-blue.svg)](https://github.com/marketplace/actions/git-workflow-enforcer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Automatically validate Git branch names and commit messages in your CI/CD pipeline using Conventional Commits specification.

## Features

- ✅ **Branch Name Validation** - Enforce naming conventions
- ✅ **Commit Message Validation** - Follow Conventional Commits
- ✅ **Auto-Detection** - Automatically detects branch and commit
- ✅ **Customizable Rules** - Use your own configuration
- ✅ **CI/CD Ready** - Works with all major CI platforms
- ✅ **Zero Configuration** - Works out of the box
- ✅ **Detailed Output** - JSON output for easy parsing

## Quick Start

```yaml
name: Validate

on: [pull_request, push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate Git Workflow
        uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
```

That's it! The action will automatically:
- Detect your current branch
- Detect your latest commit message
- Validate both against standard rules
- Fail if validation fails

## Usage

### Basic Usage

```yaml
- uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
```

### With Custom Configuration

```yaml
- uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    config-path: '.github/validation-rules.json'
```

### Validate Branch Only

```yaml
- uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    validate-commit: false
```

### Validate Commit Only

```yaml
- uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    validate-branch: false
```

### Use Outputs

```yaml
- name: Validate
  id: validate
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1

- name: Deploy if Valid
  if: steps.validate.outputs.validation-status == 'pass'
  run: echo "Deploying..."
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

| Output | Description |
|--------|-------------|
| `validation-status` | Overall validation status (`pass` or `fail`) |
| `branch-valid` | Branch validation result (`true` or `false`) |
| `commit-valid` | Commit validation result (`true` or `false`) |
| `validation-output` | Full validation output (JSON) |

## Default Rules

### Branch Names

- `feature/<TICKET-ID>-<description>` - New features
- `bugfix/<TICKET-ID>-<description>` - Bug fixes
- `hotfix/<TICKET-ID>` - Critical fixes
- `release/v<version>` - Release branches
- `main`, `master`, `develop` - Protected branches (always valid)

**Examples:**
- ✅ `feature/JIRA-123-user-authentication`
- ✅ `bugfix/PROJ-456-fix-login-error`
- ✅ `hotfix/URGENT-789`
- ✅ `release/v1.2.0`
- ❌ `add-feature` (invalid format)
- ❌ `feature/add-login` (missing ticket ID)

### Commit Messages

Format: `<type>: <description>`

**Allowed types:**
- `feat` - New feature
- `fix` - Bug fix
- `chore` - Maintenance
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Tests
- `ci` - CI/CD changes

**Rules:**
- Description: 10-100 characters
- Start with lowercase
- No period at end

**Examples:**
- ✅ `feat: add user authentication module`
- ✅ `fix: resolve null pointer exception`
- ✅ `docs: update installation guide`
- ❌ `Add feature` (invalid format)
- ❌ `feat: short` (too short)
- ❌ `feat: Add Feature` (uppercase)

## Custom Configuration

Create a configuration file (e.g., `.github/validation-rules.json`):

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

Use in workflow:

```yaml
- uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1
  with:
    config-path: '.github/validation-rules.json'
```

## Examples

### Pull Request Validation

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
```

### Matrix Testing

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

### Conditional Deployment

```yaml
- name: Validate
  id: validate
  uses: reetikesh17/devops-project-Automated-Git-Workflow-Enforcer@v1

- name: Deploy
  if: steps.validate.outputs.validation-status == 'pass'
  run: |
    echo "Deploying to production..."
```

## Documentation

- [Action Usage Guide](docs/action-usage.md) - Detailed usage examples
- [GitHub Action Guide](docs/github-action-guide.md) - Workflow integration
- [CI/CD Integration](docs/ci-cd-integration.md) - Platform-specific guides
- [Design Document](docs/design-document.md) - Technical details

## Support

- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer/issues)
- 💬 [Discussions](https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## Credits

Developed by the DevOps Team as part of the Automated Git Workflow Enforcer project.
