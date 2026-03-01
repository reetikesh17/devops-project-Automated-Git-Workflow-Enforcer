"""
Git utilities

Provides helper functions for Git operations like getting current branch
and latest commit message.
"""

import subprocess
import os
from typing import Optional


class GitError(Exception):
    """Raised when Git operations fail"""
    pass


def get_current_branch() -> str:
    """
    Get the current Git branch name
    
    Returns:
        str: Current branch name
        
    Raises:
        GitError: If Git command fails or not in a Git repository
    """
    try:
        # Try git rev-parse first
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        
        branch_name = result.stdout.strip()
        
        # Check for detached HEAD
        if branch_name == 'HEAD':
            # Try to get branch from GitHub Actions environment
            branch_name = _get_branch_from_env()
            if not branch_name:
                raise GitError("Detached HEAD state - cannot determine branch name")
        
        return branch_name
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        
        # Try environment variables as fallback
        branch_name = _get_branch_from_env()
        if branch_name:
            return branch_name
        
        raise GitError(f"Failed to get current branch: {error_msg}")
    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out")
    except FileNotFoundError:
        raise GitError("Git is not installed or not in PATH")
    except Exception as e:
        raise GitError(f"Unexpected error getting current branch: {e}")


def get_latest_commit_message() -> str:
    """
    Get the latest commit message
    
    Returns:
        str: Latest commit message
        
    Raises:
        GitError: If Git command fails or not in a Git repository
    """
    try:
        # Try git log first
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        
        message = result.stdout.strip()
        
        if not message:
            # Try environment variables as fallback
            message = _get_commit_message_from_env()
            if not message:
                raise GitError("No commits found in repository")
        
        return message
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        
        # Try environment variables as fallback
        message = _get_commit_message_from_env()
        if message:
            return message
        
        raise GitError(f"Failed to get latest commit message: {error_msg}")
    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out")
    except FileNotFoundError:
        raise GitError("Git is not installed or not in PATH")
    except Exception as e:
        raise GitError(f"Unexpected error getting commit message: {e}")


def _get_branch_from_env() -> Optional[str]:
    """
    Get branch name from environment variables
    
    Supports GitHub Actions, GitLab CI, Jenkins, CircleCI, etc.
    
    Returns:
        str or None: Branch name from environment
    """
    # GitHub Actions
    github_ref = os.getenv('GITHUB_REF')
    if github_ref:
        # GITHUB_REF format: refs/heads/branch-name or refs/pull/123/merge
        if github_ref.startswith('refs/heads/'):
            return github_ref.replace('refs/heads/', '')
        elif github_ref.startswith('refs/pull/'):
            # For PRs, use GITHUB_HEAD_REF
            return os.getenv('GITHUB_HEAD_REF')
    
    # GitHub Actions - direct branch name
    github_head_ref = os.getenv('GITHUB_HEAD_REF')
    if github_head_ref:
        return github_head_ref
    
    github_ref_name = os.getenv('GITHUB_REF_NAME')
    if github_ref_name:
        return github_ref_name
    
    # GitLab CI
    ci_commit_ref_name = os.getenv('CI_COMMIT_REF_NAME')
    if ci_commit_ref_name:
        return ci_commit_ref_name
    
    # Jenkins
    branch_name = os.getenv('BRANCH_NAME')
    if branch_name:
        return branch_name
    
    git_branch = os.getenv('GIT_BRANCH')
    if git_branch:
        # Jenkins format: origin/branch-name
        if git_branch.startswith('origin/'):
            return git_branch.replace('origin/', '')
        return git_branch
    
    # CircleCI
    circle_branch = os.getenv('CIRCLE_BRANCH')
    if circle_branch:
        return circle_branch
    
    # Azure Pipelines
    build_source_branch = os.getenv('BUILD_SOURCEBRANCH')
    if build_source_branch:
        # Format: refs/heads/branch-name
        if build_source_branch.startswith('refs/heads/'):
            return build_source_branch.replace('refs/heads/', '')
        return build_source_branch
    
    build_source_branch_name = os.getenv('BUILD_SOURCEBRANCHNAME')
    if build_source_branch_name:
        return build_source_branch_name
    
    return None


def _get_commit_message_from_env() -> Optional[str]:
    """
    Get commit message from environment variables
    
    Supports GitHub Actions, GitLab CI, Jenkins, CircleCI, etc.
    
    Returns:
        str or None: Commit message from environment
    """
    # GitHub Actions
    github_event_head_commit_message = os.getenv('GITHUB_EVENT_HEAD_COMMIT_MESSAGE')
    if github_event_head_commit_message:
        return github_event_head_commit_message
    
    # GitLab CI
    ci_commit_message = os.getenv('CI_COMMIT_MESSAGE')
    if ci_commit_message:
        return ci_commit_message
    
    # Jenkins
    git_commit_msg = os.getenv('GIT_COMMIT_MSG')
    if git_commit_msg:
        return git_commit_msg
    
    # CircleCI doesn't provide commit message directly
    # Azure Pipelines
    build_source_version_message = os.getenv('BUILD_SOURCEVERSIONMESSAGE')
    if build_source_version_message:
        return build_source_version_message
    
    return None


def is_git_repository() -> bool:
    """
    Check if current directory is in a Git repository
    
    Returns:
        bool: True if in a Git repository
    """
    try:
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False
