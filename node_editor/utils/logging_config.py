"""
Logging configuration for the node editor application.

Provides centralized logging setup with multiple handlers for different levels
and outputs (console, file). Configures rotating log files with timestamps.

Author: Michael Economou
Date: 2025-12-11
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO) -> None:
    """Configure logging for the entire application.

    Sets up:
    - INFO/WARNING logs to console and INFO log file
    - DEBUG logs to DEBUG log file only
    - ERROR/CRITICAL logs to console and ERROR log file

    All logs use format: [DATETIME] [LEVEL] [MODULE] MESSAGE

    Args:
        log_dir: Directory to store log files (created if not exists)
        log_level: Minimum log level for console output (default: INFO)
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create timestamp for log filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Log format without Unicode/Emoji
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything, handlers filter

    # Clear existing handlers
    root_logger.handlers = []

    # 1. Console handler - INFO/WARNING/ERROR/CRITICAL
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. INFO/WARNING file handler
    info_log_file = os.path.join(log_dir, f"node_editor_INFO_{timestamp}.log")
    info_file_handler = logging.FileHandler(info_log_file, encoding="utf-8")
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.addFilter(lambda record: record.levelno <= logging.WARNING)
    info_file_handler.setFormatter(formatter)
    root_logger.addHandler(info_file_handler)

    # 3. DEBUG file handler (file only)
    debug_log_file = os.path.join(log_dir, f"node_editor_DEBUG_{timestamp}.log")
    debug_file_handler = logging.FileHandler(debug_log_file, encoding="utf-8")
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.addFilter(lambda record: record.levelno == logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    root_logger.addHandler(debug_file_handler)

    # 4. ERROR/CRITICAL file handler
    error_log_file = os.path.join(log_dir, f"node_editor_ERROR_{timestamp}.log")
    error_file_handler = logging.FileHandler(error_log_file, encoding="utf-8")
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    root_logger.addHandler(error_file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: Logger name (typically __name__ from module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
