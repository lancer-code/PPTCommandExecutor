PPT Command Executor
Overview
PPT Command Executor is a desktop application designed to control PowerPoint presentations remotely using a Socket.IO-based server-client architecture. Built with Python, it provides a user-friendly GUI using customtkinter and allows users to start a local server, generate a QR code for easy connection, and send commands to navigate slides from a mobile device or another computer. This tool is ideal for presenters who need a seamless way to manage their slides without being tied to the presenting device.
The application creates a local server on your machine, which can be accessed via a QR code or manual URL entry. Once connected, clients can send commands like "Next Slide," "Previous Slide," "Start Slideshow," and more, which are executed on the host machine using pyautogui to simulate keyboard inputs.
Features

Remote Control: Control PowerPoint presentations from any device using a simple web interface.
QR Code Connection: Generate a QR code to easily connect devices to the server without manual IP configuration.
Single Client Connection: Ensures only one client is connected at a time, automatically disconnecting the previous client when a new one joins.
Cross-Platform Compatibility: Works on Windows, with potential support for macOS and Linux (requires testing).
Customizable GUI: Built with customtkinter for a modern, dark-themed interface.
Firewall Management: Automatically adds and removes Windows firewall rules for the server port.
Error Handling: Displays user-friendly error messages for network issues, admin privileges, and missing assets.

Screenshots
(Add screenshots of your application here, e.g., the main GUI, QR code screen, etc. You can upload images to your repository and link them here.)
Installation
Prerequisites

Python 3.8 or higher
Windows operating system (admin privileges required for firewall rules)
PowerPoint installed on the host machine

Steps

Clone the Repository:
git clone https://github.com/your-username/ppt-command-executor.git
cd ppt-command-executor


Install Dependencies:Install the required Python packages using pip:
pip install -r requirements.txt

If there’s no requirements.txt, install the following:
pip install customtkinter flask flask-cors python-socketio pyautogui qrcode pillow gevent gevent-websocket


Run the Application:Run the script with admin privileges (required for firewall modifications):
python your_script_name.py



Using the Pre-Built Executable
For Windows users, you can download the pre-built .exe file from the Releases section. No Python installation is required:

Download the latest release (PPT-Command-Executor-vX.X.X.exe).
Run the .exe file with administrator privileges.
Follow the on-screen instructions to start the server and connect a client.

Usage

Start the Server:

Launch the application (either via Python or the .exe).
Click the "Start Server" button. The app will start a local server and display a QR code along with the server URL (e.g., 192.168.X.X:PORT).


Connect a Client:

On a mobile device or another computer, scan the QR code or manually enter the server URL in a browser.
The client will connect to the server, and the status will change to "Connected" (displayed in green).


Control the Presentation:

Use the client interface to send commands like "Next Slide," "Previous Slide," "Start Slideshow," "End Slideshow," "Home," or "End."
The commands will control the PowerPoint presentation on the host machine.


Disconnect:

When a new client connects, the previous client is automatically disconnected.
Close the application to stop the server and remove the firewall rule.



Development
Dependencies
The project uses the following Python libraries:

customtkinter: For the GUI.
flask and python-socketio: For the server and client communication.
pyautogui: To simulate keyboard inputs for PowerPoint control.
qrcode and pillow: For generating and displaying QR codes.
gevent and gevent-websocket: For asynchronous server handling.

Building the Executable
To build the .exe yourself:

Install PyInstaller:pip install pyinstaller


Run:pyinstaller --onefile --windowed --icon=./bin/assets/favicon.ico --add-data "bin/assets;bin/assets" your_script_name.py


The .exe will be in the dist folder.

Contributing
Contributions are welcome! If you’d like to contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m "Add your feature").
Push to your branch (git push origin feature/your-feature).
Open a pull request.

Please ensure your code follows the existing style and includes appropriate tests.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

Built with customtkinter for a modern GUI.
Uses Socket.IO for real-time communication.
Inspired by the need for seamless remote presentation control.


For support or issues, please open an issue on the GitHub Issues page.
