"""Windows-specific platform implementation."""

import ctypes
import subprocess
import logging
from .base import BasePlatform

logger = logging.getLogger(__name__)


class WindowsPlatform(BasePlatform):
    """Windows-specific operations."""

    def __init__(self):
        super().__init__()
        self.platform_name = "Windows"
        self.requires_admin = True

    def is_admin(self):
        """Check if the application is running as administrator on Windows."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            logger.error(f"Error checking admin status on Windows: {e}")
            return False

    def create_firewall_rule(self, port):
        """
        Create a Windows firewall rule using netsh.

        Args:
            port (int): The port number to allow

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            subprocess.run(
                [
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name={self.firewall_rule_name}',
                    'dir=in',
                    'action=allow',
                    'protocol=TCP',
                    f'localport={port}'
                ],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Windows firewall rule '{self.firewall_rule_name}' created for port {port}")
            return True, None
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to add firewall rule: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error while adding firewall rule: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def remove_firewall_rule(self):
        """
        Remove the Windows firewall rule using netsh.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            subprocess.run(
                [
                    'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                    f'name={self.firewall_rule_name}'
                ],
                check=False,
                capture_output=True,
                text=True
            )
            logger.info(f"Windows firewall rule '{self.firewall_rule_name}' removed")
            return True, None
        except Exception as e:
            error_msg = f"Error removing firewall rule: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_admin_message(self):
        """Get the appropriate message for requesting admin privileges on Windows."""
        return "Please run the program as Administrator"
