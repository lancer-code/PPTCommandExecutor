"""PPT Command Executor - Entry point for the application."""

import customtkinter as ctk
import logging

from src.config import LOG_FORMAT, LOG_DATE_FORMAT
from src.app import App

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    # Set appearance mode
    ctk.set_appearance_mode("dark")

    # Create and run the application
    logger.info("Starting PPT Command Executor")
    app = App()
    app.mainloop()
    logger.info("PPT Command Executor closed")


if __name__ == "__main__":
    main()
