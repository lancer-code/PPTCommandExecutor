"""
Build script for creating macOS application bundle using PyInstaller.

This script should be run on a macOS machine with Python and PyInstaller installed.

Usage:
    python build_macos.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Build configuration
APP_NAME = "PPTCommandExecutor"
MAIN_SCRIPT = "main.py"
ICON_FILE = "assets/favicon.icns"  # macOS uses .icns format

# PyInstaller options
PYINSTALLER_ARGS = [
    "pyinstaller",
    "--name", APP_NAME,
    "--onefile",  # Single executable file
    "--windowed",  # Create .app bundle
    "--add-data", "assets:assets",  # Include assets folder (macOS/Linux syntax)
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

    # Check if on macOS
    if sys.platform != "darwin":
        print("ERROR: This script should be run on macOS")
        return False

    # Check if main.py exists
    if not Path(MAIN_SCRIPT).exists():
        print(f"ERROR: {MAIN_SCRIPT} not found")
        return False

    # Check if icon file exists (optional for macOS)
    if Path(ICON_FILE).exists():
        # Add icon to PyInstaller args
        PYINSTALLER_ARGS.insert(6, "--icon")
        PYINSTALLER_ARGS.insert(7, ICON_FILE)
        print(f"✓ Icon file found: {ICON_FILE}")
    else:
        print(f"WARNING: Icon file {ICON_FILE} not found (will use default icon)")
        print("To create .icns from .png, run: sips -s format icns assets/favicon.png --out assets/favicon.icns")

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


def create_icns_from_png():
    """Create .icns icon from .png if it doesn't exist."""
    png_icon = Path("assets/favicon.png")
    icns_icon = Path("assets/favicon.icns")

    if png_icon.exists() and not icns_icon.exists():
        print("\nCreating .icns icon from .png...")
        try:
            subprocess.run([
                "sips", "-s", "format", "icns",
                str(png_icon), "--out", str(icns_icon)
            ], check=True, capture_output=True)
            print(f"✓ Created {icns_icon}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("WARNING: Could not create .icns file (sips command failed)")
            return False
    return icns_icon.exists()


def build():
    """Build the macOS application."""
    print("\n" + "="*60)
    print(f"Building {APP_NAME} for macOS...")
    print("="*60 + "\n")

    if not check_requirements():
        sys.exit(1)

    # Try to create icon if needed
    create_icns_from_png()

    # Run PyInstaller
    print("\nRunning PyInstaller...\n")
    try:
        subprocess.run(PYINSTALLER_ARGS, check=True)
        print("\n" + "="*60)
        print("BUILD SUCCESSFUL!")
        print("="*60)
        print(f"\nApplication location: dist/{APP_NAME}.app")
        print(f"\nYou can:")
        print(f"  1. Run the app: open dist/{APP_NAME}.app")
        print(f"  2. Move to Applications: mv dist/{APP_NAME}.app /Applications/")
        print(f"  3. Create DMG for distribution (requires additional tools)")
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()
