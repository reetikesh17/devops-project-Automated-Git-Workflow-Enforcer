"""
Branch Name Validator
Validates branch names against defined patterns
"""

import re
import logging


class BranchValidator:
    """Validates branch names"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.patterns = config.get('branches', {}).get('patterns', {})
        self.protected = config.get('branches', {}).get('protected', [])

    def validate(self, branch_name):
        """
        Validate a branch name

        Args:
            branch_name (str): Branch name to validate

        Returns:
            dict: Validation result with 'valid', 'type', 'error', and 'examples' keys
        """
        if not branch_name or not branch_name.strip():
            return {
                'valid': False,
                'error': 'Branch name cannot be empty',
                'examples': self._get_examples()
            }

        branch_name = branch_name.strip()

        # Check if protected branch
        if branch_name in self.protected:
            self.logger.debug(f"Protected branch: {branch_name}")
            return {
                'valid': True,
                'type': 'protected'
            }

        # Match against patterns
        for branch_type, pattern in self.patterns.items():
            if re.match(pattern, branch_name):
                self.logger.debug(f"Valid {branch_type} branch: {branch_name}")
                return {
                    'valid': True,
                    'type': branch_type
                }

        # No match found
        return {
            'valid': False,
            'error': 'Branch name does not match any allowed pattern',
            'examples': self._get_examples()
        }

    def _get_examples(self):
        """Get example branch names"""
        return [
            "feature/JIRA-123-user-authentication",
            "bugfix/PROJ-456-fix-login-error",
            "hotfix/TICKET-789",
            "release/v1.2.0",
            "main (protected)",
            "develop (protected)"
        ]
