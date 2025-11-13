"""Linux-specific platform implementation."""

import os
import subprocess
import logging
from .base import BasePlatform

logger = logging.getLogger(__name__)


class LinuxPlatform(BasePlatform):
    """Linux-specific operations."""

    def __init__(self):
        super().__init__()
        self.platform_name = "Linux"
        self.requires_admin = False  # Optional on Linux

    def is_admin(self):
        """Check if the application is running with root privileges on Linux."""
        try:
            return os.geteuid() == 0
        except Exception as e:
            logger.error(f"Error checking admin status on Linux: {e}")
            return False

    def create_firewall_rule(self, port):
        """
        Attempt to create a firewall rule on Linux using iptables or ufw.

        Note: This is optional on Linux. The application will work without it
        if the firewall is already configured or disabled.

        Args:
            port (int): The port number to allow

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        # Check if ufw is available
        try:
            result = subprocess.run(
                ['which', 'ufw'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return self._create_ufw_rule(port)
        except Exception:
            pass

        # Check if iptables is available
        try:
            result = subprocess.run(
                ['which', 'iptables'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return self._create_iptables_rule(port)
        except Exception:
            pass

        logger.info("No firewall management tool found (ufw/iptables). Skipping firewall configuration.")
        return True, None

    def _create_ufw_rule(self, port):
        """Create a firewall rule using ufw."""
        try:
            subprocess.run(
                ['ufw', 'allow', str(port)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"UFW firewall rule created for port {port}")
            return True, None
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to create UFW rule (continuing anyway): {e.stderr}")
            return True, None  # Don't fail if firewall can't be configured
        except Exception as e:
            logger.warning(f"Error creating UFW rule (continuing anyway): {str(e)}")
            return True, None

    def _create_iptables_rule(self, port):
        """Create a firewall rule using iptables."""
        try:
            subprocess.run(
                [
                    'iptables', '-A', 'INPUT',
                    '-p', 'tcp',
                    '--dport', str(port),
                    '-j', 'ACCEPT'
                ],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"iptables firewall rule created for port {port}")
            return True, None
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to create iptables rule (continuing anyway): {e.stderr}")
            return True, None  # Don't fail if firewall can't be configured
        except Exception as e:
            logger.warning(f"Error creating iptables rule (continuing anyway): {str(e)}")
            return True, None

    def remove_firewall_rule(self):
        """
        Remove the firewall rule on Linux.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        logger.info("Firewall rule cleanup not implemented on Linux (manual cleanup may be needed)")
        return True, None

    def get_admin_message(self):
        """Get the appropriate message for requesting admin privileges on Linux."""
        return "Note: Running without root privileges. Firewall configuration will be skipped."
