#!/usr/bin/env python3
"""
Automated Git Workflow Enforcer - CLI Entry Point

A production-ready CLI tool for validating Git workflows including
branch names and commit messages. Optimized for CI/CD pipelines.
"""

import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.commit_validator import CommitValidator, ConfigurationError as CommitConfigError
from validators.branch_validator import BranchValidator, ConfigurationError as BranchConfigError, GitError
from config.config_loader import ConfigLoader
from utils.constants import ExitCode, APP_NAME, APP_VERSION, APP_DESCRIPTION
from utils.formatter import format_validation_report, format_error, format_success, format_ci_output
from utils.logger import setup_logger, setup_ci_logger
from utils.colors import Colors, colorize


class GitWorkflowEnforcer:
    """Main CLI application class"""

    def __init__(self, config_path=None, verbose=False, ci_mode=False):
        """
        Initialize the enforcer
        
        Args:
            config_path (str, optional): Path to configuration file
            verbose (bool): Enable verbose output
            ci_mode (bool): Enable CI/CD mode
        """
        self.ci_mode = ci_mode
        self.verbose = verbose
        
        # Setup appropriate logger
        if ci_mode:
            self.logger = setup_ci_logger(__name__)
        else:
            self.logger = setup_logger(__name__, verbose=verbose)
        
        try:
            self.config = ConfigLoader.load(config_path)
            self.commit_validator = CommitValidator(self.config)
            self.branch_validator = BranchValidator(self.config)
            self.logger.debug("Validators initialized successfully")
        except FileNotFoundError as e:
            self.logger.error(f"Configuration file not found: {e}")
            raise
        except (CommitConfigError, BranchConfigError) as e:
            self.logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise
    
    def _normalize_exit_code(self, code):
        """
        Normalize exit code for CI/CD mode
        
        In CI mode, only return 0 (success) or 1 (failure)
        
        Args:
            code (int): Original exit code
            
        Returns:
            int: Normalized exit code (0 or 1 in CI mode)
        """
        if self.ci_mode:
            return 0 if code == ExitCode.SUCCESS else 1
        return code

    def validate_commit(self, message):
        """
        Validate a commit message
        
        Args:
            message (str): Commit message to validate
            
        Returns:
            int: Exit code (0 or 1 in CI mode)
        """
        self.logger.info("Validating commit message...")
        
        try:
            result = self.commit_validator.validate_detailed(message)
            
            if self.ci_mode:
                # CI mode: structured output
                output = format_ci_output('commit', result)
                print(output)
            else:
                # Interactive mode: formatted output
                if result['valid']:
                    if not self.verbose:
                        print(format_success("Commit message is valid"))
                else:
                    # Error already printed by validator
                    pass
            
            exit_code = ExitCode.SUCCESS if result['valid'] else ExitCode.VALIDATION_ERROR
            return self._normalize_exit_code(exit_code)
                
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            if self.verbose and not self.ci_mode:
                import traceback
                traceback.print_exc()
            return self._normalize_exit_code(ExitCode.RUNTIME_ERROR)

    def validate_branch(self, branch_name=None):
        """
        Validate a branch name
        
        Args:
            branch_name (str, optional): Branch name to validate
            
        Returns:
            int: Exit code (0 or 1 in CI mode)
        """
        try:
            # Get current branch if not provided
            if branch_name is None:
                try:
                    branch_name = self.branch_validator.get_current_branch()
                    self.logger.info(f"Validating current branch: {branch_name}")
                except GitError as e:
                    self.logger.error(str(e))
                    if not self.ci_mode:
                        print(format_error(str(e), "Git Error"))
                    return self._normalize_exit_code(ExitCode.GIT_ERROR)
            else:
                self.logger.info(f"Validating branch name: {branch_name}")
            
            result = self.branch_validator.validate_detailed(branch_name)
            
            if self.ci_mode:
                # CI mode: structured output
                output = format_ci_output('branch', result)
                print(output)
            else:
                # Interactive mode: formatted output
                if result['valid']:
                    if not self.verbose:
                        print(format_success("Branch name is valid"))
                else:
                    # Error already printed by validator
                    pass
            
            exit_code = ExitCode.SUCCESS if result['valid'] else ExitCode.VALIDATION_ERROR
            return self._normalize_exit_code(exit_code)
                
        except GitError as e:
            self.logger.error(f"Git error: {e}")
            if not self.ci_mode:
                print(format_error(str(e), "Git Error"))
            return self._normalize_exit_code(ExitCode.GIT_ERROR)
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            if self.verbose and not self.ci_mode:
                import traceback
                traceback.print_exc()
            return self._normalize_exit_code(ExitCode.RUNTIME_ERROR)

    def validate_all(self, branch_name, commit_message):
        """
        Validate both branch name and commit message
        
        Args:
            branch_name (str): Branch name to validate
            commit_message (str): Commit message to validate
            
        Returns:
            int: Exit code (0 or 1 in CI mode)
        """
        self.logger.info("Running full validation...")

        try:
            branch_result = self.branch_validator.validate_detailed(branch_name)
            commit_result = self.commit_validator.validate_detailed(commit_message)

            if self.ci_mode:
                # CI mode: structured JSON output
                output = {
                    'branch': {
                        'name': branch_name,
                        'valid': branch_result['valid'],
                        'type': branch_result.get('type'),
                        'error': branch_result.get('error')
                    },
                    'commit': {
                        'message': commit_message[:50] + '...' if len(commit_message) > 50 else commit_message,
                        'valid': commit_result['valid'],
                        'type': commit_result.get('type'),
                        'error': commit_result.get('error')
                    },
                    'overall': {
                        'valid': branch_result['valid'] and commit_result['valid']
                    }
                }
                print(json.dumps(output, indent=2))
            else:
                # Interactive mode: formatted report
                print(format_validation_report(branch_result, commit_result))

            all_valid = branch_result['valid'] and commit_result['valid']
            exit_code = ExitCode.SUCCESS if all_valid else ExitCode.VALIDATION_ERROR
            return self._normalize_exit_code(exit_code)
                
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            if self.verbose and not self.ci_mode:
                import traceback
                traceback.print_exc()
            return self._normalize_exit_code(ExitCode.RUNTIME_ERROR)


def create_parser():
    """
    Create argument parser
    
    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        prog='git-enforcer',
        description=f'{APP_NAME} - {APP_DESCRIPTION}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{colorize('Examples:', Colors.CYAN, bold=True)}
  %(prog)s validate-commit "feat: add user authentication"
  %(prog)s validate-branch feature/JIRA-123-add-login
  %(prog)s validate-all feature/JIRA-123-login "feat: add login page"

{colorize('Exit Codes:', Colors.CYAN, bold=True)}
  0 - Success
  1 - Validation error
  2 - Configuration error
  3 - Runtime error
  4 - Git error

{colorize('Documentation:', Colors.CYAN, bold=True)}
  https://github.com/reetikesh17/devops-project-Automated-Git-Workflow-Enforcer
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {APP_VERSION}'
    )

    parser.add_argument(
        '--config',
        '-c',
        metavar='PATH',
        help='path to configuration file (default: src/config/rules.json)',
        default=None
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='enable verbose output with debug information'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='disable colored output'
    )

    parser.add_argument(
        '--ci',
        action='store_true',
        help='enable CI/CD mode (structured output, exit codes 0/1 only, no colors)'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        description='available validation commands',
        help='command to execute'
    )

    # validate-commit command
    commit_parser = subparsers.add_parser(
        'validate-commit',
        help='validate a commit message',
        description='Validate a commit message against Conventional Commits format'
    )
    commit_parser.add_argument(
        'message',
        help='commit message to validate'
    )

    # validate-branch command
    branch_parser = subparsers.add_parser(
        'validate-branch',
        help='validate a branch name',
        description='Validate a branch name against defined patterns'
    )
    branch_parser.add_argument(
        'branch',
        nargs='?',
        help='branch name to validate (default: current branch)',
        default=None
    )

    # validate-all command
    all_parser = subparsers.add_parser(
        'validate-all',
        help='validate both branch and commit',
        description='Validate both branch name and commit message'
    )
    all_parser.add_argument(
        'branch',
        help='branch name to validate'
    )
    all_parser.add_argument(
        'message',
        help='commit message to validate'
    )

    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # CI mode implies no-color and structured output
    if args.ci:
        import os
        os.environ['NO_COLOR'] = '1'
        args.no_color = True
    
    # Disable colors if requested
    if args.no_color:
        import os
        os.environ['NO_COLOR'] = '1'

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0 if args.ci else ExitCode.SUCCESS

    try:
        enforcer = GitWorkflowEnforcer(args.config, args.verbose, args.ci)

        if args.command == 'validate-commit':
            return enforcer.validate_commit(args.message)

        elif args.command == 'validate-branch':
            return enforcer.validate_branch(args.branch)

        elif args.command == 'validate-all':
            return enforcer.validate_all(args.branch, args.message)

    except FileNotFoundError as e:
        if not args.ci:
            print(format_error(f"Configuration file not found: {e}", "Config Error"))
        else:
            print(json.dumps({'error': 'config_not_found', 'message': str(e)}))
        return 1 if args.ci else ExitCode.CONFIG_ERROR
    except (CommitConfigError, BranchConfigError) as e:
        if not args.ci:
            print(format_error(f"Configuration error: {e}", "Config Error"))
        else:
            print(json.dumps({'error': 'config_error', 'message': str(e)}))
        return 1 if args.ci else ExitCode.CONFIG_ERROR
    except Exception as e:
        if not args.ci:
            print(format_error(f"Runtime error: {e}", "Runtime Error"))
            if args.verbose:
                import traceback
                traceback.print_exc()
        else:
            print(json.dumps({'error': 'runtime_error', 'message': str(e)}))
        return 1 if args.ci else ExitCode.RUNTIME_ERROR


if __name__ == '__main__':
    sys.exit(main())
