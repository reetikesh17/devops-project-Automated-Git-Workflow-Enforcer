#!/usr/bin/env python3
"""
Example script demonstrating the CommitValidator module

This script shows how to use the commit_validator module
with various test cases.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from validators.commit_validator import CommitValidator, ConfigurationError
from config.config_loader import ConfigLoader


def test_commit_messages():
    """Test various commit messages"""
    
    print("=" * 70)
    print("COMMIT VALIDATOR TEST SUITE")
    print("=" * 70)
    
    # Load configuration
    try:
        config = ConfigLoader.load()
        validator = CommitValidator(config)
        print("\n✓ Configuration loaded successfully\n")
        print(validator.get_config_summary())
        print()
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Test cases
    test_cases = [
        # Valid messages
        ("feat: add user authentication module", True),
        ("fix: resolve null pointer exception", True),
        ("docs: update installation guide", True),
        ("refactor: simplify validation logic", True),
        ("test: add unit tests for validator", True),
        ("chore: update dependencies to latest", True),
        ("ci: configure GitHub Actions workflow", True),
        
        # Valid with scope
        ("feat(auth): add login functionality", True),
        ("fix(api): resolve timeout issue", True),
        
        # Invalid messages
        ("Add feature", False),
        ("feat: short", False),
        ("feat: Add Feature", False),
        ("feat: add feature.", False),
        ("wrongtype: add something", False),
        ("", False),
        ("feat:missing space", False),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "=" * 70)
    print("RUNNING TEST CASES")
    print("=" * 70 + "\n")
    
    for i, (message, expected_valid) in enumerate(test_cases, 1):
        print(f"Test {i}: {message[:50] if message else '(empty)'}...")
        
        result = validator.validate(message)
        
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
    validator = CommitValidator(config)
    
    messages = [
        "feat: add user authentication module",
        "fix(api): resolve timeout issue",
        "invalid message format"
    ]
    
    for message in messages:
        print(f"Message: {message}")
        result = validator.validate_detailed(message)
        
        print(f"Valid: {result['valid']}")
        if result['valid']:
            print(f"Type: {result['type']}")
            print(f"Description: {result['description']}")
            if result.get('scope'):
                print(f"Scope: {result['scope']}")
            if result.get('breaking'):
                print(f"Breaking change: Yes")
        else:
            print(f"Error: {result['error']}")
            print(f"Error type: {result['error_type']}")
        
        print("-" * 70 + "\n")


if __name__ == '__main__':
    try:
        # Run tests
        success = test_commit_messages()
        
        # Demonstrate detailed validation
        demonstrate_detailed_validation()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
