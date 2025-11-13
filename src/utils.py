"""Utility functions for the PPT Command Executor."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_asset_paths(*paths):
    """
    Validate that asset paths exist.

    Args:
        *paths: Variable number of Path objects to validate

    Returns:
        tuple: (all_exist: bool, missing_paths: list)
    """
    missing = []
    for path in paths:
        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            logger.warning(f"Asset path does not exist: {path}")
            missing.append(str(path))

    all_exist = len(missing) == 0
    if all_exist:
        logger.info(f"All {len(paths)} asset paths validated successfully")
    else:
        logger.error(f"{len(missing)} asset paths missing: {missing}")

    return all_exist, missing


def ensure_directory_exists(directory):
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory (Path or str): Directory path

    Returns:
        bool: True if directory exists or was created successfully
    """
    if not isinstance(directory, Path):
        directory = Path(directory)

    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {directory}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False


def validate_port(port):
    """
    Validate a port number.

    Args:
        port: Port number to validate

    Returns:
        bool: True if port is valid

    Raises:
        ValueError: If port is invalid
    """
    if not isinstance(port, int):
        raise ValueError(f"Port must be an integer, got {type(port)}")

    if port < 1 or port > 65535:
        raise ValueError(f"Port must be between 1 and 65535, got {port}")

    # Check for privileged ports on Unix-like systems
    if port < 1024:
        logger.warning(f"Port {port} is a privileged port (< 1024) and may require elevated permissions")

    return True


def validate_config(config_dict):
    """
    Validate configuration values.

    Args:
        config_dict (dict): Configuration dictionary

    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []

    # Validate port range
    start_port = config_dict.get('DEFAULT_START_PORT')
    max_port = config_dict.get('DEFAULT_MAX_PORT')

    if start_port is not None and max_port is not None:
        try:
            validate_port(start_port)
            validate_port(max_port)

            if start_port >= max_port:
                errors.append(f"Start port ({start_port}) must be less than max port ({max_port})")
        except ValueError as e:
            errors.append(str(e))

    # Validate window dimensions
    width = config_dict.get('WINDOW_WIDTH')
    height = config_dict.get('WINDOW_HEIGHT')

    if width is not None and (not isinstance(width, int) or width < 100 or width > 10000):
        errors.append(f"Invalid window width: {width}")

    if height is not None and (not isinstance(height, int) or height < 100 or height > 10000):
        errors.append(f"Invalid window height: {height}")

    # Validate status update interval
    interval = config_dict.get('STATUS_UPDATE_INTERVAL')
    if interval is not None and (not isinstance(interval, int) or interval < 100 or interval > 60000):
        errors.append(f"Invalid status update interval: {interval} (must be 100-60000 ms)")

    is_valid = len(errors) == 0

    if is_valid:
        logger.info("Configuration validated successfully")
    else:
        logger.error(f"Configuration validation failed: {errors}")

    return is_valid, errors
