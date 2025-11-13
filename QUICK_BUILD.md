# Quick Build Guide

## Windows Executable

**On a Windows machine with Python installed:**

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Run the build script
python build_windows.py

# 3. Find your executable
# Location: dist/PPTCommandExecutor.exe
```

**To run:**
- Right-click `PPTCommandExecutor.exe`
- Select "Run as Administrator"

---

## macOS Application

**On a macOS machine with Python installed:**

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Run the build script
python build_macos.py

# 3. Find your application
# Location: dist/PPTCommandExecutor.app
```

**To run:**
- Double-click `PPTCommandExecutor.app`
- If blocked: Right-click → Open → Open

**To install:**
```bash
mv dist/PPTCommandExecutor.app /Applications/
```

---

## Linux Binary

**On a Linux machine with Python installed:**

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Generate spec file
python build_spec.py

# 3. Build
pyinstaller PPTCommandExecutor.spec

# 4. Find your executable
# Location: dist/PPTCommandExecutor
```

**To run:**
```bash
chmod +x dist/PPTCommandExecutor
./dist/PPTCommandExecutor
```

---

## Notes

- **Build on target platform**: Build Windows .exe on Windows, macOS .app on macOS, etc.
- **First time**: Builds may take 2-5 minutes
- **File size**: Executables will be ~120-150 MB
- **No Python needed**: End users don't need Python installed
- **Full instructions**: See `BUILD_INSTRUCTIONS.md` for detailed documentation

---

## Troubleshooting

**"PyInstaller not found"**
```bash
pip install pyinstaller
```

**"Permission denied" (Linux/macOS)**
```bash
chmod +x build_macos.py  # or build_spec.py
python build_macos.py
```

**Build fails**
- Check `requirements.txt` is installed: `pip install -r requirements.txt`
- Read error messages in terminal
- Check `BUILD_INSTRUCTIONS.md` for detailed help
