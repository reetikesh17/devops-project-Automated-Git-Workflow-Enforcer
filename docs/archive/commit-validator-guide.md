# Commit Validator Module Guide

## Overview

The `commit_validator.py` module provides production-level validation for Git commit messages following the Conventional Commits specification. It uses regex-based validation with configuration-driven rules and comprehensive error handling.

## Features

- ✅ Regex-based validation using patterns from configuration
- ✅ No hardcoded values - fully configurable
- ✅ Returns boolean (True/False) for simple validation
- ✅ Provides detailed validation results with error types
- ✅ Clear, formatted error messages
- ✅ Production-level error handling with custom exceptions
- ✅ Support for commit scopes and breaking changes
- ✅ Comprehensive logging
- ✅ Type hints for better IDE support

## Installation

```python
from validators.commit_validator import CommitValidator
from config.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader.load()

# Create validator instance
validator = CommitValidator(config)
```

## Usage

### Basic Validation (Boolean Return)

```python
# Returns True if valid, False if invalid
is_valid = validator.validate("feat: add user authentication")

if is_valid:
    print("Commit message is valid!")
else:
    print("Commit message is invalid!")
```

### Detailed Validation (Dictionary Return)

```python
# Returns detailed validation results
result = validator.validate_detailed("feat: add user authentication")

if result['valid']:
    print(f"Type: {result['type']}")
    print(f"Description: {result['description']}")
else:
    print(f"Error: {result['error']}")
    print(f"Error Type: {result['error_type']}")
```

## Configuration

The validator reads all rules from `src/config/rules.json`:

```json
{
  "commits": {
    "types": ["feat", "fix", "chore", "docs", "refactor", "test", "ci"],
    "descriptionLength": {
      "min": 10,
      "max": 100
    },
    "enforceCase": "lowercase",
    "allowBreakingChanges": true
  }
}
```

### Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `types` | array | Allowed commit types |
| `descriptionLength.min` | integer | Minimum description length |
| `descriptionLength.max` | integer | Maximum description length |
| `enforceCase` | string | Case enforcement ("lowercase" or "none") |
| `allowBreakingChanges` | boolean | Allow breaking change indicator (!) |

## Validation Rules

### Format

```
<type>: <description>
<type>(<scope>): <description>
<type>!: <description> (breaking change)
```

### Rules Applied

1. **Type Validation**: Type must be in allowed types list
2. **Format Validation**: Must match `<type>: <description>` pattern
3. **Length Validation**: Description must be between min and max length
4. **Case Validation**: Description must start with lowercase (if enforced)
5. **Punctuation Validation**: Description must not end with period

## Error Types

The validator provides specific error types for different validation failures:

| Error Type | Description |
|------------|-------------|
| `EMPTY_MESSAGE` | Commit message is empty |
| `INVALID_FORMAT` | Message doesn't match expected format |
| `INVALID_TYPE` | Commit type not in allowed types |
| `DESCRIPTION_TOO_SHORT` | Description below minimum length |
| `DESCRIPTION_TOO_LONG` | Description exceeds maximum length |
| `INVALID_CASE` | Description doesn't follow case rules |
| `INVALID_PUNCTUATION` | Description has invalid punctuation |

## Return Values

### validate() Method

Returns `bool`:
- `True`: Message is valid
- `False`: Message is invalid (prints error details)

### validate_detailed() Method

Returns `dict` with the following structure:

**Valid Message:**
```python
{
    'valid': True,
    'type': 'feat',
    'scope': 'auth',  # Optional
    'breaking': False,
    'description': 'add user authentication',
    'full_message': 'feat(auth): add user authentication'
}
```

**Invalid Message:**
```python
{
    'valid': False,
    'error': 'Description too short (minimum 10 characters)',
    'error_type': 'DESCRIPTION_TOO_SHORT',
    'current_length': 5,
    'min_length': 10,
    'suggestions': [...]
}
```

## Exception Handling

### Custom Exceptions

```python
from validators.commit_validator import (
    CommitValidatorError,
    ConfigurationError,
    ValidationError
)

try:
    validator = CommitValidator(config)
    result = validator.validate(message)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except CommitValidatorError as e:
    print(f"Validator error: {e}")
```

### Exception Hierarchy

```
CommitValidatorError (base)
├── ConfigurationError
└── ValidationError
```

## Examples

### Example 1: Simple Validation

```python
from validators.commit_validator import CommitValidator
from config.config_loader import ConfigLoader

config = ConfigLoader.load()
validator = CommitValidator(config)

# Valid messages
print(validator.validate("feat: add login page"))  # True
print(validator.validate("fix: resolve bug in auth"))  # True

# Invalid messages
print(validator.validate("Add feature"))  # False
print(validator.validate("feat: short"))  # False
```

### Example 2: Detailed Validation

```python
result = validator.validate_detailed("feat: add user authentication")

if result['valid']:
    print(f"✓ Valid {result['type']} commit")
    print(f"  Description: {result['description']}")
else:
    print(f"✗ Invalid commit")
    print(f"  Error: {result['error']}")
    print(f"  Type: {result['error_type']}")
```

### Example 3: With Scope

```python
# Commit with scope
result = validator.validate_detailed("feat(auth): add login functionality")

if result['valid']:
    print(f"Type: {result['type']}")      # feat
    print(f"Scope: {result['scope']}")    # auth
    print(f"Description: {result['description']}")
```

### Example 4: Breaking Changes

```python
# Breaking change indicator
result = validator.validate_detailed("feat!: change API structure")

if result['valid']:
    print(f"Breaking change: {result['breaking']}")  # True
```

### Example 5: Error Handling

```python
try:
    validator = CommitValidator(invalid_config)
except ConfigurationError as e:
    print(f"Config error: {e}")
    # Handle configuration error
```

## Integration with Git Hooks

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/commit-msg

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

python -c "
import sys
sys.path.insert(0, 'src')
from validators.commit_validator import CommitValidator
from config.config_loader import ConfigLoader

config = ConfigLoader.load()
validator = CommitValidator(config)

if not validator.validate('$COMMIT_MSG'):
    sys.exit(1)
"

exit $?
```

## Testing

### Unit Tests

```python
import pytest
from validators.commit_validator import CommitValidator

def test_valid_commit():
    config = {'commits': {...}}
    validator = CommitValidator(config)
    assert validator.validate("feat: add feature") == True

def test_invalid_commit():
    validator = CommitValidator(config)
    assert validator.validate("invalid") == False
```

### Running Tests

```bash
# Run the example test suite
python examples/test_commit_validator.py

# Run with pytest
pytest tests/unit/validators/test_commit_validator.py
```

## Performance

- Regex compilation: Once during initialization
- Validation time: < 1ms per message
- Memory usage: Minimal (< 1MB)

## Best Practices

1. **Reuse Validator Instance**: Create once, use multiple times
2. **Handle Exceptions**: Always catch ConfigurationError
3. **Use Detailed Validation**: For programmatic error handling
4. **Configure Appropriately**: Adjust rules for your team
5. **Log Validation**: Enable logging for debugging

## Troubleshooting

### Common Issues

**Issue**: "Missing required configuration key"
```python
# Solution: Ensure config has all required keys
config = {
    'commits': {
        'types': [...],
        'descriptionLength': {'min': 10, 'max': 100}
    }
}
```

**Issue**: Regex not matching expected messages
```python
# Solution: Check allowed types in config
validator.get_config_summary()  # View current config
```

**Issue**: False positives/negatives
```python
# Solution: Use detailed validation to see exact error
result = validator.validate_detailed(message)
print(result['error_type'])
```

## API Reference

### CommitValidator Class

#### `__init__(config: Dict)`
Initialize validator with configuration.

**Raises**: `ConfigurationError` if config is invalid

#### `validate(message: str) -> bool`
Validate commit message, print errors if invalid.

**Returns**: `True` if valid, `False` if invalid

#### `validate_detailed(message: str) -> Dict`
Validate and return detailed results.

**Returns**: Dictionary with validation results

#### `get_config_summary() -> str`
Get human-readable configuration summary.

**Returns**: Configuration summary string

## Contributing

When modifying the validator:

1. Maintain backward compatibility
2. Add tests for new features
3. Update documentation
4. Follow existing code style
5. Handle errors gracefully

## License

MIT License - See LICENSE file for details
