"""Laser pointer overlay module for displaying a movable dot on screen."""

import tkinter as tk
import time
import platform
import logging

logger = logging.getLogger(__name__)


class LaserPointerOverlay:
    """Transparent overlay window for displaying laser pointer dot."""

    def __init__(self):
        """Initialize laser pointer overlay."""
        self.enabled = False
        self.root = None
        self.canvas = None
        self.dot = None
        self.current_x = 100
        self.current_y = 100
        self.last_update_time = time.time()

    def enable(self):
        """Create and show overlay window."""
        if self.enabled:
            logger.warning("Laser pointer overlay already enabled")
            return

        try:
            self.root = tk.Toplevel()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")

            # Make window transparent and always on top
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', 0.9)
            self.root.overrideredirect(True)  # Remove window decorations

            # Create canvas for drawing
            self.canvas = tk.Canvas(
                self.root, bg='black',
                highlightthickness=0,
                cursor='none'
            )
            self.canvas.pack(fill=tk.BOTH, expand=True)

            # Create laser dot (red circle, 20px diameter)
            radius = 10
            self.dot = self.canvas.create_oval(
                self.current_x - radius,
                self.current_y - radius,
                self.current_x + radius,
                self.current_y + radius,
                fill='red', outline='red'
            )

            # Platform-specific click-through setup
            if platform.system() == 'Windows':
                self._setup_windows_clickthrough()

            self.enabled = True
            self._animate()
            logger.info("Laser pointer overlay enabled")
        except Exception as e:
            logger.error(f"Failed to enable laser pointer overlay: {e}")
            if self.root:
                self.root.destroy()
                self.root = None

    def disable(self):
        """Hide and destroy overlay window."""
        if not self.enabled or not self.root:
            logger.debug("Laser pointer overlay already disabled")
            return

        try:
            self.root.destroy()
            self.root = None
            self.canvas = None
            self.dot = None
            self.enabled = False
            logger.info("Laser pointer overlay disabled")
        except Exception as e:
            logger.error(f"Error disabling laser pointer overlay: {e}")

    def update_position(self, x, y):
        """
        Update laser pointer position from Socket.IO event.

        Args:
            x (float): Normalized x coordinate (0.0-1.0)
            y (float): Normalized y coordinate (0.0-1.0)
        """
        if not self.enabled or not self.root:
            return

        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Convert normalized coordinates to pixel coordinates
            self.current_x = x * screen_width
            self.current_y = y * screen_height
        except Exception as e:
            logger.error(f"Error updating laser pointer position: {e}")

    def _animate(self):
        """Animation loop for smooth rendering at 60 FPS."""
        if not self.enabled or not self.canvas:
            return

        try:
            current_time = time.time()
            elapsed = current_time - self.last_update_time

            # Target 60 FPS (16.67ms per frame)
            if elapsed >= 0.016:
                # Update dot position on canvas
                radius = 10
                self.canvas.coords(
                    self.dot,
                    self.current_x - radius,
                    self.current_y - radius,
                    self.current_x + radius,
                    self.current_y + radius
                )
                self.last_update_time = current_time

            # Schedule next frame
            if self.root:
                self.root.after(16, self._animate)
        except Exception as e:
            logger.error(f"Error in laser pointer animation loop: {e}")

    def _setup_windows_clickthrough(self):
        """Windows-specific: Make window click-through using Win32 API."""
        try:
            import ctypes
            hwnd = self.root.winfo_id()

            # Window style constants
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20

            # Get current extended style
            exstyle = ctypes.windll.user32.GetWindowLongA(hwnd, GWL_EXSTYLE)

            # Apply click-through style
            ctypes.windll.user32.SetWindowLongA(
                hwnd, GWL_EXSTYLE,
                exstyle | WS_EX_LAYERED | WS_EX_TRANSPARENT
            )

            # Set color key transparency (make black transparent)
            # Parameters: hwnd, crKey (color), bAlpha (opacity), dwFlags (LWA_COLORKEY)
            ctypes.windll.user32.SetLayeredWindowAttributes(
                hwnd, 0x000000, 255, 2  # LWA_COLORKEY = 2
            )
            logger.debug("Windows click-through enabled for laser pointer overlay")
        except Exception as e:
            logger.warning(f"Could not enable Windows click-through: {e}")
