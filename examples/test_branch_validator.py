#!/usr/bin/env python3
"""
Example script demonstrating the BranchValidator module

This script shows how to use the branch_validator module
with various test cases.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from validators.branch_validator import BranchValidator, ConfigurationError, GitError
from config.config_loader import ConfigLoader


def test_branch_names():
    """Test various branch names"""
    
    print("=" * 70)
    print("BRANCH VALIDATOR TEST SUITE")
    print("=" * 70)
    
    # Load configuration
    try:
        config = ConfigLoader.load()
        validator = BranchValidator(config)
        print("\n✓ Configuration loaded successfully\n")
        print(validator.get_config_summary())
        print()
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test cases
    test_cases = [
        # Valid feature branches
        ("feature/JIRA-123-user-authentication", True),
        ("feature/PROJ-456-add-login-page", True),
        ("feature/TICKET-789-implement-api", True),
        
        # Valid bugfix branches
        ("bugfix/BUG-111-fix-login-error", True),
        ("bugfix/ISSUE-222-resolve-timeout", True),
        
        # Valid hotfix branches
        ("hotfix/URGENT-999", True),
        ("hotfix/CRITICAL-001", True),
        
        # Valid release branches
        ("release/v1.0.0", True),
        ("release/v2.3.1", True),
        ("release/v1.0.0-beta", True),
        ("release/v1.0.0-rc1", True),
        
        # Protected branches
        ("main", True),
        ("master", True),
        ("develop", True),
        
        # Invalid branches
        ("add-feature", False),
        ("feature/add-login", False),  # Missing ticket ID
        ("feature/123-login", False),  # Invalid ticket format
        ("feature/JIRA-123", False),  # Missing description
        ("bugfix/fix-bug", False),  # Missing ticket ID
        ("hotfix/fix", False),  # Missing ticket ID
        ("release/1.0.0", False),  # Missing 'v' prefix
        ("release/v1.0", False),  # Invalid version format
        ("", False),  # Empty
        ("random-branch-name", False),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "=" * 70)
    print("RUNNING TEST CASES")
    print("=" * 70 + "\n")
    
    for i, (branch_name, expected_valid) in enumerate(test_cases, 1):
        print(f"Test {i}: {branch_name if branch_name else '(empty)'}...")
        
        result = validator.validate(branch_name)
        
        if result == expected_valid:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        print(f"  Expected: {'Valid' if expected_valid else 'Invalid'}")
        print(f"  Result: {'Valid' if result else 'Invalid'}")
        print(f"  {status}\n")
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/len(test_cases)*100):.1f}%")
    print("=" * 70)
    
    return failed == 0


def demonstrate_detailed_validation():
    """Demonstrate detailed validation results"""
    
    print("\n\n" + "=" * 70)
    print("DETAILED VALIDATION DEMONSTRATION")
    print("=" * 70 + "\n")
    
    config = ConfigLoader.load()
    validator = BranchValidator(config)
    
    branches = [
        "feature/JIRA-123-user-authentication",
        "bugfix/PROJ-456-fix-login",
        "hotfix/URGENT-789",
        "release/v1.2.0",
        "main",
        "invalid-branch-name"
    ]
    
    for branch in branches:
        print(f"Branch: {branch}")
        result = validator.validate_detailed(branch)
        
        print(f"Valid: {result['valid']}")
        if result['valid']:
            print(f"Type: {result['type']}")
            if result.get('ticket_id'):
                print(f"Ticket ID: {result['ticket_id']}")
        else:
            print(f"Error: {result['error']}")
            print(f"Error type: {result['error_type']}")
        
        print("-" * 70 + "\n")


def test_git_integration():
    """Test Git integration (current branch detection)"""
    
    print("\n" + "=" * 70)
    print("GIT INTEGRATION TEST")
    print("=" * 70 + "\n")
    
    config = ConfigLoader.load()
    validator = BranchValidator(config)
    
    try:
        current_branch = validator.get_current_branch()
        print(f"✓ Current Git branch detected: {current_branch}")
        
        print(f"\nValidating current branch...")
        is_valid = validator.validate_current_branch()
        
        if is_valid:
            print(f"✓ Current branch is valid")
        else:
            print(f"✗ Current branch is invalid")
        
        return True
        
    except GitError as e:
        print(f"⚠ Git error (expected if not in a Git repo): {e}")
        return True  # Not a failure, just not in a Git repo
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def demonstrate_error_messages():
    """Demonstrate error message formatting"""
    
    print("\n" + "=" * 70)
    print("ERROR MESSAGE DEMONSTRATION")
    print("=" * 70 + "\n")
    
    config = ConfigLoader.load()
    validator = BranchValidator(config)
    
    invalid_branches = [
        "add-feature",
        "feature/add-login",
        "random-name"
    ]
    
    print("Testing invalid branch names to show error messages:\n")
    
    for branch in invalid_branches:
        print(f"Testing: {branch}")
        validator.validate(branch)
        print()


if __name__ == '__main__':
    try:
        # Run tests
        test_success = test_branch_names()
        
        # Demonstrate detailed validation
        demonstrate_detailed_validation()
        
        # Test Git integration
        git_success = test_git_integration()
        
        # Demonstrate error messages
        demonstrate_error_messages()
        
        # Exit with appropriate code
        sys.exit(0 if (test_success and git_success) else 1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
