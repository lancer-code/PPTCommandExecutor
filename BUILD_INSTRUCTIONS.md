# Build Instructions for PPT Command Executor

This document provides instructions for building executable files for Windows and macOS.

## Prerequisites

1. **Python 3.8+** installed on the target platform
2. **All dependencies installed**: `pip install -r requirements.txt`
3. **PyInstaller**: `pip install pyinstaller`

## Quick Build (Recommended)

### For Windows (.exe)

**On a Windows machine:**

```bash
# Run the automated build script
python build_windows.py
```

The executable will be created at: `dist/PPTCommandExecutor.exe`

### For macOS (.app)

**On a macOS machine:**

```bash
# Run the automated build script
python build_macos.py
```

The application bundle will be created at: `dist/PPTCommandExecutor.app`

### For Linux

**On a Linux machine:**

```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file
python build_spec.py
pyinstaller PPTCommandExecutor.spec
```

The executable will be created at: `dist/PPTCommandExecutor`

---

## Advanced Build (Using .spec files)

For more control over the build process:

1. **Generate platform-specific .spec file:**
   ```bash
   python build_spec.py
   ```

2. **Customize the .spec file** (optional):
   - Edit `PPTCommandExecutor.spec`
   - Modify hidden imports, data files, etc.

3. **Build the executable:**
   ```bash
   pyinstaller PPTCommandExecutor.spec
   ```

---

## Manual Build (PyInstaller Commands)

### Windows

```bash
pyinstaller --name PPTCommandExecutor ^
    --onefile ^
    --windowed ^
    --icon assets/favicon.ico ^
    --add-data "assets;assets" ^
    --hidden-import flask ^
    --hidden-import flask_cors ^
    --hidden-import socketio ^
    --hidden-import gevent ^
    --hidden-import gevent.lock ^
    --hidden-import geventwebsocket ^
    --hidden-import PIL ^
    --hidden-import customtkinter ^
    --hidden-import qrcode ^
    --hidden-import pyautogui ^
    --hidden-import engineio.async_drivers.gevent ^
    --clean ^
    --noconfirm ^
    main.py
```

### macOS

```bash
# First, create .icns icon from .png (if needed)
sips -s format icns assets/favicon.png --out assets/favicon.icns

# Build the app
pyinstaller --name PPTCommandExecutor \
    --onefile \
    --windowed \
    --icon assets/favicon.icns \
    --add-data "assets:assets" \
    --hidden-import flask \
    --hidden-import flask_cors \
    --hidden-import socketio \
    --hidden-import gevent \
    --hidden-import gevent.lock \
    --hidden-import geventwebsocket \
    --hidden-import PIL \
    --hidden-import customtkinter \
    --hidden-import qrcode \
    --hidden-import pyautogui \
    --hidden-import engineio.async_drivers.gevent \
    --clean \
    --noconfirm \
    main.py
```

### Linux

```bash
pyinstaller --name PPTCommandExecutor \
    --onefile \
    --add-data "assets:assets" \
    --hidden-import flask \
    --hidden-import flask_cors \
    --hidden-import socketio \
    --hidden-import gevent \
    --hidden-import gevent.lock \
    --hidden-import geventwebsocket \
    --hidden-import PIL \
    --hidden-import customtkinter \
    --hidden-import qrcode \
    --hidden-import pyautogui \
    --hidden-import engineio.async_drivers.gevent \
    --clean \
    --noconfirm \
    main.py
```

---

## Platform-Specific Notes

### Windows

- **Admin privileges**: The executable requires admin privileges to manage firewall rules
- **Right-click** the .exe and select "Run as Administrator"
- **Windows Defender**: May flag the executable as unknown. Add an exception if needed.

### macOS

- **Icon format**: macOS uses `.icns` format. Convert PNG to ICNS:
  ```bash
  sips -s format icns assets/favicon.png --out assets/favicon.icns
  ```

- **Gatekeeper**: macOS may block unsigned apps. To run:
  1. Right-click the app
  2. Select "Open"
  3. Click "Open" in the dialog

- **Code signing** (optional, for distribution):
  ```bash
  codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" \
      dist/PPTCommandExecutor.app
  ```

- **Create DMG** (optional, for distribution):
  ```bash
  # Install create-dmg
  brew install create-dmg

  # Create DMG
  create-dmg \
      --volname "PPT Command Executor" \
      --window-pos 200 120 \
      --window-size 800 400 \
      --icon-size 100 \
      --icon "PPTCommandExecutor.app" 200 190 \
      --app-drop-link 600 185 \
      "PPTCommandExecutor.dmg" \
      "dist/"
  ```

### Linux

- **Display server**: Requires X11 or Wayland
- **Permissions**: No admin required (firewall rules are optional)
- **Distribution**: Package as `.AppImage`, `.deb`, or `.rpm` for easier distribution

---

## Troubleshooting

### Build Errors

1. **Missing modules**:
   ```bash
   pip install -r requirements.txt
   ```

2. **PyInstaller not found**:
   ```bash
   pip install pyinstaller
   ```

3. **Import errors during runtime**:
   - Add missing modules to `--hidden-import` list
   - Check PyInstaller warnings during build

### Runtime Errors

1. **Assets not found**:
   - Ensure `--add-data` includes the assets folder
   - Check that assets exist in the original directory

2. **Tkinter errors on Linux**:
   ```bash
   sudo apt-get install python3-tk
   ```

3. **Permission errors**:
   - Windows: Run as Administrator
   - Linux: Run with `sudo` if firewall configuration needed

---

## Distribution Checklist

- [ ] Test executable on clean machine (without Python installed)
- [ ] Verify all assets are bundled
- [ ] Test firewall rule creation (Windows)
- [ ] Test network connectivity detection
- [ ] Test QR code generation
- [ ] Test PowerPoint command execution
- [ ] Create README for end users
- [ ] Package with license file
- [ ] Code sign (macOS/Windows for production)

---

## File Sizes (Approximate)

- **Windows .exe**: ~120-150 MB
- **macOS .app**: ~130-160 MB
- **Linux binary**: ~120-150 MB

Sizes can be reduced with:
- `--exclude-module` for unused modules
- UPX compression: `--upx-dir /path/to/upx`
- Two-file mode instead of `--onefile`

---

## Support

For build issues, check:
1. PyInstaller documentation: https://pyinstaller.org/
2. Project issues: https://github.com/your-username/ppt-command-executor/issues
3. Logs in `build/` and `dist/` directories
