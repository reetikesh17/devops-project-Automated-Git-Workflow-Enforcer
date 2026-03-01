"""
Unit tests for BranchValidator

Tests the branch name validation functionality with various
valid and invalid branch names.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.validators.branch_validator import (
    BranchValidator,
    ConfigurationError,
    GitError
)


@pytest.fixture
def valid_config():
    """Fixture providing valid configuration"""
    return {
        'branches': {
            'patterns': {
                'feature': r'^feature/[A-Z]+-[0-9]+-[a-z0-9-]+$',
                'bugfix': r'^bugfix/[A-Z]+-[0-9]+-[a-z0-9-]+$',
                'hotfix': r'^hotfix/[A-Z]+-[0-9]+$',
                'release': r'^release/v[0-9]+\.[0-9]+\.[0-9]+(-[a-z0-9]+)?$'
            },
            'protected': ['main', 'master', 'develop'],
            'ticketIdPattern': '[A-Z]+-[0-9]+'
        }
    }


@pytest.fixture
def validator(valid_config):
    """Fixture providing a BranchValidator instance"""
    return BranchValidator(valid_config)


class TestBranchValidatorInitialization:
    """Test validator initialization and configuration"""
    
    def test_valid_initialization(self, valid_config):
        """Test validator initializes with valid config"""
        validator = BranchValidator(valid_config)
        assert validator is not None
        assert len(validator.patterns) == 4
        assert len(validator.protected) == 3
        assert validator.ticket_id_pattern == '[A-Z]+-[0-9]+'
    
    def test_missing_branches_section(self):
        """Test initialization fails with missing branches section"""
        config = {}
        with pytest.raises(ConfigurationError, match="Missing 'branches' section"):
            BranchValidator(config)
    
    def test_missing_patterns(self):
        """Test initialization fails with missing patterns"""
        config = {
            'branches': {
                'protected': ['main']
            }
        }
        with pytest.raises(ConfigurationError, match="Missing or empty 'patterns'"):
            BranchValidator(config)
    
    def test_missing_protected(self):
        """Test initialization fails with missing protected"""
        config = {
            'branches': {
                'patterns': {'feature': '^feature/.*$'}
            }
        }
        with pytest.raises(ConfigurationError, match="Missing 'protected'"):
            BranchValidator(config)
    
    def test_invalid_regex_pattern(self):
        """Test initialization fails with invalid regex"""
        config = {
            'branches': {
                'patterns': {'feature': '[invalid(regex'},
                'protected': ['main']
            }
        }
        with pytest.raises(ConfigurationError, match="Invalid regex pattern"):
            BranchValidator(config)
    
    def test_patterns_compiled(self, validator):
        """Test that patterns are compiled on initialization"""
        assert len(validator.compiled_patterns) == 4
        assert 'feature' in validator.compiled_patterns
        assert 'bugfix' in validator.compiled_patterns


class TestValidBranchNames:
    """Test validation of valid branch names"""
    
    def test_valid_feature_branch(self, validator):
        """Test valid feature branch"""
        assert validator.validate("feature/JIRA-123-user-authentication") is True
    
    def test_valid_feature_branch_different_ticket(self, validator):
        """Test valid feature branch with different ticket format"""
        assert validator.validate("feature/PROJ-456-add-login-page") is True
    
    def test_valid_bugfix_branch(self, validator):
        """Test valid bugfix branch"""
        assert validator.validate("bugfix/BUG-111-fix-login-error") is True
    
    def test_valid_hotfix_branch(self, validator):
        """Test valid hotfix branch"""
        assert validator.validate("hotfix/URGENT-999") is True
    
    def test_valid_release_branch(self, validator):
        """Test valid release branch"""
        assert validator.validate("release/v1.0.0") is True
    
    def test_valid_release_branch_with_prerelease(self, validator):
        """Test valid release branch with prerelease tag"""
        assert validator.validate("release/v1.0.0-beta") is True
        assert validator.validate("release/v2.3.1-rc1") is True
    
    def test_protected_branch_main(self, validator):
        """Test protected branch main"""
        assert validator.validate("main") is True
    
    def test_protected_branch_master(self, validator):
        """Test protected branch master"""
        assert validator.validate("master") is True
    
    def test_protected_branch_develop(self, validator):
        """Test protected branch develop"""
        assert validator.validate("develop") is True


class TestInvalidBranchNames:
    """Test validation of invalid branch names"""
    
    def test_empty_branch_name(self, validator):
        """Test empty branch name"""
        assert validator.validate("") is False
    
    def test_whitespace_only_branch(self, validator):
        """Test whitespace-only branch name"""
        assert validator.validate("   ") is False
    
    def test_invalid_format_no_prefix(self, validator):
        """Test invalid format without prefix"""
        assert validator.validate("add-feature") is False
    
    def test_feature_missing_ticket_id(self, validator):
        """Test feature branch missing ticket ID"""
        assert validator.validate("feature/add-login") is False
    
    def test_feature_invalid_ticket_format(self, validator):
        """Test feature branch with invalid ticket format"""
        assert validator.validate("feature/123-login") is False
    
    def test_feature_missing_description(self, validator):
        """Test feature branch missing description"""
        assert validator.validate("feature/JIRA-123") is False
    
    def test_bugfix_missing_ticket_id(self, validator):
        """Test bugfix branch missing ticket ID"""
        assert validator.validate("bugfix/fix-bug") is False
    
    def test_hotfix_missing_ticket_id(self, validator):
        """Test hotfix branch missing ticket ID"""
        assert validator.validate("hotfix/fix") is False
    
    def test_release_missing_v_prefix(self, validator):
        """Test release branch missing v prefix"""
        assert validator.validate("release/1.0.0") is False
    
    def test_release_invalid_version_format(self, validator):
        """Test release branch with invalid version format"""
        assert validator.validate("release/v1.0") is False
        assert validator.validate("release/v1") is False
    
    def test_random_branch_name(self, validator):
        """Test random branch name"""
        assert validator.validate("random-branch-name") is False
    
    def test_uppercase_in_description(self, validator):
        """Test uppercase letters in description"""
        assert validator.validate("feature/JIRA-123-Add-Login") is False


class TestDetailedValidation:
    """Test detailed validation results"""
    
    def test_valid_feature_detailed(self, validator):
        """Test detailed result for valid feature branch"""
        result = validator.validate_detailed("feature/JIRA-123-user-auth")
        
        assert result['valid'] is True
        assert result['type'] == 'feature'
        assert result['branch_name'] == "feature/JIRA-123-user-auth"
        assert result['ticket_id'] == 'JIRA-123'
    
    def test_valid_bugfix_detailed(self, validator):
        """Test detailed result for valid bugfix branch"""
        result = validator.validate_detailed("bugfix/PROJ-456-fix-error")
        
        assert result['valid'] is True
        assert result['type'] == 'bugfix'
        assert result['ticket_id'] == 'PROJ-456'
    
    def test_valid_hotfix_detailed(self, validator):
        """Test detailed result for valid hotfix branch"""
        result = validator.validate_detailed("hotfix/URGENT-789")
        
        assert result['valid'] is True
        assert result['type'] == 'hotfix'
        assert result['ticket_id'] == 'URGENT-789'
    
    def test_valid_release_detailed(self, validator):
        """Test detailed result for valid release branch"""
        result = validator.validate_detailed("release/v1.2.0")
        
        assert result['valid'] is True
        assert result['type'] == 'release'
        assert result['ticket_id'] is None  # Release branches don't have ticket IDs
    
    def test_protected_branch_detailed(self, validator):
        """Test detailed result for protected branch"""
        result = validator.validate_detailed("main")
        
        assert result['valid'] is True
        assert result['type'] == 'protected'
    
    def test_invalid_pattern_detailed(self, validator):
        """Test detailed result for invalid pattern"""
        result = validator.validate_detailed("invalid-branch")
        
        assert result['valid'] is False
        assert result['error_type'] == 'INVALID_PATTERN'
        assert 'error' in result
        assert 'examples' in result
    
    def test_empty_branch_detailed(self, validator):
        """Test detailed result for empty branch"""
        result = validator.validate_detailed("")
        
        assert result['valid'] is False
        assert result['error_type'] == 'EMPTY_BRANCH_NAME'


class TestGitIntegration:
    """Test Git integration functionality"""
    
    @patch('subprocess.run')
    def test_get_current_branch_success(self, mock_run, validator):
        """Test successful current branch detection"""
        mock_run.return_value = MagicMock(
            stdout="feature/JIRA-123-test\n",
            returncode=0
        )
        
        branch = validator.get_current_branch()
        assert branch == "feature/JIRA-123-test"
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
    
    @patch('subprocess.run')
    def test_get_current_branch_git_error(self, mock_run, validator):
        """Test Git error when getting current branch"""
        mock_run.side_effect = Exception("Git command failed")
        
        with pytest.raises(GitError):
            validator.get_current_branch()
    
    @patch('subprocess.run')
    def test_get_current_branch_not_git_repo(self, mock_run, validator):
        """Test error when not in Git repository"""
        mock_run.side_effect = FileNotFoundError()
        
        with pytest.raises(GitError, match="Git is not installed"):
            validator.get_current_branch()
    
    @patch.object(BranchValidator, 'get_current_branch')
    def test_validate_current_branch_valid(self, mock_get_branch, validator):
        """Test validating current branch when valid"""
        mock_get_branch.return_value = "feature/JIRA-123-test"
        
        assert validator.validate_current_branch() is True
    
    @patch.object(BranchValidator, 'get_current_branch')
    def test_validate_current_branch_invalid(self, mock_get_branch, validator):
        """Test validating current branch when invalid"""
        mock_get_branch.return_value = "invalid-branch"
        
        assert validator.validate_current_branch() is False
    
    @patch.object(BranchValidator, 'get_current_branch')
    def test_validate_without_branch_name(self, mock_get_branch, validator):
        """Test validate() without branch name uses current branch"""
        mock_get_branch.return_value = "main"
        
        assert validator.validate() is True
        mock_get_branch.assert_called_once()


class TestTicketIdExtraction:
    """Test ticket ID extraction"""
    
    def test_extract_ticket_id_feature(self, validator):
        """Test ticket ID extraction from feature branch"""
        ticket_id = validator._extract_ticket_id("feature/JIRA-123-description")
        assert ticket_id == "JIRA-123"
    
    def test_extract_ticket_id_bugfix(self, validator):
        """Test ticket ID extraction from bugfix branch"""
        ticket_id = validator._extract_ticket_id("bugfix/PROJ-456-fix")
        assert ticket_id == "PROJ-456"
    
    def test_extract_ticket_id_hotfix(self, validator):
        """Test ticket ID extraction from hotfix branch"""
        ticket_id = validator._extract_ticket_id("hotfix/URGENT-789")
        assert ticket_id == "URGENT-789"
    
    def test_extract_ticket_id_none(self, validator):
        """Test ticket ID extraction when none present"""
        ticket_id = validator._extract_ticket_id("release/v1.0.0")
        assert ticket_id is None
    
    def test_extract_ticket_id_invalid_format(self, validator):
        """Test ticket ID extraction with invalid format"""
        ticket_id = validator._extract_ticket_id("feature/123-description")
        assert ticket_id is None


class TestConfigSummary:
    """Test configuration summary"""
    
    def test_get_config_summary(self, validator):
        """Test configuration summary generation"""
        summary = validator.get_config_summary()
        
        assert 'Branch Validator Configuration' in summary
        assert 'feature' in summary
        assert 'main' in summary
        assert '[A-Z]+-[0-9]+' in summary


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_branch_with_multiple_hyphens(self, validator):
        """Test branch with multiple hyphens in description"""
        assert validator.validate("feature/JIRA-123-multi-word-description") is True
    
    def test_branch_with_numbers_in_description(self, validator):
        """Test branch with numbers in description"""
        assert validator.validate("feature/JIRA-123-add-http2-support") is True
    
    def test_ticket_id_with_long_prefix(self, validator):
        """Test ticket ID with long prefix"""
        assert validator.validate("feature/PROJECT-999-description") is True
    
    def test_release_with_patch_version(self, validator):
        """Test release with patch version"""
        assert validator.validate("release/v1.2.3") is True
    
    def test_release_with_prerelease_alpha(self, validator):
        """Test release with alpha prerelease"""
        assert validator.validate("release/v1.0.0-alpha") is True
    
    def test_whitespace_trimming(self, validator):
        """Test that whitespace is trimmed"""
        assert validator.validate("  main  ") is True


class TestCustomConfiguration:
    """Test with custom configurations"""
    
    def test_custom_patterns(self):
        """Test with custom branch patterns"""
        config = {
            'branches': {
                'patterns': {
                    'task': r'^task/[0-9]+-.*$'
                },
                'protected': ['main'],
                'ticketIdPattern': '[0-9]+'
            }
        }
        validator = BranchValidator(config)
        
        assert validator.validate("task/123-description") is True
        assert validator.validate("feature/JIRA-123-desc") is False
    
    def test_custom_protected_branches(self):
        """Test with custom protected branches"""
        config = {
            'branches': {
                'patterns': {
                    'feature': r'^feature/.*$'
                },
                'protected': ['production', 'staging'],
                'ticketIdPattern': '[A-Z]+-[0-9]+'
            }
        }
        validator = BranchValidator(config)
        
        assert validator.validate("production") is True
        assert validator.validate("staging") is True
        assert validator.validate("main") is False
    
    def test_custom_ticket_pattern(self):
        """Test with custom ticket ID pattern"""
        config = {
            'branches': {
                'patterns': {
                    'feature': r'^feature/[0-9]+-.*$'
                },
                'protected': ['main'],
                'ticketIdPattern': '[0-9]+'
            }
        }
        validator = BranchValidator(config)
        
        result = validator.validate_detailed("feature/12345-description")
        assert result['valid'] is True
        assert result['ticket_id'] == '12345'


class TestPatternDescriptions:
    """Test pattern description generation"""
    
    def test_get_pattern_descriptions(self, validator):
        """Test pattern descriptions are generated"""
        descriptions = validator._get_pattern_descriptions()
        
        assert len(descriptions) > 0
        assert any('feature' in desc.lower() for desc in descriptions)
        assert any('bugfix' in desc.lower() for desc in descriptions)
    
    def test_get_examples(self, validator):
        """Test example generation"""
        examples = validator._get_examples()
        
        assert len(examples) > 0
        assert any('feature/' in ex for ex in examples)
        assert any('protected' in ex for ex in examples)
