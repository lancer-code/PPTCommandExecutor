"""Command handler for PowerPoint presentation control."""

import pyautogui
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def safe_keypress(func):
    """
    Decorator to safely execute keyboard commands with error handling.

    Args:
        func: The function to wrap

    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pyautogui.FailSafeException as e:
            logger.error(f"PyAutoGUI failsafe triggered: {e}")
            raise
        except Exception as e:
            logger.error(f"Error executing keyboard command in {func.__name__}: {e}")
            raise
    return wrapper


class CommandHandler:
    """Handles commands for controlling PowerPoint presentations."""

    def __init__(self, command_timeout=0.5):
        """
        Initialize the command handler.

        Args:
            command_timeout (float): Timeout for command execution in seconds
        """
        # Configure PyAutoGUI
        pyautogui.PAUSE = command_timeout  # Add pause between actions
        pyautogui.FAILSAFE = True  # Enable failsafe (move mouse to corner to abort)

        self.command_map = {
            "NEXT_SLIDE": self.next_slide,
            "FORWARD": self.next_slide,
            "PREV_SLIDE": self.previous_slide,
            "BACK": self.previous_slide,
            "START_SLIDESHOW": self.start_slideshow,
            "END_SLIDESHOW": self.end_slideshow,
            "HOME": self.go_to_first_slide,
            "END": self.go_to_last_slide,
        }

    def handle_command(self, command):
        """
        Execute the appropriate action for the given command.

        Args:
            command (str): The command to execute

        Returns:
            bool: True if command was handled successfully, False otherwise
        """
        # Normalize command
        if not isinstance(command, str):
            logger.error(f"Invalid command type: {type(command)}")
            return False

        command = command.strip().upper()

        if not command:
            logger.warning("Empty command received")
            return False

        handler = self.command_map.get(command)

        if handler:
            try:
                logger.info(f"Executing command: {command}")
                handler()
                logger.debug(f"Command '{command}' executed successfully")
                return True
            except pyautogui.FailSafeException:
                logger.error("PyAutoGUI failsafe triggered - aborting command execution")
                return False
            except Exception as e:
                logger.error(f"Failed to execute command '{command}': {e}")
                return False
        else:
            logger.warning(f"Unknown command received: {command}")
            return False

    @safe_keypress
    def next_slide(self):
        """Move to the next slide."""
        logger.debug("Pressing 'right' key for next slide")
        pyautogui.press("right")

    @safe_keypress
    def previous_slide(self):
        """Move to the previous slide."""
        logger.debug("Pressing 'left' key for previous slide")
        pyautogui.press("left")

    @safe_keypress
    def start_slideshow(self):
        """Start the slideshow presentation."""
        logger.debug("Pressing 'F5' to start slideshow")
        pyautogui.press("f5")

    @safe_keypress
    def end_slideshow(self):
        """End the slideshow presentation."""
        logger.debug("Pressing 'ESC' to end slideshow")
        pyautogui.press("esc")

    @safe_keypress
    def go_to_first_slide(self):
        """Go to the first slide."""
        logger.debug("Pressing 'Home' key for first slide")
        pyautogui.press("home")

    @safe_keypress
    def go_to_last_slide(self):
        """Go to the last slide."""
        logger.debug("Pressing 'End' key for last slide")
        pyautogui.press("end")
