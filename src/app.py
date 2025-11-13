"""Main application class for the PPT Command Executor."""

import customtkinter as ctk
import threading
import logging
import sys
from PIL import Image, ImageTk

from .config import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_BG_COLOR,
    FAVICON_PNG, FAVICON_ICO
)
from .platform import get_platform_handler
from .network.utils import get_local_ip, check_network_connection, find_free_port
from .server.socket_server import PPTServer
from .gui.screens import FirstScreen, SecondScreen
from .gui.widgets import ErrorDialog

logger = logging.getLogger(__name__)


class App(ctk.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Application setup
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=WINDOW_BG_COLOR)

        # Set window icon
        self._set_icon()

        # Initialize platform handler
        self.platform_handler = get_platform_handler()
        logger.info(f"Running on platform: {self.platform_handler.get_platform_name()}")

        # Check admin privileges if required
        if self.platform_handler.requires_admin and not self.platform_handler.is_admin():
            message = self.platform_handler.get_admin_message()
            logger.warning(message)
            # On Windows, show error and exit. On other platforms, just warn.
            if self.platform_handler.get_platform_name() == "Windows":
                ErrorDialog.show(self, message)
                sys.exit(1)
            else:
                logger.info("Continuing without admin privileges (firewall configuration will be skipped)")

        # Initialize server
        self.server = PPTServer()
        self.server_thread = None
        self.url = ''
        self.port = 0

        # Application state
        self.status_var = ctk.StringVar(value="")
        self.current_screen = "FirstScreen"

        # Create UI container
        self.container = ctk.CTkFrame(self, fg_color=WINDOW_BG_COLOR)
        self.container.pack(fill="both", expand=True)

        # Initialize screens
        self.screens = {}
        for ScreenClass in (FirstScreen, SecondScreen):
            screen_name = ScreenClass.__name__
            screen = ScreenClass(self.container, self)
            self.screens[screen_name] = screen

        # Show initial screen
        self.show_screen(self.current_screen)

    def _set_icon(self):
        """Set the window icon."""
        try:
            # Try PNG icon (cross-platform)
            icon_image = Image.open(str(FAVICON_PNG))
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.iconphoto(True, icon_photo)
            logger.info("Window icon loaded successfully (PNG)")
        except Exception as e:
            logger.warning(f"Failed to load PNG favicon: {e}")

    def show_screen(self, screen_name):
        """
        Show the specified screen.

        Args:
            screen_name (str): Name of the screen to show
        """
        self.current_screen = screen_name
        for screen in self.screens.values():
            screen.pack_forget()
        self.screens[screen_name].pack(fill="both", expand=True)
        logger.info(f"Showing screen: {screen_name}")

    def start_server(self):
        """Start the server in a background thread."""
        if not check_network_connection():
            self.status_var.set("No network connection")
            logger.error("Cannot start server: No network connection")
            return

        self.status_var.set("Starting server...")
        logger.info("Starting server...")

        # Start server in a daemon thread
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()

    def _run_server(self):
        """Run the server (called in background thread)."""
        try:
            # Find a free port
            self.port = find_free_port()

            # Create firewall rule
            success, error_msg = self.platform_handler.create_firewall_rule(self.port)
            if not success and self.platform_handler.requires_admin:
                logger.error(f"Failed to create firewall rule: {error_msg}")
                self.status_var.set(f"Firewall error: {error_msg}")
                return

            # Build server URL
            local_ip = get_local_ip()
            self.url = f"{local_ip}:{self.port}"

            # Start the server
            self.server.start(self.port)

        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.status_var.set(f"Error: {e}")

    def get_status(self):
        """
        Get the current server status.

        Returns:
            str: Current status message
        """
        return self.server.get_status()

    def get_url(self):
        """
        Get the server URL.

        Returns:
            str: Server URL
        """
        return self.url

    def is_client_connected(self):
        """
        Check if a client is connected.

        Returns:
            bool: True if client is connected
        """
        return self.server.is_client_connected()

    def destroy(self):
        """Clean up and close the application."""
        logger.info("Initiating application shutdown")

        # Stop the server
        if self.server:
            self.server.stop()

        # Remove firewall rule
        logger.info("Removing firewall rule")
        try:
            success, error_msg = self.platform_handler.remove_firewall_rule()
            if not success:
                logger.warning(f"Failed to remove firewall rule: {error_msg}")
        except Exception as e:
            logger.error(f"Error removing firewall rule: {e}")

        logger.info("Application shutdown complete")
        super().destroy()
