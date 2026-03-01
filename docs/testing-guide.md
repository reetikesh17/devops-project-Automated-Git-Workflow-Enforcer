# Testing Guide

## Overview

This document describes the testing strategy and how to run tests for the Automated Git Workflow Enforcer project.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Pytest configuration and shared fixtures
├── unit/
│   ├── __init__.py
│   └── validators/
│       ├── __init__.py
│       ├── test_commit_validator.py    # 46 tests
│       └── test_branch_validator.py    # 57 tests
└── integration/                   # (Future)
```

## Test Statistics

- Total Tests: 103
- Commit Validator Tests: 46
- Branch Validator Tests: 57
- Pass Rate: 100%

## Running Tests

### Install Dependencies

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Files

```bash
# Run commit validator tests only
pytest tests/unit/validators/test_commit_validator.py

# Run branch validator tests only
pytest tests/unit/validators/test_branch_validator.py
```

### Run Specific Test Classes

```bash
# Run specific test class
pytest tests/unit/validators/test_commit_validator.py::TestValidCommitMessages

# Run specific test method
pytest tests/unit/validators/test_commit_validator.py::TestValidCommitMessages::test_valid_feat_commit
```

## Test Coverage

### Commit Validator Tests (46 tests)

**Initialization Tests (5 tests)**
- Valid configuration
- Missing configuration sections
- Invalid configuration values

**Valid Message Tests (11 tests)**
- All commit types (feat, fix, chore, docs, refactor, test, ci)
- Commits with scope
- Commits with breaking changes
- Minimum and maximum length validation

**Invalid Message Tests (10 tests)**
- Empty messages
- Invalid format
- Invalid types
- Length violations
- Case violations
- Punctuation violations

**Detailed Validation Tests (10 tests)**
- Detailed results for valid messages
- Detailed results for invalid messages
- Error type classification

**Edge Cases (6 tests)**
- Multiline messages
- Special characters
- Numbers and hyphens
- Scope variations

**Custom Configuration (3 tests)**
- Custom commit types
- Custom length constraints
- Breaking changes disabled

### Branch Validator Tests (57 tests)

**Initialization Tests (6 tests)**
- Valid configuration
- Missing configuration sections
- Invalid regex patterns
- Pattern compilation

**Valid Branch Tests (9 tests)**
- Feature branches
- Bugfix branches
- Hotfix branches
- Release branches
- Protected branches

**Invalid Branch Tests (12 tests)**
- Empty branch names
- Missing ticket IDs
- Invalid formats
- Invalid version formats

**Detailed Validation Tests (7 tests)**
- Detailed results for all branch types
- Error type classification
- Ticket ID extraction

**Git Integration Tests (6 tests)**
- Current branch detection
- Git error handling
- Validation without branch name

**Ticket ID Extraction Tests (5 tests)**
- Extraction from different branch types
- Invalid format handling

**Edge Cases (6 tests)**
- Multiple hyphens
- Numbers in descriptions
- Whitespace trimming
- Prerelease versions

**Custom Configuration (3 tests)**
- Custom patterns
- Custom protected branches
- Custom ticket patterns

**Helper Methods (3 tests)**
- Pattern descriptions
- Example generation
- Config summary

## Test Fixtures

### Shared Fixtures (conftest.py)

```python
# Automatically adds src to Python path
# Configures pytest markers
```

### Validator Fixtures

```python
@pytest.fixture
def valid_config():
    """Provides valid configuration for tests"""
    
@pytest.fixture
def validator(valid_config):
    """Provides initialized validator instance"""
```

## Mocking

Tests use `unittest.mock` for Git operations:

```python
@patch('subprocess.run')
def test_get_current_branch_success(mock_run, validator):
    mock_run.return_value = MagicMock(stdout="main\n")
    branch = validator.get_current_branch()
    assert branch == "main"
```

## Test Markers

```python
# Mark as unit test
@pytest.mark.unit
def test_something():
    pass

# Mark as integration test
@pytest.mark.integration
def test_integration():
    pass

# Mark as slow test
@pytest.mark.slow
def test_slow_operation():
    pass
```

Run specific markers:

```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Writing New Tests

### Test Structure

```python
class TestFeatureName:
    """Test description"""
    
    def test_specific_behavior(self, validator):
        """Test specific behavior description"""
        # Arrange
        input_data = "test input"
        
        # Act
        result = validator.validate(input_data)
        
        # Assert
        assert result is True
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Clear test names** describing what is being tested
3. **Use fixtures** for common setup
4. **Test both success and failure** cases
5. **Test edge cases** and boundary conditions
6. **Mock external dependencies** (Git, file system)
7. **Keep tests independent** - no test should depend on another

### Example Test

```python
def test_valid_feature_branch(self, validator):
    """Test that a valid feature branch passes validation"""
    # Arrange
    branch_name = "feature/JIRA-123-add-login"
    
    # Act
    result = validator.validate(branch_name)
    
    # Assert
    assert result is True
```

## Debugging Tests

### Run with verbose output

```bash
pytest tests/ -vv
```

### Show print statements

```bash
pytest tests/ -s
```

### Stop on first failure

```bash
pytest tests/ -x
```

### Run last failed tests

```bash
pytest tests/ --lf
```

### Run with debugger

```bash
pytest tests/ --pdb
```

## Coverage Reports

### Generate HTML coverage report

```bash
pytest tests/ --cov=src --cov-report=html
```

View report:
```bash
# Open htmlcov/index.html in browser
```

### Generate terminal coverage report

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Test Performance

Current test performance:
- All tests: ~0.4 seconds
- Commit validator tests: ~0.37 seconds
- Branch validator tests: ~0.26 seconds

## Future Testing

### Integration Tests (Planned)

- End-to-end CLI testing
- Git hook integration
- Configuration file loading
- Error handling workflows

### Performance Tests (Planned)

- Validation speed benchmarks
- Large commit message handling
- Regex performance testing

## Troubleshooting

### Import Errors

If you get import errors, ensure `conftest.py` is properly configured:

```python
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))
```

### Fixture Not Found

Ensure fixtures are defined in:
- Same test file
- `conftest.py` in same directory
- `conftest.py` in parent directory

### Mock Not Working

Ensure you're patching the correct path:

```python
# Patch where it's used, not where it's defined
@patch('src.validators.branch_validator.subprocess.run')
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain test coverage above 90%
4. Update this documentation
