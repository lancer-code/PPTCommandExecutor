"""Reusable GUI widgets for the PPT Command Executor."""

import customtkinter as ctk
import qrcode
import logging
from PIL import Image, ImageTk
from ..config import QR_CODE_SIZE, QR_CODE_BOX_SIZE, QR_CODE_BORDER

logger = logging.getLogger(__name__)


class QRCodeWidget(ctk.CTkFrame):
    """Widget for displaying a QR code."""

    def __init__(self, parent, **kwargs):
        """
        Initialize the QR code widget.

        Args:
            parent: The parent widget
            **kwargs: Additional keyword arguments for CTkFrame
        """
        super().__init__(parent, **kwargs)

        self.canvas = ctk.CTkCanvas(
            self,
            width=QR_CODE_SIZE,
            height=QR_CODE_SIZE,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)

    def update_qr_code(self, url):
        """
        Update the QR code with a new URL.

        Args:
            url (str): The URL to encode in the QR code
        """
        if not url:
            return

        self.canvas.delete("all")

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=QR_CODE_BOX_SIZE,
                border=QR_CODE_BORDER
            )
            qr.add_data(url)
            qr.make(fit=True)

            qr_matrix = qr.get_matrix()
            module_size = QR_CODE_BOX_SIZE
            qr_size = len(qr_matrix) * module_size
            offset_x = (QR_CODE_SIZE - qr_size) // 2
            offset_y = (QR_CODE_SIZE - qr_size) // 2

            for row in range(len(qr_matrix)):
                for col in range(len(qr_matrix[row])):
                    x1 = offset_x + col * module_size
                    y1 = offset_y + row * module_size
                    x2 = x1 + module_size
                    y2 = y1 + module_size

                    color = "black" if qr_matrix[row][col] else "white"
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=color,
                        outline=""
                    )
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")


class ErrorDialog:
    """Dialog for displaying error messages."""

    @staticmethod
    def show(parent, message, title="Error"):
        """
        Show an error dialog.

        Args:
            parent: The parent window
            message (str): The error message to display
            title (str): The dialog title
        """
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.configure(fg_color="#242938")
        dialog.resizable(False, False)
        dialog.transient(parent)

        # Center the dialog
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Message label
        label = ctk.CTkLabel(
            dialog,
            text=message,
            text_color="white",
            font=("Arial", 14),
            wraplength=250
        )
        label.pack(pady=20, padx=20)

        # Close button
        close_button = ctk.CTkButton(
            dialog,
            text="Close",
            fg_color="#61AFEF",
            text_color="white",
            width=100,
            height=40,
            command=dialog.destroy
        )
        close_button.pack(pady=10)

        dialog.grab_set()
        dialog.wait_window()


class ImageWidget(ctk.CTkLabel):
    """Widget for displaying images with error handling."""

    def __init__(self, parent, image_path, size=(400, 400), **kwargs):
        """
        Initialize the image widget.

        Args:
            parent: The parent widget
            image_path (str or Path): Path to the image file
            size (tuple): (width, height) of the image
            **kwargs: Additional keyword arguments for CTkLabel
        """
        try:
            image_pil = Image.open(str(image_path))
            image = ctk.CTkImage(
                light_image=image_pil,
                dark_image=image_pil,
                size=size
            )
            super().__init__(parent, image=image, text="", **kwargs)
        except Exception as e:
            logger.error(f"Failed to load image from {image_path}: {e}")
            # Create label with error message instead
            super().__init__(
                parent,
                text="Image not found",
                text_color="red",
                font=("Arial", 16),
                **kwargs
            )
