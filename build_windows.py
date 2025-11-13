"""
Build script for creating Windows executable using PyInstaller.

This script should be run on a Windows machine with Python and PyInstaller installed.

Usage:
    python build_windows.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Build configuration
APP_NAME = "PPTCommandExecutor"
MAIN_SCRIPT = "main.py"
ICON_FILE = "assets/favicon.ico"

# PyInstaller options
PYINSTALLER_ARGS = [
    "pyinstaller",
    "--name", APP_NAME,
    "--onefile",  # Single executable file
    "--windowed",  # No console window
    "--icon", ICON_FILE,
    "--add-data", "assets;assets",  # Include assets folder (Windows syntax)
    "--hidden-import", "flask",
    "--hidden-import", "flask_cors",
    "--hidden-import", "socketio",
    "--hidden-import", "gevent",
    "--hidden-import", "geventwebsocket",
    "--hidden-import", "PIL",
    "--hidden-import", "customtkinter",
    "--hidden-import", "qrcode",
    "--hidden-import", "pyautogui",
    "--hidden-import", "engineio.async_drivers.gevent",
    "--clean",  # Clean PyInstaller cache
    "--noconfirm",  # Replace output directory without asking
    MAIN_SCRIPT
]


def check_requirements():
    """Check if all requirements are met."""
    print("Checking requirements...")

    # Check if on Windows
    if sys.platform != "win32":
        print("ERROR: This script should be run on Windows")
        return False

    # Check if main.py exists
    if not Path(MAIN_SCRIPT).exists():
        print(f"ERROR: {MAIN_SCRIPT} not found")
        return False

    # Check if icon file exists
    if not Path(ICON_FILE).exists():
        print(f"WARNING: Icon file {ICON_FILE} not found")

    # Check if assets folder exists
    if not Path("assets").exists():
        print("WARNING: assets folder not found")

    # Check if PyInstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        print("✓ PyInstaller is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: PyInstaller is not installed")
        print("Install it with: pip install pyinstaller")
        return False

    return True


def build():
    """Build the Windows executable."""
    print("\n" + "="*60)
    print(f"Building {APP_NAME} for Windows...")
    print("="*60 + "\n")

    if not check_requirements():
        sys.exit(1)

    # Run PyInstaller
    print("Running PyInstaller...\n")
    try:
        subprocess.run(PYINSTALLER_ARGS, check=True)
        print("\n" + "="*60)
        print("BUILD SUCCESSFUL!")
        print("="*60)
        print(f"\nExecutable location: dist/{APP_NAME}.exe")
        print(f"You can distribute the entire 'dist' folder or just the .exe file")
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()
