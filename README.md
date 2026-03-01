# Automated Git Workflow Enforcer

A Python CLI tool to enforce Git workflow standards by validating branch names and commit messages.

## Features

- ✅ Validate branch names against defined patterns
- ✅ Validate commit messages (Conventional Commits format)
- ✅ Clean CLI interface with argparse
- ✅ Configurable rules via JSON
- ✅ Proper exit codes for CI/CD integration
- ✅ Structured logging support
- ✅ Modular and extensible design

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer.git
cd devops-project-Automated-Git-Workflow-Enforcer

# Install in development mode
pip install -e .

# Install Git hooks (recommended)
./install-hooks.sh      # Linux/macOS
# or
install-hooks.bat       # Windows
```

### Using pip (after publishing)

```bash
pip install git-workflow-enforcer
```

## Usage

### Validate Commit Message

```bash
python src/main/cli.py validate-commit "feat: add user authentication"
```

### Validate Branch Name

```bash
python src/main/cli.py validate-branch feature/JIRA-123-add-login
```

### Validate Both

```bash
python src/main/cli.py validate-all feature/JIRA-123-login "feat: add login page"
```

### Options

```bash
# Use custom configuration file
python src/main/cli.py --config custom-rules.json validate-commit "feat: new feature"

# Enable verbose output
python src/main/cli.py --verbose validate-branch feature/TEST-001-example
```

## Branch Naming Rules

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<TICKET-ID>-<description>` | `feature/JIRA-123-user-auth` |
| Bugfix | `bugfix/<TICKET-ID>-<description>` | `bugfix/PROJ-456-fix-login` |
| Hotfix | `hotfix/<TICKET-ID>` | `hotfix/URGENT-789` |
| Release | `release/v<version>` | `release/v1.2.0` |

Protected branches: `main`, `master`, `develop`

## Commit Message Format

Format: `<type>: <description>`

Allowed types:
- `feat` - New feature
- `fix` - Bug fix
- `chore` - Maintenance
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Tests
- `ci` - CI/CD changes

Rules:
- Description: 10-100 characters
- Start with lowercase
- No period at the end

Examples:
```
✓ feat: add user authentication module
✓ fix: resolve null pointer in login handler
✓ docs: update API documentation
✗ Feature: Add login (wrong type)
✗ feat: Add (too short)
✗ feat: Add feature. (ends with period)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - validation passed |
| 1 | Validation error - invalid format |
| 2 | Configuration error - invalid config |
| 3 | Runtime error - unexpected error |
| 4 | Git error - git command failed |

## Configuration

Edit `src/config/rules.json` to customize validation rules:

```json
{
  "branches": {
    "patterns": {
      "feature": "^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$",
      "bugfix": "^bugfix/[A-Z]+-[0-9]+-[a-z0-9-]+$"
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

## Project Structure

```
src/
├── main/
│   └── cli.py                    # CLI entry point
├── validators/
│   ├── __init__.py
│   ├── commit_validator.py      # Commit message validator
│   └── branch_validator.py      # Branch name validator
└── config/
    ├── __init__.py
    ├── config_loader.py          # Configuration loader
    └── rules.json                # Validation rules
```

## Development

### Run Tests

```bash
# Install development dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/
```

## CI/CD Integration

Use in GitHub Actions:

```yaml
- name: Validate commit
  run: |
    python src/main/cli.py validate-commit "${{ github.event.head_commit.message }}"
```

Use in Jenkins:

```groovy
sh 'python src/main/cli.py validate-branch ${BRANCH_NAME}'
```

## Git Hooks

The project includes Git hooks for automatic validation:

- **commit-msg**: Validates commit messages before commit
- **pre-commit**: Validates branch name before commit
- **pre-push**: Validates branch name before push

### Install Hooks

```bash
# Linux/macOS
./install-hooks.sh

# Windows
install-hooks.bat
```

### Uninstall Hooks

```bash
# Linux/macOS
./uninstall-hooks.sh

# Windows
uninstall-hooks.bat
```

See [Hooks Guide](docs/hooks-guide.md) for detailed documentation.

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

Test statistics:
- Total tests: 103
- Commit validator: 46 tests
- Branch validator: 57 tests
- Pass rate: 100%

See [Testing Guide](docs/testing-guide.md) for detailed documentation.

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
