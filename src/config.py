"""Configuration constants for the PPT Command Executor."""

import os
from pathlib import Path

# Application info
APP_NAME = "PPT Command Executor"
APP_VERSION = "1.0.0"

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Asset paths
ASSETS_DIR = ROOT_DIR / "assets"
FAVICON_PNG = ASSETS_DIR / "favicon.png"
FAVICON_ICO = ASSETS_DIR / "favicon.ico"
BANNER_IMAGE = ASSETS_DIR / "banner_image.png"

# Server configuration
DEFAULT_START_PORT = 5000
DEFAULT_MAX_PORT = 5100

# GUI configuration
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 750
WINDOW_BG_COLOR = "#242938"
BUTTON_COLOR = "#61AFEF"
CONNECTED_COLOR = "#44FF00"
DISCONNECTED_COLOR = "white"

# QR Code configuration
QR_CODE_SIZE = 200
QR_CODE_BOX_SIZE = 8
QR_CODE_BORDER = 2

# Logging configuration
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Status update interval (milliseconds)
STATUS_UPDATE_INTERVAL = 1000
