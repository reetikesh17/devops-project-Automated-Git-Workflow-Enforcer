"""
Commit Message Validator
Validates commit messages against Conventional Commits format

This module provides production-level validation for Git commit messages
following the Conventional Commits specification.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple


class CommitValidatorError(Exception):
    """Base exception for commit validator errors"""
    pass


class ConfigurationError(CommitValidatorError):
    """Raised when configuration is invalid or missing"""
    pass


class ValidationError(CommitValidatorError):
    """Raised when validation fails"""
    pass


class CommitValidator:
    """
    Validates commit messages against Conventional Commits specification
    
    This validator uses regex patterns and configuration-driven rules
    to ensure commit messages follow the required format.
    """

    def __init__(self, config: Dict):
        """
        Initialize the commit validator
        
        Args:
            config (dict): Configuration dictionary containing validation rules
            
        Raises:
            ConfigurationError: If configuration is invalid or missing required keys
        """
        self.logger = logging.getLogger(__name__)
        
        try:
            self._validate_config(config)
            self.config = config
            
            # Load configuration values
            commits_config = config.get('commits', {})
            self.allowed_types = commits_config.get('types', [])
            
            length_config = commits_config.get('descriptionLength', {})
            self.min_length = length_config.get('min')
            self.max_length = length_config.get('max')
            
            self.enforce_case = commits_config.get('enforceCase', 'lowercase')
            self.allow_breaking_changes = commits_config.get('allowBreakingChanges', True)
            
            # Build regex pattern from config
            self._build_regex_pattern()
            
            self.logger.debug("CommitValidator initialized successfully")
            
        except KeyError as e:
            raise ConfigurationError(f"Missing required configuration key: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize validator: {e}")

    def _validate_config(self, config: Dict) -> None:
        """
        Validate configuration structure
        
        Args:
            config (dict): Configuration to validate
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration must be a dictionary")
        
        if 'commits' not in config:
            raise ConfigurationError("Missing 'commits' section in configuration")
        
        commits = config['commits']
        
        if 'types' not in commits or not commits['types']:
            raise ConfigurationError("Missing or empty 'types' in commits configuration")
        
        if not isinstance(commits['types'], list):
            raise ConfigurationError("'types' must be a list")
        
        if 'descriptionLength' not in commits:
            raise ConfigurationError("Missing 'descriptionLength' in commits configuration")
        
        length = commits['descriptionLength']
        if 'min' not in length or 'max' not in length:
            raise ConfigurationError("'descriptionLength' must contain 'min' and 'max'")
        
        if not isinstance(length['min'], int) or not isinstance(length['max'], int):
            raise ConfigurationError("'min' and 'max' length must be integers")
        
        if length['min'] < 1 or length['max'] < length['min']:
            raise ConfigurationError("Invalid length constraints")

    def _build_regex_pattern(self) -> None:
        """Build regex pattern from configuration"""
        # Create pattern with allowed types from config
        types_pattern = '|'.join(re.escape(t) for t in self.allowed_types)
        
        # Pattern: <type>: <description>
        # Optional scope: <type>(<scope>): <description>
        # Optional breaking change: <type>!: <description>
        if self.allow_breaking_changes:
            self.pattern = re.compile(
                rf'^({types_pattern})(\([a-z0-9-]+\))?(!)?:\s+(.+)$',
                re.MULTILINE
            )
        else:
            self.pattern = re.compile(
                rf'^({types_pattern})(\([a-z0-9-]+\))?:\s+(.+)$',
                re.MULTILINE
            )
        
        self.logger.debug(f"Regex pattern built: {self.pattern.pattern}")

    def validate(self, message: str) -> bool:
        """
        Validate a commit message
        
        Args:
            message (str): Commit message to validate
            
        Returns:
            bool: True if valid, False if invalid
            
        Note:
            Prints detailed error messages to stdout if validation fails
        """
        try:
            result = self.validate_detailed(message)
            
            if result['valid']:
                self.logger.info(f"✓ Valid commit message: {result['type']}")
                return True
            else:
                self._print_error(message, result)
                return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            print(f"\n❌ VALIDATION ERROR")
            print(f"An unexpected error occurred: {e}")
            return False

    def validate_detailed(self, message: str) -> Dict:
        """
        Validate a commit message and return detailed results
        
        Args:
            message (str): Commit message to validate
            
        Returns:
            dict: Validation result with 'valid', 'type', 'error', and other keys
        """
        # Check for empty message
        if not message or not message.strip():
            return {
                'valid': False,
                'error': 'Commit message cannot be empty',
                'error_type': 'EMPTY_MESSAGE',
                'suggestions': self._get_suggestions()
            }

        message = message.strip()

        # Parse the commit message
        parsed = self._parse_message(message)

        if not parsed:
            return {
                'valid': False,
                'error': 'Invalid commit message format',
                'error_type': 'INVALID_FORMAT',
                'expected_format': '<type>: <description>',
                'suggestions': self._get_suggestions()
            }

        commit_type = parsed['type']
        scope = parsed.get('scope')
        breaking = parsed.get('breaking', False)
        description = parsed['description']

        # Validate type
        if commit_type not in self.allowed_types:
            return {
                'valid': False,
                'error': f"Invalid commit type '{commit_type}'",
                'error_type': 'INVALID_TYPE',
                'allowed_types': self.allowed_types,
                'suggestions': [
                    f"Allowed types: {', '.join(self.allowed_types)}",
                    f"Example: feat: {description}"
                ]
            }

        # Validate description length
        desc_length = len(description)
        
        if desc_length < self.min_length:
            return {
                'valid': False,
                'error': f"Description too short (minimum {self.min_length} characters)",
                'error_type': 'DESCRIPTION_TOO_SHORT',
                'current_length': desc_length,
                'min_length': self.min_length,
                'suggestions': [
                    f"Current: {desc_length} characters, Required: {self.min_length}+",
                    "Add more detail to your commit message"
                ]
            }

        if desc_length > self.max_length:
            return {
                'valid': False,
                'error': f"Description too long (maximum {self.max_length} characters)",
                'error_type': 'DESCRIPTION_TOO_LONG',
                'current_length': desc_length,
                'max_length': self.max_length,
                'suggestions': [
                    f"Current: {desc_length} characters, Maximum: {self.max_length}",
                    "Make your commit message more concise"
                ]
            }

        # Validate description format based on config
        if self.enforce_case == 'lowercase' and description[0].isupper():
            return {
                'valid': False,
                'error': 'Description should start with lowercase letter',
                'error_type': 'INVALID_CASE',
                'suggestions': [
                    f"Try: {commit_type}: {description[0].lower()}{description[1:]}"
                ]
            }

        if description.endswith('.'):
            return {
                'valid': False,
                'error': 'Description should not end with a period',
                'error_type': 'INVALID_PUNCTUATION',
                'suggestions': [
                    f"Try: {commit_type}: {description[:-1]}"
                ]
            }

        self.logger.debug(f"Valid commit: {commit_type}{scope or ''}: {description}")

        return {
            'valid': True,
            'type': commit_type,
            'scope': scope,
            'breaking': breaking,
            'description': description,
            'full_message': message
        }

    def _parse_message(self, message: str) -> Optional[Dict]:
        """
        Parse commit message using regex
        
        Args:
            message (str): Commit message
            
        Returns:
            dict or None: Parsed message components
        """
        try:
            match = self.pattern.match(message)
            
            if not match:
                return None
            
            groups = match.groups()
            
            # Handle both patterns (with and without breaking change)
            if self.allow_breaking_changes and len(groups) == 4:
                commit_type, scope, breaking, description = groups
                return {
                    'type': commit_type,
                    'scope': scope[1:-1] if scope else None,  # Remove parentheses
                    'breaking': breaking == '!',
                    'description': description.split('\n')[0]  # Only first line
                }
            elif len(groups) == 3:
                commit_type, scope, description = groups
                return {
                    'type': commit_type,
                    'scope': scope[1:-1] if scope else None,
                    'breaking': False,
                    'description': description.split('\n')[0]
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error parsing message: {e}")
            return None

    def _print_error(self, message: str, result: Dict) -> None:
        """
        Print formatted error message
        
        Args:
            message (str): Original commit message
            result (dict): Validation result
        """
        print("\n" + "=" * 70)
        print("❌ INVALID COMMIT MESSAGE")
        print("=" * 70)
        
        print(f"\nYour message:")
        print(f"  {message[:100]}{'...' if len(message) > 100 else ''}")
        
        print(f"\nError: {result['error']}")
        
        if 'expected_format' in result:
            print(f"\nExpected format:")
            print(f"  {result['expected_format']}")
        
        if 'allowed_types' in result:
            print(f"\nAllowed types:")
            for t in result['allowed_types']:
                print(f"  • {t}")
        
        if 'current_length' in result:
            print(f"\nLength: {result['current_length']} characters")
            if 'min_length' in result:
                print(f"Minimum: {result['min_length']} characters")
            if 'max_length' in result:
                print(f"Maximum: {result['max_length']} characters")
        
        if 'suggestions' in result and result['suggestions']:
            print(f"\nSuggestions:")
            for suggestion in result['suggestions']:
                print(f"  • {suggestion}")
        
        print("\n" + "=" * 70 + "\n")

    def _get_suggestions(self) -> List[str]:
        """
        Get example commit messages based on config
        
        Returns:
            list: Example commit messages
        """
        examples = []
        example_descriptions = [
            "add user authentication module",
            "resolve null pointer in login handler",
            "update API documentation",
            "simplify validation logic",
            "add unit tests for validator",
            "update dependencies",
            "configure GitHub Actions workflow"
        ]
        
        for i, commit_type in enumerate(self.allowed_types):
            if i < len(example_descriptions):
                examples.append(f"{commit_type}: {example_descriptions[i]}")
        
        return examples

    def get_config_summary(self) -> str:
        """
        Get a summary of current configuration
        
        Returns:
            str: Configuration summary
        """
        summary = []
        summary.append("Commit Validator Configuration:")
        summary.append(f"  Allowed types: {', '.join(self.allowed_types)}")
        summary.append(f"  Description length: {self.min_length}-{self.max_length} characters")
        summary.append(f"  Enforce case: {self.enforce_case}")
        summary.append(f"  Allow breaking changes: {self.allow_breaking_changes}")
        return '\n'.join(summary)
