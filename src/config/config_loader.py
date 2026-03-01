"""
Configuration Loader
Loads and validates configuration from JSON file
"""

import json
import logging
from pathlib import Path


class ConfigLoader:
    """Loads configuration from file"""

    @staticmethod
    def load(config_path=None):
        """
        Load configuration from file

        Args:
            config_path (str, optional): Path to config file

        Returns:
            dict: Configuration dictionary
        """
        logger = logging.getLogger(__name__)

        # Default config path
        if config_path is None:
            config_path = Path(__file__).parent / 'rules.json'
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        logger.debug(f"Loading configuration from: {config_path}")

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}")

    @staticmethod
    def validate(config):
        """
        Validate configuration structure

        Args:
            config (dict): Configuration to validate

        Returns:
            bool: True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = ['branches', 'commits']

        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")

        # Validate branches config
        if 'patterns' not in config['branches']:
            raise ValueError("Missing 'patterns' in branches configuration")

        # Validate commits config
        if 'types' not in config['commits']:
            raise ValueError("Missing 'types' in commits configuration")

        return True
