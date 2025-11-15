"""
Logging configuration module.

This module provides centralized logging setup for the emotion analysis system.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import LogConfig, PathConfig


def setup_logging(
    log_level: str = None,
    log_dir: Path = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, uses LOG_LEVEL from config.
        log_dir: Directory for log files. If None, uses LOG_DIR from config.
        console: Whether to also output logs to console.
        
    Returns:
        Configured root logger.
    """
    # Use config defaults if not specified
    if log_level is None:
        log_level = LogConfig.LOG_LEVEL
    if log_dir is None:
        log_dir = PathConfig.LOG_DIR
    
    # Ensure log directory exists
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(
        LogConfig.LOG_FORMAT,
        datefmt=LogConfig.LOG_DATE_FORMAT
    )
    
    # File handler with rotation
    log_file = log_dir / 'emotion_analysis.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LogConfig.MAX_LOG_SIZE,
        backupCount=LogConfig.BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (if enabled)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Log startup message
    logger.info("="*60)
    logger.info("Emotion Analysis System - Logging Started")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Log File: {log_file}")
    logger.info("="*60)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Name of the module (usually __name__).
        
    Returns:
        Logger instance for the module.
    """
    return logging.getLogger(name)
