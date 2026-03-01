#!/usr/bin/env python3
"""
Automated Git Workflow Enforcer - CLI Entry Point
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.commit_validator import CommitValidator
from validators.branch_validator import BranchValidator
from config.config_loader import ConfigLoader

# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_CONFIG_ERROR = 2
EXIT_RUNTIME_ERROR = 3
EXIT_GIT_ERROR = 4


class GitWorkflowEnforcer:
    """Main CLI application class"""

    def __init__(self, config_path=None):
        self.setup_logging()
        self.config = ConfigLoader.load(config_path)
        self.commit_validator = CommitValidator(self.config)
        self.branch_validator = BranchValidator(self.config)

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def validate_commit(self, message):
        """Validate a commit message"""
        self.logger.info("Validating commit message...")
        
        # Use the boolean validate method
        is_valid = self.commit_validator.validate(message)
        
        if is_valid:
            return EXIT_SUCCESS
        else:
            return EXIT_VALIDATION_ERROR

    def validate_branch(self, branch_name):
        """Validate a branch name"""
        self.logger.info(f"Validating branch name: {branch_name}")
        
        # Use the boolean validate method
        is_valid = self.branch_validator.validate(branch_name)
        
        if is_valid:
            return EXIT_SUCCESS
        else:
            return EXIT_VALIDATION_ERROR

    def validate_all(self, branch_name, commit_message):
        """Validate both branch name and commit message"""
        self.logger.info("Running full validation...")

        branch_result = self.branch_validator.validate_detailed(branch_name)
        commit_result = self.commit_validator.validate_detailed(commit_message)

        print("=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)

        # Branch validation
        print(f"\n1. Branch Name: {branch_name}")
        if branch_result['valid']:
            print(f"   ✓ Valid ({branch_result['type']})")
        else:
            print(f"   ✗ Invalid - {branch_result['error']}")

        # Commit validation
        print(f"\n2. Commit Message: {commit_message[:50]}...")
        if commit_result['valid']:
            print(f"   ✓ Valid ({commit_result['type']})")
        else:
            print(f"   ✗ Invalid - {commit_result['error']}")

        print("\n" + "=" * 60)

        if branch_result['valid'] and commit_result['valid']:
            print("RESULT: All validations passed ✓")
            return EXIT_SUCCESS
        else:
            print("RESULT: Validation failed ✗")
            return EXIT_VALIDATION_ERROR


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Automated Git Workflow Enforcer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s validate-commit "feat: add user authentication"
  %(prog)s validate-branch feature/JIRA-123-add-login
  %(prog)s validate-all feature/JIRA-123-login "feat: add login page"
        """
    )

    parser.add_argument(
        '--config',
        '-c',
        help='Path to configuration file',
        default=None
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # validate-commit command
    commit_parser = subparsers.add_parser(
        'validate-commit',
        help='Validate a commit message'
    )
    commit_parser.add_argument(
        'message',
        help='Commit message to validate'
    )

    # validate-branch command
    branch_parser = subparsers.add_parser(
        'validate-branch',
        help='Validate a branch name'
    )
    branch_parser.add_argument(
        'branch',
        help='Branch name to validate'
    )

    # validate-all command
    all_parser = subparsers.add_parser(
        'validate-all',
        help='Validate both branch name and commit message'
    )
    all_parser.add_argument(
        'branch',
        help='Branch name to validate'
    )
    all_parser.add_argument(
        'message',
        help='Commit message to validate'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return EXIT_SUCCESS

    try:
        enforcer = GitWorkflowEnforcer(args.config)

        if args.command == 'validate-commit':
            return enforcer.validate_commit(args.message)

        elif args.command == 'validate-branch':
            return enforcer.validate_branch(args.branch)

        elif args.command == 'validate-all':
            return enforcer.validate_all(args.branch, args.message)

    except FileNotFoundError as e:
        logging.error(f"Configuration error: {e}")
        return EXIT_CONFIG_ERROR
    except Exception as e:
        logging.error(f"Runtime error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return EXIT_RUNTIME_ERROR


if __name__ == '__main__':
    sys.exit(main())
