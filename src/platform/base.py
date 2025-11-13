"""Base platform class with default implementations."""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BasePlatform(ABC):
    """Abstract base class for platform-specific operations."""

    def __init__(self):
        self.platform_name = "base"
        self.requires_admin = False
        self.firewall_rule_name = "PowerPoint Control"

    def is_admin(self):
        """Check if the application is running with administrator/root privileges."""
        logger.info(f"Admin check not implemented for {self.platform_name}")
        return True  # Default to True for platforms that don't require it

    def create_firewall_rule(self, port):
        """
        Create a firewall rule to allow incoming connections on the specified port.

        Args:
            port (int): The port number to allow

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        logger.info(f"Firewall rule creation not implemented for {self.platform_name}")
        return True, None

    def remove_firewall_rule(self):
        """
        Remove the firewall rule created by create_firewall_rule.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        logger.info(f"Firewall rule removal not implemented for {self.platform_name}")
        return True, None

    def get_platform_name(self):
        """Get the platform name."""
        return self.platform_name

    def get_admin_message(self):
        """Get the appropriate message for requesting admin privileges."""
        return "This application requires elevated privileges to manage firewall rules."
