"""Network utility functions for the PPT Command Executor."""

import socket
import logging

logger = logging.getLogger(__name__)


def get_local_ip():
    """
    Get the local IP address of the machine.

    Returns:
        str: The local IP address, or '127.0.0.1' if unable to determine
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a dummy address to get the local IP
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        logger.info(f"Detected local IP: {ip}")
    except Exception as e:
        logger.warning(f"Failed to detect local IP: {e}. Using localhost.")
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def check_network_connection():
    """
    Check if the machine has an active network connection.

    Returns:
        bool: True if connected to a network, False otherwise
    """
    ip = get_local_ip()
    is_connected = ip != '127.0.0.1'
    logger.info(f"Network connection status: {is_connected}")
    return is_connected


def find_free_port(start_port=5000, max_port=5100):
    """
    Find an available port in the specified range.

    Args:
        start_port (int): The starting port number to check
        max_port (int): The maximum port number to check

    Returns:
        int: An available port number

    Raises:
        RuntimeError: If no free ports are available in the range
    """
    for port in range(start_port, max_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
            s.close()
            logger.info(f"Found free port: {port}")
            return port
        except OSError:
            continue

    error_msg = f'No free ports available in range {start_port}-{max_port}'
    logger.error(error_msg)
    raise RuntimeError(error_msg)
