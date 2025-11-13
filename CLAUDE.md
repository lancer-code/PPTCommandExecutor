# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PPT Command Executor is a Python desktop application for remotely controlling PowerPoint presentations via a Socket.IO-based server-client architecture. The app creates a local server with QR code connection support, allowing mobile devices or other computers to send presentation control commands (Next Slide, Previous Slide, Start/End Slideshow, etc.).

## Architecture

### Technology Stack
- **GUI Framework**: CustomTkinter (modern dark-themed Tkinter wrapper)
- **Server**: Flask + Socket.IO with gevent WSGI server
- **Automation**: PyAutoGUI for keyboard input simulation
- **Networking**: Socket.IO for real-time bidirectional communication
- **QR Code**: qrcode library with PIL/Pillow for image handling

### Core Components

1. **Server Layer** (lines 34-89 in main.py)
   - Flask app with CORS support
   - Socket.IO server using gevent async mode
   - Single client connection enforcement - automatically disconnects previous client when new one connects
   - Command handler with pattern matching for presentation control

2. **GUI Layer** (lines 191-438 in main.py)
   - Two-screen architecture: FirstScreen (initial) and SecondScreen (QR code display)
   - Real-time status updates via polling (1-second intervals)
   - Dynamic QR code generation based on server URL

3. **Network Management** (lines 131-189 in main.py)
   - Automatic port discovery (5000-5100 range)
   - Windows firewall rule management via netsh
   - Local IP detection for server URL generation

### Key Design Patterns

- **Global State Management**: Uses module-level globals (STATUS, PORT, URL, client_connected, current_client_sid)
- **Threading**: Server runs in daemon thread, GUI updates via after() polling
- **Admin Privilege Check**: Required for Windows firewall modification (checked on startup)

## Development Commands

### Setup
```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run from source (requires admin privileges on Windows)
python main.py

# On Windows, run as Administrator:
# Right-click main.py -> "Run as Administrator"
```

### Building Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable (Windows)
pyinstaller --onefile --windowed --icon=./bin/assets/favicon.ico --add-data "bin/assets;bin/assets" main.py

# For macOS/Linux (note the colon separator)
pyinstaller --onefile --windowed --icon=./bin/assets/favicon.ico --add-data "bin/assets:bin/assets" main.py

# Alternative: Use auto-py-to-exe (GUI-based)
auto-py-to-exe
# Load configuration from auto-py-to-exe.json
```

## Important Implementation Details

### Windows-Specific Features
- **Firewall Management**: Automatically creates/removes firewall rule named "PowerPoint Controll" (note: typo in rule_name)
- **Admin Check**: Uses ctypes.windll.shell32.IsUserAnAdmin() - only works on Windows
- **Icon Loading**: Uses both PNG (line 204) and ICO (line 209) formats for cross-platform compatibility

### Asset Paths
The application expects assets in `./bin/assets/`:
- `favicon.png` and `favicon.ico`: Window icon
- `banner_image.png`: Initial screen banner (400x400px)

These paths are relative and work both in development and when bundled with PyInstaller (using --add-data).

### Socket.IO Commands
The server accepts these commands via the 'command' event:
- `NEXT_SLIDE` / `FORWARD`: Press Right arrow
- `PREV_SLIDE` / `BACK`: Press Left arrow
- `START_SLIDESHOW`: Press F5
- `END_SLIDESHOW`: Press Esc
- `HOME`: Press Home (first slide)
- `END`: Press End (last slide)

### Connection Handling
- Only ONE client can be connected at a time
- New client connections automatically disconnect the previous client
- Status changes from "Waiting for connection..." to "Connected" (displayed in green)
- Client disconnections reset status to "Waiting for connection..."

### Network Requirements
- Requires active network connection (not 127.0.0.1)
- Server binds to 0.0.0.0 to accept connections from any network interface
- Uses local IP detection via dummy socket connection to 10.255.255.255

## Common Gotchas

1. **Admin Privileges**: Application exits with dialog if not running as administrator (Windows)
2. **Port Conflicts**: Automatically finds free port in range 5000-5100
3. **Asset Loading**: Logs errors but continues if banner/favicon missing
4. **Firewall Rule Cleanup**: remove_firewall_rule() is called on app destroy - ensure proper shutdown
5. **Threading**: Server runs in daemon thread - app exit may not gracefully shutdown server if interrupted

## Testing Notes

- Test on Windows for full functionality (firewall rules, admin checks)
- Verify cross-platform compatibility for macOS/Linux (admin check and firewall features will fail)
- Test with multiple simultaneous connection attempts to verify single-client enforcement
- Verify QR code generation with various network configurations
