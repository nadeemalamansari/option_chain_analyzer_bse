"""Logging utilities for Option Chain Analyzer"""

import logging
import sys
from datetime import datetime
import os


def setup_logger(name: str = "option_chain_analyzer", level: str = "INFO") -> logging.Logger:
    """
    Setup and return a logger instance.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # If logger already has handlers, return it (avoid duplicate handlers)
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "option_chain_analyzer") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    return setup_logger(name)


# Default logger instance
logger = setup_logger()


def set_log_level(level: str):
    """
    Set log level for the default logger.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global logger
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    for handler in logger.handlers:
        handler.setLevel(log_level)


def add_file_handler(logger: logging.Logger, file_path: str, level: str = "INFO"):
    """
    Add a file handler to a logger.
    
    Args:
        logger: Logger instance
        file_path: Path to log file
        level: Log level
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
    except Exception as e:
        logger.error(f"Failed to add file handler: {e}")