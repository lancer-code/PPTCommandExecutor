# PPT Command Executor

![GitHub release (latest by date)](https://img.shields.io/github/v/release/lancer-code/ppt-command-executor?color=blue&style=flat-square)
![GitHub license](https://img.shields.io/github/license/lancer-code/ppt-command-executor?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/lancer-code/ppt-command-executor?style=flat-square)

---

## 📖 Overview

**PPT Command Executor** is a desktop application that enables remote control of PowerPoint presentations using a Socket.IO-based server-client architecture. Built with Python, it features a modern GUI powered by `customtkinter`, allowing users to start a local server, generate a QR code for easy client connection, and send commands to navigate slides from a mobile device or another computer. This tool is perfect for presenters who need to manage their slides seamlessly without being tied to the presenting device.

The application creates a local server on your machine, accessible via a QR code or manual URL entry. Once connected, clients can send commands like "Next Slide," "Previous Slide," "Start Slideshow," and more, which are executed on the host machine using `pyautogui` to simulate keyboard inputs.

---

## ✨ Features

- **Remote Control**: Control PowerPoint presentations from any device using a simple web interface.
- **QR Code Connection**: Generate a QR code for quick and easy device connection without manual IP configuration.
- **Single Client Connection**: Ensures only one client is connected at a time, automatically disconnecting the previous client when a new one joins.
- **Cross-Platform Compatibility**: Works on Windows, with potential support for macOS and Linux (requires testing).
- **Modern GUI**: Built with `customtkinter` for a sleek, dark-themed interface.
- **Firewall Management**: Automatically adds and removes Windows firewall rules for the server port.
- **Error Handling**: Displays user-friendly error messages for network issues, admin privileges, and missing assets.

---

## 📸 Screenshots

| Initial Screen | QR Code Screen |
|---------------|----------------|
| ![Initial Screen](screenshots/initial-screen.png) | ![QR Code Screen](screenshots/qr-code-screen.png) |

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8 or higher** (if running from source)
- **Windows operating system** (admin privileges required for firewall rules)
- **PowerPoint** installed on the host machine

### Option 1: Run from Source
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/ppt-command-executor.git
   cd ppt-command-executor
   ```

2. **Install Dependencies**:
   Install the required Python packages using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` is missing, install the following:
   ```bash
   pip install customtkinter flask flask-cors python-socketio pyautogui qrcode pillow gevent gevent-websocket
   ```

3. **Run the Application**:
   Launch the script with admin privileges (required for firewall modifications):
   ```bash
   python ppt_command_executor.py
   ```

### Option 2: Use the Pre-Built Executable
For Windows users, download the pre-built `.exe` file from the [Releases](https://github.com/your-username/ppt-command-executor/releases) section. No Python installation is required:
1. Download the latest release (e.g., `PPT-Command-Executor-v1.0.0.exe`).
2. Run the `.exe` file with administrator privileges.
3. Follow the on-screen instructions to start the server and connect a client.

---

## 🚀 Usage

1. **Start the Server**:
   - Launch the application (via Python or the `.exe`).
   - Click the **"Start Server"** button. The app will start a local server and display a QR code along with the server URL (e.g., `192.168.X.X:PORT`).

2. **Connect a Client**:
   - On a mobile device or another computer, scan the QR code or manually enter the server URL in a browser.
   - The client will connect to the server, and the status will change to **"Connected"** (displayed in green).

3. **Control the Presentation**:
   - Use the client interface to send commands such as:
     - **Next Slide** / **Forward**
     - **Previous Slide** / **Back**
     - **Start Slideshow** (`F5`)
     - **End Slideshow** (`Esc`)
     - **Home** (first slide)
     - **End** (last slide)
   - The commands will control the PowerPoint presentation on the host machine.

4. **Disconnect**:
   - When a new client connects, the previous client is automatically disconnected.
   - Close the application to stop the server and remove the firewall rule.

---

## 💻 Development

### Dependencies
The project uses the following Python libraries:
- `customtkinter`: Modern GUI framework.
- `flask` and `python-socketio`: Server and client communication.
- `pyautogui`: Simulates keyboard inputs for PowerPoint control.
- `qrcode` and `pillow`: Generates and displays QR codes.
- `gevent` and `gevent-websocket`: Asynchronous server handling.

### Building the Executable
To build the `.exe` yourself:
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run the following command to bundle the application:
   ```bash
   pyinstaller --onefile --windowed --icon=./bin/assets/favicon.ico --add-data "bin/assets;bin/assets" ppt_command_executor.py
   ```
   - On macOS/Linux, use `--add-data "bin/assets:bin/assets"` instead.
3. The `.exe` will be generated in the `dist` folder.

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Make your changes and commit:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request on GitHub.

Please ensure your code follows the existing style and includes appropriate tests.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for a modern GUI.
- Uses [Socket.IO](https://socket.io/) for real-time communication.
- Inspired by the need for seamless remote presentation control.

---

## ❓ Support

For support or issues, please open an issue on the [GitHub Issues page](https://github.com/your-username/ppt-command-executor/issues).
