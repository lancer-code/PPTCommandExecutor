"""
Advanced build script that generates platform-specific .spec files for PyInstaller.

This provides more control over the build process and can be customized further.

Usage:
    python build_spec.py
    pyinstaller PPTCommandExecutor.spec
"""

import sys
import platform
from pathlib import Path

# Detect platform
PLATFORM = platform.system().lower()
IS_WINDOWS = PLATFORM == "windows"
IS_MACOS = PLATFORM == "darwin"
IS_LINUX = PLATFORM == "linux"

# Configuration
APP_NAME = "PPTCommandExecutor"
MAIN_SCRIPT = "main.py"

# Platform-specific paths
if IS_WINDOWS:
    ICON_FILE = "assets/favicon.ico"
    PATH_SEP = ";"
    WINDOWED = True
elif IS_MACOS:
    ICON_FILE = "assets/favicon.icns"
    PATH_SEP = ":"
    WINDOWED = True
else:  # Linux
    ICON_FILE = "assets/favicon.png"
    PATH_SEP = ":"
    WINDOWED = False  # Keep console on Linux for debugging

# Generate .spec file content
SPEC_CONTENT = f"""# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for {APP_NAME}
# Generated for {PLATFORM}

block_cipher = None

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[
        'flask',
        'flask_cors',
        'socketio',
        'gevent',
        'gevent.lock',
        'geventwebsocket',
        'PIL',
        'PIL._tkinter_finder',
        'customtkinter',
        'qrcode',
        'pyautogui',
        'engineio.async_drivers.gevent',
        'src.platform.windows',
        'src.platform.linux',
        'src.platform.darwin',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={'not ' + str(WINDOWED)},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {'icon="' + ICON_FILE + '",' if Path(ICON_FILE).exists() else ''}
)

{'# macOS-specific app bundle' if IS_MACOS else ''}
{'app = BUNDLE(' if IS_MACOS else '# app = BUNDLE('}
{'    exe,' if IS_MACOS else '#     exe,'}
{'    name="' + APP_NAME + '.app",' if IS_MACOS else '#     name="' + APP_NAME + '.app",'}
{'    icon="' + ICON_FILE + '",' if IS_MACOS and Path(ICON_FILE).exists() else '#     icon=None,'}
{'    bundle_identifier="com.pptcommandexecutor.app",' if IS_MACOS else '#     bundle_identifier=None,'}
{'    info_plist={{' if IS_MACOS else '#     info_plist={'}
{'        "NSHighResolutionCapable": "True",' if IS_MACOS else '#         "NSHighResolutionCapable": "True",'}
{'        "LSUIElement": "0",' if IS_MACOS else '#         "LSUIElement": "0",'}
{'    }},' if IS_MACOS else '#     },'}
{')' if IS_MACOS else '# )'}
"""


def generate_spec():
    """Generate platform-specific .spec file."""
    spec_file = Path(f"{APP_NAME}.spec")

    print("="*60)
    print(f"Generating {spec_file} for {PLATFORM}")
    print("="*60)

    # Check if main script exists
    if not Path(MAIN_SCRIPT).exists():
        print(f"ERROR: {MAIN_SCRIPT} not found")
        sys.exit(1)

    # Check icon
    if Path(ICON_FILE).exists():
        print(f"✓ Icon file: {ICON_FILE}")
    else:
        print(f"WARNING: Icon file not found: {ICON_FILE}")
        if IS_MACOS:
            print("  To create .icns: sips -s format icns assets/favicon.png --out assets/favicon.icns")

    # Write spec file
    spec_file.write_text(SPEC_CONTENT)
    print(f"\n✓ Generated {spec_file}")

    print("\nNext steps:")
    print(f"  1. Install PyInstaller: pip install pyinstaller")
    print(f"  2. Build executable: pyinstaller {spec_file}")
    print(f"  3. Find output in: dist/{APP_NAME}{'/' if IS_WINDOWS else '.app' if IS_MACOS else ''}")

    if IS_WINDOWS:
        print(f"\nWindows executable will be: dist/{APP_NAME}.exe")
    elif IS_MACOS:
        print(f"\nmacOS application will be: dist/{APP_NAME}.app")
    else:
        print(f"\nLinux executable will be: dist/{APP_NAME}")


if __name__ == "__main__":
    generate_spec()
