import customtkinter as ctk
import threading
import socket
import subprocess
import gevent
from flask import Flask
from flask_cors import CORS
import socketio
import pyautogui
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import logging
import qrcode
import ctypes
import sys
from PIL import Image
from PIL import Image, ImageTk  # Add ImageTk for PNG support
import engineio.async_drivers.gevent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Global variables
STATUS = ""
PORT = 0
URL = ''
server = None
rule_name = "PowerPoint Controll"
Current_Screen = "FirstScreen"
client_connected = False  # Track client connection status
current_client_sid = None  # Track the current client's session ID

# Flask and Socket.IO setup
app = Flask(__name__)
CORS(app)
sio = socketio.Server(cors_allowed_origins="*", async_mode='gevent')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Socket.IO events
@sio.event
def connect(sid, environ):
    global client_connected, STATUS, current_client_sid
    logger.info(f"Client {sid} connected")
    # If there's an existing client, disconnect it
    if current_client_sid is not None and current_client_sid != sid:
        logger.info(f"Disconnecting previous client {current_client_sid}")
        sio.disconnect(current_client_sid)
    # Set the new client as the current one
    current_client_sid = sid
    client_connected = True
    STATUS = "Connected"
    sio.emit("message", "Welcome to the server!", to=sid)

@sio.event
def disconnect(sid):
    global client_connected, STATUS, current_client_sid
    logger.info(f"Client {sid} disconnected")
    # Only update state if the disconnecting client is the current one
    if sid == current_client_sid:
        client_connected = False
        STATUS = "Waiting for connection..."
        current_client_sid = None

@sio.event
def command(sid, data):
    print(f"Received command: {data}")
    match data:
        case "NEXT_SLIDE" | "FORWARD":
            print("Moving to the next slide...")
            pyautogui.press("right")
        case "PREV_SLIDE" | "BACK":
            print("Moving to the Previous slide...")
            pyautogui.press('left')
        case "START_SLIDESHOW":
            print("Starting Slideshow...")
            pyautogui.press('f5')
        case "END_SLIDESHOW":
            print("Ending Slideshow...")
            pyautogui.press('esc')
        case "HOME":
            print("Going to first slide...")
            pyautogui.press('home')
        case "END":
            print("Going to last slide...")
            pyautogui.press('end')
        case _:
            print(f"Unknown command: {data}")

# Function to check if the program is running as admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

# Function to show a styled dialog box and exit
def show_dialog_and_exit(root, message):
    dialog = ctk.CTkToplevel(root)
    dialog.title("Error")
    dialog.geometry("300x150")
    dialog.configure(fg_color="#242938")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    label = ctk.CTkLabel(
        dialog,
        text=message,
        text_color="white",
        font=("Arial", 14),
        wraplength=250
    )
    label.pack(pady=20, padx=20)
    close_button = ctk.CTkButton(
        dialog,
        text="Close",
        fg_color="#61AFEF",
        text_color="white",
        width=100,
        height=40,
        command=lambda: sys.exit()
    )
    close_button.pack(pady=10)
    dialog.grab_set()

# Global helper functions
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def check_network_connection():
    return get_local_ip() != '127.0.0.1'

def find_free_port(start_port=5000, max_port=5100):
    for port in range(start_port, max_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
            s.close()
            return port
        except OSError:
            continue
    raise RuntimeError('No free ports available')

def create_firewall_rule(port, root):
    try:
        subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=' + rule_name, 'dir=in', 'action=allow',
             'protocol=TCP', 'localport=' + str(port)], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to add firewall rule: {e.stderr}"
        show_dialog_and_exit(root, error_msg)
    except Exception as e:
        error_msg = f"Unexpected error while adding firewall rule: {str(e)}"
        show_dialog_and_exit(root, error_msg)

def remove_firewall_rule():
    subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=' + rule_name], check=False,
                   capture_output=True, text=True)

def start_server(root):
    global server, PORT, URL, STATUS
    try:
        PORT = find_free_port()
        create_firewall_rule(PORT, root)
        server = pywsgi.WSGIServer(('0.0.0.0', PORT), app, handler_class=WebSocketHandler)
        local_ip = get_local_ip()
        URL = f"{local_ip}:{PORT}"
        STATUS = "Waiting for connection..."
        logger.info(f"Server started on {URL}")
        server.serve_forever()
    except Exception as e:
        STATUS = f"Failed to start server: {e}"
        logger.error(f"Failed to start server: {e}")
        server = None

def server_thread_func(root):
    start_server(root)

# CustomTkinter Application
ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PPT Command Executor")
        self.geometry("500x750")
        self.configure(fg_color="#242938")

        # Set the window icon (favicon)
        try:
            # Option 1: Using a PNG file (cross-platform)
            icon_image = Image.open("./bin/assets/favicon.png")  # Path to your PNG file
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.iconphoto(True, icon_photo)  # Set the icon for the window

            # Option 2: Using an ICO file (Windows only)
            self.iconbitmap("./bin/assets/favicon.ico")  # Uncomment this line if using ICO on Windows
        except Exception as e:
            logger.error(f"Failed to load favicon: {e}")

        if not is_admin():
            show_dialog_and_exit(self, "Please run the program as Administrator")
            return
        self.status_var = ctk.StringVar(value=STATUS)
        self.container = ctk.CTkFrame(self, fg_color="#242938")
        self.container.pack(fill="both", expand=True)
        self.screens = {}
        for ScreenClass in (FirstScreen, SecondScreen):
            screen_name = ScreenClass.__name__
            screen = ScreenClass(self.container, self)
            self.screens[screen_name] = screen
        self.show_screen(Current_Screen)

    def show_screen(self, screen_name):
        for screen in self.screens.values():
            screen.pack_forget()
        self.screens[screen_name].pack(fill="both", expand=True)

    def destroy(self):
        global server
        logger.info("Initiating application shutdown")
        if sio:
            logger.info("Emitting server_shutdown event")
            sio.emit("server_shutdown", {"message": "Server is shutting down"}, namespace='/')
            gevent.sleep(0.5)
        if server is not None:
            logger.info("Stopping server")
            server.close()
            server.stop()
        logger.info("Removing firewall rule")
        try:
            remove_firewall_rule()
        except Exception as e:
            logger.error(f"Error removing firewall rule: {e}")
        logger.info("Completing application shutdown")
        super().destroy()

class FirstScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#242938")
        self.controller = controller
        self.center_frame = ctk.CTkFrame(self, fg_color="#242938")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.status_label = ctk.CTkLabel(
            self.center_frame,
            textvariable=controller.status_var,
            text_color="white",
            font=("Arial", 22, "bold")
        )
        self.status_label.pack(pady=20)
        try:
            banner_image_pil = Image.open("./bin/assets/banner_image.png")
            banner_image = ctk.CTkImage(
                light_image=banner_image_pil,
                dark_image=banner_image_pil,
                size=(400, 400)
            )
            self.image_label = ctk.CTkLabel(
                self.center_frame,
                image=banner_image,
                fg_color="#242938",
                text=""
            )
            self.image_label.pack(pady=20)
        except Exception as e:
            logger.error(f"Failed to load banner image: {e}")
            self.image_label = ctk.CTkLabel(
                self.center_frame,
                text="Image not found",
                text_color="red",
                font=("Arial", 16)
            )
            self.image_label.pack(pady=20)
        self.title_label = ctk.CTkLabel(
            self.center_frame,
            text="PPT Command Executor",
            text_color="white",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=20)
        self.start_button = ctk.CTkButton(
            self.center_frame,
            text="Start Server",
            font=('Arial', 18, "bold"),
            fg_color="#61AFEF",
            text_color="white",
            width=200,
            height=50,
            command=self.start_server
        )
        self.start_button.pack(pady=20)
        self.after(1000, self.update_status)

    def start_server(self):
        global STATUS, Current_Screen
        if not check_network_connection():
            STATUS = "No network connection"
            self.controller.status_var.set(STATUS)
        else:
            STATUS = "Starting server..."
            self.controller.status_var.set(STATUS)
            threading.Thread(target=server_thread_func, args=(self.controller,), daemon=True).start()

    def update_status(self):
        global STATUS, Current_Screen
        self.controller.status_var.set(STATUS)
        if STATUS.startswith("Waiting for connection...") and Current_Screen == "FirstScreen":
            Current_Screen = "SecondScreen"
            self.controller.show_screen(Current_Screen)
        self.after(1000, self.update_status)

class SecondScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#242938")
        self.controller = controller
        self.center_frame = ctk.CTkFrame(self, fg_color="#242938")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.status_label = ctk.CTkLabel(
            self.center_frame,
            textvariable=controller.status_var,
            font=("Arial", 22, "bold")
        )
        self.status_label.pack(pady=20)
        self.qr_frame = ctk.CTkFrame(
            self.center_frame,
            fg_color="white",
            corner_radius=5
        )
        self.qr_frame.pack(pady=20)
        self.canvas = ctk.CTkCanvas(
            self.qr_frame,
            width=200,
            height=200,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        self.scan_label = ctk.CTkLabel(
            self.center_frame,
            text="Scan QR to Connect",
            text_color="white",
            font=("Arial", 16, "bold")
        )
        self.scan_label.pack(pady=10)
        self.or_label = ctk.CTkLabel(
            self.center_frame,
            text="OR",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        self.or_label.pack(pady=10)
        self.manual_label = ctk.CTkLabel(
            self.center_frame,
            text="Manually enter the URL",
            text_color="white",
            font=("Arial", 16, "bold")
        )
        self.manual_label.pack(pady=10)
        self.url_frame = ctk.CTkFrame(
            self.center_frame,
            fg_color="#242938",
            border_color="white",
            border_width=2,
            corner_radius=5
        )
        self.url_frame.pack(pady=10)
        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text=URL,
            text_color="white",
            font=("Arial", 16, "bold")
        )
        self.url_label.pack(padx=20, pady=10)
        self.after(1000, self.update_status)

    def update_status(self):
        global STATUS, URL, client_connected
        self.url_label.configure(text=URL)
        if client_connected:
            self.status_label.configure(text=STATUS, text_color="#44FF00")  # Green when connected
        else:
            self.status_label.configure(text=STATUS, text_color="white")    # White when disconnected
        if URL:
            self.draw_qr_code(URL)
        self.after(1000, self.update_status)

    def draw_qr_code(self, url):
        self.canvas.delete("all")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_matrix = qr.get_matrix()
        module_size = 8
        canvas_width = 200
        canvas_height = 200
        qr_size = len(qr_matrix) * module_size
        offset_x = (canvas_width - qr_size) // 2
        offset_y = (canvas_height - qr_size) // 2
        for row in range(len(qr_matrix)):
            for col in range(len(qr_matrix[row])):
                if qr_matrix[row][col]:
                    x1 = offset_x + col * module_size
                    y1 = offset_y + row * module_size
                    x2 = x1 + module_size
                    y2 = y1 + module_size
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="black",
                        outline=""
                    )
                else:
                    x1 = offset_x + col * module_size
                    y1 = offset_y + row * module_size
                    x2 = x1 + module_size
                    y2 = y1 + module_size
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="white",
                        outline=""
                    )

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()