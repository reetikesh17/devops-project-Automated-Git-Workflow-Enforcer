"""
Commit Message Validator
Validates commit messages against Conventional Commits format
"""

import re
import logging


class CommitValidator:
    """Validates commit messages"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.allowed_types = config.get('commits', {}).get('types', [])
        self.min_length = config.get('commits', {}).get('descriptionLength', {}).get('min', 10)
        self.max_length = config.get('commits', {}).get('descriptionLength', {}).get('max', 100)

    def validate(self, message):
        """
        Validate a commit message

        Args:
            message (str): Commit message to validate

        Returns:
            dict: Validation result with 'valid', 'type', 'error', and 'suggestions' keys
        """
        if not message or not message.strip():
            return {
                'valid': False,
                'error': 'Commit message cannot be empty',
                'suggestions': self._get_suggestions()
            }

        # Parse the commit message
        parsed = self._parse_message(message)

        if not parsed:
            return {
                'valid': False,
                'error': 'Invalid commit message format. Expected: <type>: <description>',
                'suggestions': self._get_suggestions()
            }

        commit_type = parsed['type']
        description = parsed['description']

        # Validate type
        if commit_type not in self.allowed_types:
            return {
                'valid': False,
                'error': f"Invalid commit type '{commit_type}'",
                'suggestions': [
                    f"Allowed types: {', '.join(self.allowed_types)}",
                    f"Example: feat: {description}"
                ]
            }

        # Validate description length
        if len(description) < self.min_length:
            return {
                'valid': False,
                'error': f"Description too short (minimum {self.min_length} characters)",
                'suggestions': [
                    f"Current length: {len(description)} characters",
                    "Add more detail to your commit message"
                ]
            }

        if len(description) > self.max_length:
            return {
                'valid': False,
                'error': f"Description too long (maximum {self.max_length} characters)",
                'suggestions': [
                    f"Current length: {len(description)} characters",
                    "Make your commit message more concise"
                ]
            }

        # Validate description format
        if description[0].isupper():
            return {
                'valid': False,
                'error': 'Description should start with lowercase letter',
                'suggestions': [
                    f"Try: {commit_type}: {description[0].lower()}{description[1:]}"
                ]
            }

        if description.endswith('.'):
            return {
                'valid': False,
                'error': 'Description should not end with a period',
                'suggestions': [
                    f"Try: {commit_type}: {description[:-1]}"
                ]
            }

        self.logger.debug(f"Valid commit message: {commit_type}: {description}")

        return {
            'valid': True,
            'type': commit_type,
            'description': description
        }

    def _parse_message(self, message):
        """
        Parse commit message into type and description

        Args:
            message (str): Commit message

        Returns:
            dict or None: Parsed message with 'type' and 'description' keys
        """
        # Pattern: <type>: <description>
        pattern = r'^(feat|fix|chore|docs|refactor|test|ci):\s+(.+)$'
        match = re.match(pattern, message.strip(), re.MULTILINE)

        if not match:
            return None

        return {
            'type': match.group(1),
            'description': match.group(2).split('\n')[0]  # Only first line
        }

    def _get_suggestions(self):
        """Get example commit messages"""
        return [
            "feat: add user authentication module",
            "fix: resolve null pointer in login handler",
            "docs: update API documentation",
            "refactor: simplify validation logic",
            "test: add unit tests for validator",
            "chore: update dependencies",
            "ci: configure GitHub Actions workflow"
        ]
