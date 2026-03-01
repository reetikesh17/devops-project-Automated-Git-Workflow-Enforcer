"""
Logging utilities

Provides consistent logging configuration across the application.
"""

import logging
import sys
from .colors import Colors, colorize


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output"""
    
    COLORS = {
        'DEBUG': Colors.DIM,
        'INFO': Colors.BLUE,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.BRIGHT_RED
    }
    
    def format(self, record):
        """Format log record with colors"""
        # Save original levelname
        levelname = record.levelname
        
        # Colorize level name
        if Colors.is_color_supported():
            color = self.COLORS.get(levelname, Colors.WHITE)
            record.levelname = colorize(levelname, color, bold=True)
        
        # Format message
        result = super().format(record)
        
        # Restore original levelname
        record.levelname = levelname
        
        return result


def setup_logger(name, level=logging.INFO, verbose=False):
    """
    Setup logger with consistent configuration
    
    Args:
        name (str): Logger name
        level (int): Logging level
        verbose (bool): Enable verbose output
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if verbose else level)
    
    # Create formatter
    if Colors.is_color_supported():
        formatter = ColoredFormatter(
            '%(levelname)s: %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name):
    """
    Get logger instance
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
