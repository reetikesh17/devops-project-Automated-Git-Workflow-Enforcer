"""
Output formatting utilities

Provides consistent formatting for error messages, success messages,
and validation results. Includes CI/CD-friendly JSON output.
"""

import json
from .colors import Colors, colorize


class ErrorFormatter:
    """Formats error messages consistently"""
    
    @staticmethod
    def format_validation_error(title, message, details=None, suggestions=None):
        """
        Format a validation error message
        
        Args:
            title (str): Error title
            message (str): Error message
            details (dict): Additional details
            suggestions (list): List of suggestions
            
        Returns:
            str: Formatted error message
        """
        lines = []
        
        # Header
        lines.append("")
        lines.append("=" * 70)
        lines.append(colorize(f"❌ {title}", Colors.RED, bold=True))
        lines.append("=" * 70)
        lines.append("")
        
        # Main message
        if message:
            lines.append(colorize("Error:", Colors.RED, bold=True) + f" {message}")
            lines.append("")
        
        # Details
        if details:
            for key, value in details.items():
                if isinstance(value, list):
                    lines.append(colorize(f"{key}:", Colors.YELLOW))
                    for item in value:
                        lines.append(f"  • {item}")
                else:
                    lines.append(colorize(f"{key}:", Colors.YELLOW) + f" {value}")
            lines.append("")
        
        # Suggestions
        if suggestions:
            lines.append(colorize("Suggestions:", Colors.CYAN, bold=True))
            for suggestion in suggestions:
                lines.append(f"  • {suggestion}")
            lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_config_error(message, fix=None):
        """
        Format a configuration error message
        
        Args:
            message (str): Error message
            fix (str): How to fix the error
            
        Returns:
            str: Formatted error message
        """
        lines = []
        
        lines.append("")
        lines.append(colorize("❌ Configuration Error", Colors.RED, bold=True))
        lines.append("")
        lines.append(message)
        
        if fix:
            lines.append("")
            lines.append(colorize("Fix:", Colors.YELLOW, bold=True))
            lines.append(f"  {fix}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_runtime_error(message, debug_info=None):
        """
        Format a runtime error message
        
        Args:
            message (str): Error message
            debug_info (str): Debug information
            
        Returns:
            str: Formatted error message
        """
        lines = []
        
        lines.append("")
        lines.append(colorize("❌ Runtime Error", Colors.RED, bold=True))
        lines.append("")
        lines.append(message)
        
        if debug_info:
            lines.append("")
            lines.append(colorize("Debug Info:", Colors.DIM))
            lines.append(debug_info)
        
        lines.append("")
        
        return "\n".join(lines)


def format_error(message, error_type="Error"):
    """
    Format a simple error message
    
    Args:
        message (str): Error message
        error_type (str): Type of error
        
    Returns:
        str: Formatted error message
    """
    return colorize(f"❌ {error_type}: {message}", Colors.RED)


def format_success(message):
    """
    Format a success message
    
    Args:
        message (str): Success message
        
    Returns:
        str: Formatted success message
    """
    return colorize(f"✓ {message}", Colors.GREEN)


def format_warning(message):
    """
    Format a warning message
    
    Args:
        message (str): Warning message
        
    Returns:
        str: Formatted warning message
    """
    return colorize(f"⚠ {message}", Colors.YELLOW)


def format_info(message):
    """
    Format an info message
    
    Args:
        message (str): Info message
        
    Returns:
        str: Formatted info message
    """
    return colorize(f"ℹ {message}", Colors.BLUE)


def format_ci_output(validation_type, result):
    """
    Format output for CI/CD pipelines
    
    Args:
        validation_type (str): Type of validation ('commit' or 'branch')
        result (dict): Validation result
        
    Returns:
        str: JSON formatted output
    """
    output = {
        'type': validation_type,
        'valid': result['valid'],
        'status': 'pass' if result['valid'] else 'fail'
    }
    
    if result['valid']:
        output['validation_type'] = result.get('type')
    else:
        output['error'] = result.get('error')
        output['error_type'] = result.get('error_type')
    
    return json.dumps(output, indent=2)


def format_validation_report(branch_result, commit_result):
    """
    Format a validation report for validate-all command
    
    Args:
        branch_result (dict): Branch validation result
        commit_result (dict): Commit validation result
        
    Returns:
        str: Formatted validation report
    """
    lines = []
    
    lines.append("")
    lines.append("=" * 60)
    lines.append(colorize("VALIDATION REPORT", Colors.BLUE, bold=True))
    lines.append("=" * 60)
    lines.append("")
    
    # Branch validation
    lines.append(colorize("1. Branch Name", Colors.CYAN, bold=True))
    if branch_result['valid']:
        lines.append(format_success(f"Valid ({branch_result['type']})"))
    else:
        lines.append(format_error(branch_result['error'], "Invalid"))
    lines.append("")
    
    # Commit validation
    lines.append(colorize("2. Commit Message", Colors.CYAN, bold=True))
    if commit_result['valid']:
        lines.append(format_success(f"Valid ({commit_result['type']})"))
    else:
        lines.append(format_error(commit_result['error'], "Invalid"))
    lines.append("")
    
    # Overall result
    lines.append("=" * 60)
    if branch_result['valid'] and commit_result['valid']:
        lines.append(colorize("RESULT: All validations passed ✓", Colors.GREEN, bold=True))
    else:
        lines.append(colorize("RESULT: Validation failed ✗", Colors.RED, bold=True))
    lines.append("=" * 60)
    lines.append("")
    
    return "\n".join(lines)
