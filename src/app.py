"""Main application class for the PPT Command Executor."""

import customtkinter as ctk
import threading
import logging
import sys
from PIL import Image, ImageTk

from .config import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_BG_COLOR,
    FAVICON_PNG, FAVICON_ICO, ASSETS_DIR
)
from .platform import get_platform_handler
from .network.utils import get_local_ip, check_network_connection, find_free_port
from .server.socket_server import PPTServer
from .gui.screens import FirstScreen, SecondScreen
from .gui.widgets import ErrorDialog
from .utils import validate_asset_paths, validate_config

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

        # Validate assets
        self._validate_assets()

        # Initialize server
        self.server = PPTServer()
        self.server_thread = None
        self.server_starting = False  # Flag to prevent concurrent starts
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

    def _validate_assets(self):
        """Validate that required assets exist."""
        all_exist, missing = validate_asset_paths(ASSETS_DIR, FAVICON_PNG)

        if not all_exist:
            logger.warning(f"Some assets are missing: {missing}")
            logger.info("Application will continue with limited functionality")

    def start_server(self):
        """Start the server in a background thread."""
        # Prevent concurrent server starts
        if self.server_starting:
            logger.warning("Server start already in progress")
            return

        if not check_network_connection():
            self.status_var.set("No network connection")
            logger.error("Cannot start server: No network connection")
            ErrorDialog.show(self, "Cannot start server: No network connection detected")
            return

        self.server_starting = True
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
            try:
                self.port = find_free_port()
            except RuntimeError as e:
                logger.error(f"Port exhaustion: {e}")
                self.status_var.set("Error: No available ports")
                ErrorDialog.show(self, "Failed to find an available port. Please close some applications and try again.")
                return

            # Create firewall rule
            success, error_msg = self.platform_handler.create_firewall_rule(self.port)
            if not success and self.platform_handler.requires_admin:
                logger.error(f"Failed to create firewall rule: {error_msg}")
                self.status_var.set(f"Firewall error: {error_msg}")
                return

            # Build server URL
            local_ip = get_local_ip()
            self.url = f"{local_ip}:{self.port}"
            logger.info(f"Server URL: {self.url}")

            # Start the server
            self.server.start(self.port)

        except ValueError as e:
            # Invalid port
            logger.error(f"Port validation error: {e}")
            self.status_var.set(f"Configuration error: {e}")
        except RuntimeError as e:
            # Server already running or other runtime error
            logger.error(f"Runtime error starting server: {e}")
            self.status_var.set(f"Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error starting server: {e}", exc_info=True)
            self.status_var.set(f"Error: {e}")
        finally:
            self.server_starting = False

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
