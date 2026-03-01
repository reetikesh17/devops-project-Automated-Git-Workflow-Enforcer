"""
Application constants

Defines exit codes, error types, and other constants used throughout
the application.
"""


class ExitCode:
    """Exit codes for the application"""
    
    SUCCESS = 0
    VALIDATION_ERROR = 1
    CONFIG_ERROR = 2
    RUNTIME_ERROR = 3
    GIT_ERROR = 4
    
    @classmethod
    def get_description(cls, code):
        """Get description for exit code"""
        descriptions = {
            cls.SUCCESS: "Success",
            cls.VALIDATION_ERROR: "Validation error",
            cls.CONFIG_ERROR: "Configuration error",
            cls.RUNTIME_ERROR: "Runtime error",
            cls.GIT_ERROR: "Git error"
        }
        return descriptions.get(code, "Unknown error")


class ErrorType:
    """Error types for validation"""
    
    # Commit validation errors
    EMPTY_MESSAGE = "EMPTY_MESSAGE"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_TYPE = "INVALID_TYPE"
    DESCRIPTION_TOO_SHORT = "DESCRIPTION_TOO_SHORT"
    DESCRIPTION_TOO_LONG = "DESCRIPTION_TOO_LONG"
    INVALID_CASE = "INVALID_CASE"
    INVALID_PUNCTUATION = "INVALID_PUNCTUATION"
    
    # Branch validation errors
    EMPTY_BRANCH_NAME = "EMPTY_BRANCH_NAME"
    INVALID_PATTERN = "INVALID_PATTERN"
    
    # Configuration errors
    MISSING_CONFIG = "MISSING_CONFIG"
    INVALID_CONFIG = "INVALID_CONFIG"
    
    # Git errors
    NOT_GIT_REPO = "NOT_GIT_REPO"
    GIT_COMMAND_FAILED = "GIT_COMMAND_FAILED"


class ValidationStatus:
    """Validation status constants"""
    
    VALID = "valid"
    INVALID = "invalid"
    SKIPPED = "skipped"


# Application metadata
APP_NAME = "Git Workflow Enforcer"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Automated Git workflow validation tool"
