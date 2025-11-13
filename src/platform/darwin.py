"""macOS-specific platform implementation."""

import os
import subprocess
import logging
from .base import BasePlatform

logger = logging.getLogger(__name__)


class DarwinPlatform(BasePlatform):
    """macOS-specific operations."""

    def __init__(self):
        super().__init__()
        self.platform_name = "macOS"
        self.requires_admin = False  # Optional on macOS

    def is_admin(self):
        """Check if the application is running with root privileges on macOS."""
        try:
            return os.geteuid() == 0
        except Exception as e:
            logger.error(f"Error checking admin status on macOS: {e}")
            return False

    def create_firewall_rule(self, port):
        """
        Attempt to create a firewall rule on macOS.

        Note: macOS firewall configuration is complex and often unnecessary
        for local network applications.

        Args:
            port (int): The port number to allow

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        logger.info(f"Firewall configuration on macOS is manual. Please ensure port {port} is accessible.")
        return True, None

    def remove_firewall_rule(self):
        """
        Remove the firewall rule on macOS.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        logger.info("Firewall rule cleanup not implemented on macOS")
        return True, None

    def get_admin_message(self):
        """Get the appropriate message for requesting admin privileges on macOS."""
        return "Note: Running without root privileges. Firewall configuration will be skipped."
