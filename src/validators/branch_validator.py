"""
Branch Name Validator
Validates branch names against defined patterns

This module provides production-level validation for Git branch names
with regex-based pattern matching and Git integration.
"""

import re
import subprocess
import logging
from typing import Dict, List, Optional, Tuple


class BranchValidatorError(Exception):
    """Base exception for branch validator errors"""
    pass


class ConfigurationError(BranchValidatorError):
    """Raised when configuration is invalid or missing"""
    pass


class GitError(BranchValidatorError):
    """Raised when Git operations fail"""
    pass


class ValidationError(BranchValidatorError):
    """Raised when validation fails"""
    pass


class BranchValidator:
    """
    Validates branch names against defined patterns
    
    This validator uses regex patterns and configuration-driven rules
    to ensure branch names follow the required format.
    """

    def __init__(self, config: Dict):
        """
        Initialize the branch validator
        
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
            branches_config = config.get('branches', {})
            self.patterns = branches_config.get('patterns', {})
            self.protected = branches_config.get('protected', [])
            self.ticket_id_pattern = branches_config.get('ticketIdPattern', '[A-Z]+-[0-9]+')
            
            # Compile regex patterns for performance
            self._compile_patterns()
            
            self.logger.debug("BranchValidator initialized successfully")
            
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
        
        if 'branches' not in config:
            raise ConfigurationError("Missing 'branches' section in configuration")
        
        branches = config['branches']
        
        if 'patterns' not in branches or not branches['patterns']:
            raise ConfigurationError("Missing or empty 'patterns' in branches configuration")
        
        if not isinstance(branches['patterns'], dict):
            raise ConfigurationError("'patterns' must be a dictionary")
        
        if 'protected' not in branches:
            raise ConfigurationError("Missing 'protected' in branches configuration")
        
        if not isinstance(branches['protected'], list):
            raise ConfigurationError("'protected' must be a list")

    def _compile_patterns(self) -> None:
        """Compile regex patterns for better performance"""
        self.compiled_patterns = {}
        
        for branch_type, pattern in self.patterns.items():
            try:
                self.compiled_patterns[branch_type] = re.compile(pattern)
                self.logger.debug(f"Compiled pattern for {branch_type}: {pattern}")
            except re.error as e:
                raise ConfigurationError(f"Invalid regex pattern for {branch_type}: {e}")

    def get_current_branch(self) -> str:
        """
        Get the current Git branch name
        
        Returns:
            str: Current branch name
            
        Raises:
            GitError: If Git command fails or not in a Git repository
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            
            branch_name = result.stdout.strip()
            self.logger.debug(f"Current branch: {branch_name}")
            return branch_name
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            raise GitError(f"Failed to get current branch: {error_msg}")
        except subprocess.TimeoutExpired:
            raise GitError("Git command timed out")
        except FileNotFoundError:
            raise GitError("Git is not installed or not in PATH")
        except Exception as e:
            raise GitError(f"Unexpected error getting current branch: {e}")

    def validate(self, branch_name: Optional[str] = None) -> bool:
        """
        Validate a branch name
        
        Args:
            branch_name (str, optional): Branch name to validate. 
                                        If None, validates current Git branch.
            
        Returns:
            bool: True if valid, False if invalid
            
        Note:
            Prints detailed error messages to stdout if validation fails
        """
        try:
            # If no branch name provided, get current branch
            if branch_name is None:
                try:
                    branch_name = self.get_current_branch()
                    self.logger.info(f"Validating current branch: {branch_name}")
                except GitError as e:
                    print(f"\n❌ GIT ERROR")
                    print(f"Error: {e}")
                    return False
            
            result = self.validate_detailed(branch_name)
            
            if result['valid']:
                self.logger.info(f"✓ Valid branch name: {result['type']}")
                return True
            else:
                self._print_error(branch_name, result)
                return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            print(f"\n❌ VALIDATION ERROR")
            print(f"An unexpected error occurred: {e}")
            return False

    def validate_detailed(self, branch_name: str) -> Dict:
        """
        Validate a branch name and return detailed results
        
        Args:
            branch_name (str): Branch name to validate
            
        Returns:
            dict: Validation result with 'valid', 'type', 'error', and other keys
        """
        # Check for empty branch name
        if not branch_name or not branch_name.strip():
            return {
                'valid': False,
                'error': 'Branch name cannot be empty',
                'error_type': 'EMPTY_BRANCH_NAME',
                'examples': self._get_examples()
            }

        branch_name = branch_name.strip()

        # Check if protected branch
        if branch_name in self.protected:
            self.logger.debug(f"Protected branch: {branch_name}")
            return {
                'valid': True,
                'type': 'protected',
                'branch_name': branch_name
            }

        # Match against patterns
        for branch_type, compiled_pattern in self.compiled_patterns.items():
            match = compiled_pattern.match(branch_name)
            if match:
                self.logger.debug(f"Valid {branch_type} branch: {branch_name}")
                
                # Extract ticket ID if present
                ticket_id = self._extract_ticket_id(branch_name)
                
                return {
                    'valid': True,
                    'type': branch_type,
                    'branch_name': branch_name,
                    'ticket_id': ticket_id,
                    'pattern': self.patterns[branch_type]
                }

        # No match found
        return {
            'valid': False,
            'error': 'Branch name does not match any allowed pattern',
            'error_type': 'INVALID_PATTERN',
            'branch_name': branch_name,
            'examples': self._get_examples(),
            'patterns': self._get_pattern_descriptions()
        }

    def _extract_ticket_id(self, branch_name: str) -> Optional[str]:
        """
        Extract ticket ID from branch name
        
        Args:
            branch_name (str): Branch name
            
        Returns:
            str or None: Ticket ID if found
        """
        try:
            pattern = re.compile(self.ticket_id_pattern)
            match = pattern.search(branch_name)
            if match:
                return match.group(0)
        except Exception as e:
            self.logger.debug(f"Could not extract ticket ID: {e}")
        
        return None

    def _print_error(self, branch_name: str, result: Dict) -> None:
        """
        Print formatted error message
        
        Args:
            branch_name (str): Branch name that failed validation
            result (dict): Validation result
        """
        print("\n" + "=" * 70)
        print("❌ INVALID BRANCH NAME")
        print("=" * 70)
        
        print(f"\nYour branch:")
        print(f"  {branch_name}")
        
        print(f"\nError: {result['error']}")
        
        if 'patterns' in result:
            print(f"\nAllowed patterns:")
            for pattern_desc in result['patterns']:
                print(f"  • {pattern_desc}")
        
        if 'examples' in result and result['examples']:
            print(f"\nExamples:")
            for example in result['examples']:
                print(f"  ✓ {example}")
        
        print(f"\nTo rename your branch:")
        print(f"  git branch -m <new-branch-name>")
        
        print("\n" + "=" * 70 + "\n")

    def _get_examples(self) -> List[str]:
        """
        Get example branch names based on config
        
        Returns:
            list: Example branch names
        """
        examples = []
        
        # Add examples for each pattern type
        pattern_examples = {
            'feature': 'feature/JIRA-123-user-authentication',
            'bugfix': 'bugfix/PROJ-456-fix-login-error',
            'hotfix': 'hotfix/TICKET-789',
            'release': 'release/v1.2.0'
        }
        
        for branch_type in self.patterns.keys():
            if branch_type in pattern_examples:
                examples.append(pattern_examples[branch_type])
        
        # Add protected branches
        for protected in self.protected:
            examples.append(f"{protected} (protected)")
        
        return examples

    def _get_pattern_descriptions(self) -> List[str]:
        """
        Get human-readable pattern descriptions
        
        Returns:
            list: Pattern descriptions
        """
        descriptions = []
        
        pattern_desc = {
            'feature': 'feature/<TICKET-ID>-<description>',
            'bugfix': 'bugfix/<TICKET-ID>-<description>',
            'hotfix': 'hotfix/<TICKET-ID>',
            'release': 'release/v<version>'
        }
        
        for branch_type in self.patterns.keys():
            if branch_type in pattern_desc:
                descriptions.append(f"{branch_type.capitalize()}: {pattern_desc[branch_type]}")
        
        return descriptions

    def get_config_summary(self) -> str:
        """
        Get a summary of current configuration
        
        Returns:
            str: Configuration summary
        """
        summary = []
        summary.append("Branch Validator Configuration:")
        summary.append(f"  Branch types: {', '.join(self.patterns.keys())}")
        summary.append(f"  Protected branches: {', '.join(self.protected)}")
        summary.append(f"  Ticket ID pattern: {self.ticket_id_pattern}")
        return '\n'.join(summary)

    def validate_current_branch(self) -> bool:
        """
        Validate the current Git branch
        
        Returns:
            bool: True if valid, False if invalid
            
        Raises:
            GitError: If Git command fails
        """
        branch_name = self.get_current_branch()
        return self.validate(branch_name)
