"""
Logging configuration for the automation system.
"""

import logging
import sys
from pathlib import Path


def setup_logging(level=logging.INFO, log_file: str = None):
    """
    Setup logging configuration.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional log file path
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
