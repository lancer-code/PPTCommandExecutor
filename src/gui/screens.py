"""Screen components for the PPT Command Executor GUI."""

import customtkinter as ctk
import logging
from .widgets import QRCodeWidget, ImageWidget
from ..config import (
    WINDOW_BG_COLOR, BUTTON_COLOR, CONNECTED_COLOR,
    DISCONNECTED_COLOR, BANNER_IMAGE, STATUS_UPDATE_INTERVAL
)

logger = logging.getLogger(__name__)


class FirstScreen(ctk.CTkFrame):
    """Initial screen with start server button."""

    def __init__(self, parent, controller):
        """
        Initialize the first screen.

        Args:
            parent: The parent widget
            controller: The main application controller
        """
        super().__init__(parent, fg_color=WINDOW_BG_COLOR)
        self.controller = controller

        # Center frame
        self.center_frame = ctk.CTkFrame(self, fg_color=WINDOW_BG_COLOR)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Status label
        self.status_label = ctk.CTkLabel(
            self.center_frame,
            textvariable=controller.status_var,
            text_color="white",
            font=("Arial", 22, "bold")
        )
        self.status_label.pack(pady=20)

        # Banner image
        self.image_widget = ImageWidget(
            self.center_frame,
            image_path=BANNER_IMAGE,
            size=(400, 400),
            fg_color=WINDOW_BG_COLOR
        )
        self.image_widget.pack(pady=20)

        # Title label
        self.title_label = ctk.CTkLabel(
            self.center_frame,
            text="PPT Command Executor",
            text_color="white",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=20)

        # Start button
        self.start_button = ctk.CTkButton(
            self.center_frame,
            text="Start Server",
            font=('Arial', 18, "bold"),
            fg_color=BUTTON_COLOR,
            text_color="white",
            width=200,
            height=50,
            command=self.start_server
        )
        self.start_button.pack(pady=20)

        # Start status update loop
        self.after(STATUS_UPDATE_INTERVAL, self.update_status)

    def start_server(self):
        """Handle the start server button click."""
        self.controller.start_server()

    def update_status(self):
        """Update the status display periodically."""
        status = self.controller.get_status()
        self.controller.status_var.set(status)

        # Switch to second screen when server is waiting for connection
        if status.startswith("Waiting for connection...") and self.controller.current_screen == "FirstScreen":
            self.controller.show_screen("SecondScreen")

        self.after(STATUS_UPDATE_INTERVAL, self.update_status)


class SecondScreen(ctk.CTkFrame):
    """Screen displaying QR code and connection information."""

    def __init__(self, parent, controller):
        """
        Initialize the second screen.

        Args:
            parent: The parent widget
            controller: The main application controller
        """
        super().__init__(parent, fg_color=WINDOW_BG_COLOR)
        self.controller = controller

        # Center frame
        self.center_frame = ctk.CTkFrame(self, fg_color=WINDOW_BG_COLOR)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Status label
        self.status_label = ctk.CTkLabel(
            self.center_frame,
            textvariable=controller.status_var,
            font=("Arial", 22, "bold")
        )
        self.status_label.pack(pady=20)

        # QR code frame
        self.qr_widget = QRCodeWidget(
            self.center_frame,
            fg_color="white",
            corner_radius=5
        )
        self.qr_widget.pack(pady=20)

        # Scan instruction
        self.scan_label = ctk.CTkLabel(
            self.center_frame,
            text="Scan QR to Connect",
            text_color="white",
            font=("Arial", 16, "bold")
        )
        self.scan_label.pack(pady=10)

        # OR separator
        self.or_label = ctk.CTkLabel(
            self.center_frame,
            text="OR",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        self.or_label.pack(pady=10)

        # Manual instruction
        self.manual_label = ctk.CTkLabel(
            self.center_frame,
            text="Manually enter the URL",
            text_color="white",
            font=("Arial", 16, "bold")
        )
        self.manual_label.pack(pady=10)

        # URL frame
        self.url_frame = ctk.CTkFrame(
            self.center_frame,
            fg_color=WINDOW_BG_COLOR,
            border_color="white",
            border_width=2,
            corner_radius=5
        )
        self.url_frame.pack(pady=10)

        # URL label
        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text="",
            text_color="white",
            font=("Arial", 16, "bold")
        )
        self.url_label.pack(padx=20, pady=10)

        # Start status update loop
        self.after(STATUS_UPDATE_INTERVAL, self.update_status)

    def update_status(self):
        """Update the status and QR code display periodically."""
        status = self.controller.get_status()
        url = self.controller.get_url()
        is_connected = self.controller.is_client_connected()

        # Update URL display
        self.url_label.configure(text=url)

        # Update status color based on connection state
        status_color = CONNECTED_COLOR if is_connected else DISCONNECTED_COLOR
        self.status_label.configure(text=status, text_color=status_color)

        # Update QR code
        if url:
            self.qr_widget.update_qr_code(url)

        self.after(STATUS_UPDATE_INTERVAL, self.update_status)
