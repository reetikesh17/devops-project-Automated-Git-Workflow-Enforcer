"""
Terminal color utilities

Provides cross-platform colored terminal output with automatic
color detection and fallback for non-color terminals.
"""

import sys
import os


class Colors:
    """ANSI color codes for terminal output"""
    
    # Basic colors
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    
    # Bright colors
    BRIGHT_RED = '\033[1;31m'
    BRIGHT_GREEN = '\033[1;32m'
    BRIGHT_YELLOW = '\033[1;33m'
    BRIGHT_BLUE = '\033[1;34m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # Reset
    RESET = '\033[0m'
    NC = '\033[0m'  # No Color (alias)
    
    @staticmethod
    def is_color_supported():
        """
        Check if terminal supports colors
        
        Returns:
            bool: True if colors are supported
        """
        # Check if output is redirected
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check environment variables
        if os.getenv('NO_COLOR'):
            return False
        
        if os.getenv('FORCE_COLOR'):
            return True
        
        # Check terminal type
        term = os.getenv('TERM', '')
        if term in ('dumb', ''):
            return False
        
        # Windows color support
        if sys.platform == 'win32':
            # Windows 10+ supports ANSI colors
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        
        return True


def colorize(text, color, bold=False):
    """
    Colorize text for terminal output
    
    Args:
        text (str): Text to colorize
        color (str): Color code from Colors class
        bold (bool): Whether to make text bold
        
    Returns:
        str: Colorized text or plain text if colors not supported
    """
    if not Colors.is_color_supported():
        return text
    
    prefix = f"{Colors.BOLD}{color}" if bold else color
    return f"{prefix}{text}{Colors.RESET}"


def strip_colors(text):
    """
    Remove ANSI color codes from text
    
    Args:
        text (str): Text with color codes
        
    Returns:
        str: Text without color codes
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
