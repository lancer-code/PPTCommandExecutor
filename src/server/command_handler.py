"""Command handler for PowerPoint presentation control."""

import pyautogui
import logging

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handles commands for controlling PowerPoint presentations."""

    def __init__(self):
        """Initialize the command handler."""
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
            bool: True if command was handled, False otherwise
        """
        handler = self.command_map.get(command)

        if handler:
            logger.info(f"Executing command: {command}")
            handler()
            return True
        else:
            logger.warning(f"Unknown command received: {command}")
            return False

    def next_slide(self):
        """Move to the next slide."""
        logger.info("Moving to the next slide...")
        pyautogui.press("right")

    def previous_slide(self):
        """Move to the previous slide."""
        logger.info("Moving to the previous slide...")
        pyautogui.press("left")

    def start_slideshow(self):
        """Start the slideshow presentation."""
        logger.info("Starting slideshow...")
        pyautogui.press("f5")

    def end_slideshow(self):
        """End the slideshow presentation."""
        logger.info("Ending slideshow...")
        pyautogui.press("esc")

    def go_to_first_slide(self):
        """Go to the first slide."""
        logger.info("Going to first slide...")
        pyautogui.press("home")

    def go_to_last_slide(self):
        """Go to the last slide."""
        logger.info("Going to last slide...")
        pyautogui.press("end")
