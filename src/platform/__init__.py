"""Platform-specific implementations for OS-dependent functionality."""

import platform
import logging

logger = logging.getLogger(__name__)

def get_platform_handler():
    """Factory function to get the appropriate platform handler."""
    system = platform.system()

    if system == "Windows":
        from .windows import WindowsPlatform
        return WindowsPlatform()
    elif system == "Linux":
        from .linux import LinuxPlatform
        return LinuxPlatform()
    elif system == "Darwin":
        from .darwin import DarwinPlatform
        return DarwinPlatform()
    else:
        logger.warning(f"Unsupported platform: {system}, using base implementation")
        from .base import BasePlatform
        return BasePlatform()
