"""
Unit tests for CommitValidator

Tests the commit message validation functionality with various
valid and invalid commit messages.
"""

import pytest
from src.validators.commit_validator import (
    CommitValidator,
    ConfigurationError,
    ValidationError
)


@pytest.fixture
def valid_config():
    """Fixture providing valid configuration"""
    return {
        'commits': {
            'types': ['feat', 'fix', 'chore', 'docs', 'refactor', 'test', 'ci'],
            'descriptionLength': {
                'min': 10,
                'max': 100
            },
            'enforceCase': 'lowercase',
            'allowBreakingChanges': True
        }
    }


@pytest.fixture
def validator(valid_config):
    """Fixture providing a CommitValidator instance"""
    return CommitValidator(valid_config)


class TestCommitValidatorInitialization:
    """Test validator initialization and configuration"""
    
    def test_valid_initialization(self, valid_config):
        """Test validator initializes with valid config"""
        validator = CommitValidator(valid_config)
        assert validator is not None
        assert validator.allowed_types == ['feat', 'fix', 'chore', 'docs', 'refactor', 'test', 'ci']
        assert validator.min_length == 10
        assert validator.max_length == 100
    
    def test_missing_commits_section(self):
        """Test initialization fails with missing commits section"""
        config = {}
        with pytest.raises(ConfigurationError, match="Missing 'commits' section"):
            CommitValidator(config)
    
    def test_missing_types(self):
        """Test initialization fails with missing types"""
        config = {
            'commits': {
                'descriptionLength': {'min': 10, 'max': 100}
            }
        }
        with pytest.raises(ConfigurationError, match="Missing or empty 'types'"):
            CommitValidator(config)
    
    def test_missing_description_length(self):
        """Test initialization fails with missing description length"""
        config = {
            'commits': {
                'types': ['feat', 'fix']
            }
        }
        with pytest.raises(ConfigurationError, match="Missing 'descriptionLength'"):
            CommitValidator(config)
    
    def test_invalid_length_constraints(self):
        """Test initialization fails with invalid length constraints"""
        config = {
            'commits': {
                'types': ['feat'],
                'descriptionLength': {'min': 100, 'max': 10}
            }
        }
        with pytest.raises(ConfigurationError, match="Invalid length constraints"):
            CommitValidator(config)


class TestValidCommitMessages:
    """Test validation of valid commit messages"""
    
    def test_valid_feat_commit(self, validator):
        """Test valid feat commit"""
        assert validator.validate("feat: add user authentication module") is True
    
    def test_valid_fix_commit(self, validator):
        """Test valid fix commit"""
        assert validator.validate("fix: resolve null pointer exception") is True
    
    def test_valid_chore_commit(self, validator):
        """Test valid chore commit"""
        assert validator.validate("chore: update dependencies to latest") is True
    
    def test_valid_docs_commit(self, validator):
        """Test valid docs commit"""
        assert validator.validate("docs: update installation guide") is True
    
    def test_valid_refactor_commit(self, validator):
        """Test valid refactor commit"""
        assert validator.validate("refactor: simplify validation logic") is True
    
    def test_valid_test_commit(self, validator):
        """Test valid test commit"""
        assert validator.validate("test: add unit tests for validator") is True
    
    def test_valid_ci_commit(self, validator):
        """Test valid ci commit"""
        assert validator.validate("ci: configure github actions workflow") is True
    
    def test_valid_commit_with_scope(self, validator):
        """Test valid commit with scope"""
        assert validator.validate("feat(auth): add login functionality") is True
    
    def test_valid_commit_with_breaking_change(self, validator):
        """Test valid commit with breaking change indicator"""
        assert validator.validate("feat!: change api structure completely") is True
    
    def test_valid_commit_minimum_length(self, validator):
        """Test valid commit at minimum length"""
        assert validator.validate("feat: add login page") is True  # 15 chars, > 10
    
    def test_valid_commit_maximum_length(self, validator):
        """Test valid commit at maximum length"""
        message = "feat: " + "a" * 94  # Description is 94 chars, total 100
        assert validator.validate(message) is True


class TestInvalidCommitMessages:
    """Test validation of invalid commit messages"""
    
    def test_empty_message(self, validator):
        """Test empty commit message"""
        assert validator.validate("") is False
    
    def test_whitespace_only_message(self, validator):
        """Test whitespace-only commit message"""
        assert validator.validate("   ") is False
    
    def test_invalid_format_no_colon(self, validator):
        """Test invalid format without colon"""
        assert validator.validate("feat add feature") is False
    
    def test_invalid_format_no_space_after_colon(self, validator):
        """Test invalid format without space after colon"""
        assert validator.validate("feat:add feature") is False
    
    def test_invalid_type(self, validator):
        """Test invalid commit type"""
        assert validator.validate("invalid: add something here") is False
    
    def test_description_too_short(self, validator):
        """Test description below minimum length"""
        assert validator.validate("feat: short") is False
    
    def test_description_too_long(self, validator):
        """Test description exceeds maximum length"""
        message = "feat: " + "a" * 101  # Description is 101 chars, > 100
        assert validator.validate(message) is False
    
    def test_description_starts_uppercase(self, validator):
        """Test description starting with uppercase"""
        assert validator.validate("feat: Add feature here") is False
    
    def test_description_ends_with_period(self, validator):
        """Test description ending with period"""
        assert validator.validate("feat: add feature here.") is False
    
    def test_no_description(self, validator):
        """Test commit with no description"""
        assert validator.validate("feat: ") is False


class TestDetailedValidation:
    """Test detailed validation results"""
    
    def test_valid_detailed_result(self, validator):
        """Test detailed result for valid commit"""
        result = validator.validate_detailed("feat: add user authentication")
        
        assert result['valid'] is True
        assert result['type'] == 'feat'
        assert result['description'] == 'add user authentication'
        assert result['breaking'] is False
    
    def test_valid_with_scope_detailed(self, validator):
        """Test detailed result with scope"""
        result = validator.validate_detailed("feat(auth): add login page")
        
        assert result['valid'] is True
        assert result['type'] == 'feat'
        assert result['scope'] == 'auth'
        assert result['description'] == 'add login page'
    
    def test_valid_with_breaking_change_detailed(self, validator):
        """Test detailed result with breaking change"""
        result = validator.validate_detailed("feat!: change api structure")
        
        assert result['valid'] is True
        assert result['breaking'] is True
    
    def test_invalid_format_detailed(self, validator):
        """Test detailed result for invalid format"""
        result = validator.validate_detailed("invalid message")
        
        assert result['valid'] is False
        assert result['error_type'] == 'INVALID_FORMAT'
        assert 'error' in result
    
    def test_invalid_type_detailed(self, validator):
        """Test detailed result for invalid type"""
        result = validator.validate_detailed("wrongtype: add something")
        
        assert result['valid'] is False
        assert result['error_type'] == 'INVALID_FORMAT'
    
    def test_too_short_detailed(self, validator):
        """Test detailed result for too short description"""
        result = validator.validate_detailed("feat: short")
        
        assert result['valid'] is False
        assert result['error_type'] == 'DESCRIPTION_TOO_SHORT'
        assert result['current_length'] == 5
        assert result['min_length'] == 10
    
    def test_too_long_detailed(self, validator):
        """Test detailed result for too long description"""
        message = "feat: " + "a" * 101  # Description is 101 chars
        result = validator.validate_detailed(message)
        
        assert result['valid'] is False
        assert result['error_type'] == 'DESCRIPTION_TOO_LONG'
        assert result['current_length'] == 101
        assert result['max_length'] == 100
    
    def test_invalid_case_detailed(self, validator):
        """Test detailed result for invalid case"""
        result = validator.validate_detailed("feat: Add feature")
        
        assert result['valid'] is False
        assert result['error_type'] == 'INVALID_CASE'
    
    def test_invalid_punctuation_detailed(self, validator):
        """Test detailed result for invalid punctuation"""
        result = validator.validate_detailed("feat: add feature.")
        
        assert result['valid'] is False
        assert result['error_type'] == 'INVALID_PUNCTUATION'
    
    def test_empty_message_detailed(self, validator):
        """Test detailed result for empty message"""
        result = validator.validate_detailed("")
        
        assert result['valid'] is False
        assert result['error_type'] == 'EMPTY_MESSAGE'


class TestConfigSummary:
    """Test configuration summary"""
    
    def test_get_config_summary(self, validator):
        """Test configuration summary generation"""
        summary = validator.get_config_summary()
        
        assert 'Commit Validator Configuration' in summary
        assert 'feat' in summary
        assert '10-100' in summary
        assert 'lowercase' in summary


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_multiline_commit_message(self, validator):
        """Test multiline commit message (only first line validated)"""
        message = "feat: add user authentication\n\nThis is the body\nWith multiple lines"
        assert validator.validate(message) is True
    
    def test_commit_with_special_characters(self, validator):
        """Test commit with special characters in description"""
        assert validator.validate("feat: add user@example.com validation") is True
    
    def test_commit_with_numbers(self, validator):
        """Test commit with numbers in description"""
        assert validator.validate("feat: add support for http2 protocol") is True
    
    def test_commit_with_hyphens(self, validator):
        """Test commit with hyphens in description"""
        assert validator.validate("feat: add multi-factor authentication") is True
    
    def test_scope_with_hyphens(self, validator):
        """Test scope with hyphens"""
        assert validator.validate("feat(user-auth): add login page") is True
    
    def test_scope_with_numbers(self, validator):
        """Test scope with numbers"""
        assert validator.validate("feat(api-v2): add new endpoints") is True


class TestCustomConfiguration:
    """Test with custom configurations"""
    
    def test_custom_types(self):
        """Test with custom commit types"""
        config = {
            'commits': {
                'types': ['feature', 'bugfix'],
                'descriptionLength': {'min': 5, 'max': 50},
                'enforceCase': 'lowercase',
                'allowBreakingChanges': False
            }
        }
        validator = CommitValidator(config)
        
        assert validator.validate("feature: add login") is True
        assert validator.validate("bugfix: fix error") is True
        assert validator.validate("feat: add login") is False
    
    def test_custom_length_constraints(self):
        """Test with custom length constraints"""
        config = {
            'commits': {
                'types': ['feat'],
                'descriptionLength': {'min': 5, 'max': 20},
                'enforceCase': 'lowercase',
                'allowBreakingChanges': True
            }
        }
        validator = CommitValidator(config)
        
        assert validator.validate("feat: short") is True
        assert validator.validate("feat: this is too long for config") is False
    
    def test_breaking_changes_disabled(self):
        """Test with breaking changes disabled"""
        config = {
            'commits': {
                'types': ['feat'],
                'descriptionLength': {'min': 10, 'max': 100},
                'enforceCase': 'lowercase',
                'allowBreakingChanges': False
            }
        }
        validator = CommitValidator(config)
        
        # Breaking change indicator should not be recognized
        result = validator.validate_detailed("feat!: change api structure")
        assert result['valid'] is False
