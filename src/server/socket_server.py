"""Socket.IO server for handling client connections and commands."""

import logging
import gevent
from gevent.lock import Semaphore
from enum import Enum
from flask import Flask
from flask_cors import CORS
import socketio
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import engineio.async_drivers.gevent

from .command_handler import CommandHandler
from ..gui.laser_overlay import LaserPointerOverlay

logger = logging.getLogger(__name__)


class ServerState(Enum):
    """Server state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class PPTServer:
    """Socket.IO server for PowerPoint remote control."""

    def __init__(self):
        """Initialize the server."""
        self.app = Flask(__name__)
        CORS(self.app)

        self.sio = None
        self.command_handler = CommandHandler()
        self.laser_overlay = LaserPointerOverlay()
        self.server = None
        self.port = None

        # Server state
        self.state = ServerState.STOPPED
        self._state_lock = Semaphore()

        # Connection state
        self.client_connected = False
        self.current_client_sid = None
        self.status = ""

        # Initialize Socket.IO
        self._initialize_socketio()

    def _initialize_socketio(self):
        """Initialize Socket.IO server with error handling."""
        try:
            self.sio = socketio.Server(cors_allowed_origins="*", async_mode='gevent')
            self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)
            self._register_events()
            logger.info("Socket.IO initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Socket.IO: {e}")
            self.state = ServerState.ERROR
            raise

    def _register_events(self):
        """Register Socket.IO event handlers."""

        @self.sio.event
        def connect(sid, environ):
            logger.info(f"Client {sid} connected from {environ.get('REMOTE_ADDR', 'unknown')}")

            # Validate server is in correct state
            if self.state != ServerState.RUNNING:
                logger.warning(f"Client attempted connection while server in state: {self.state}")
                return False

            # If there's an existing client, disconnect it
            if self.current_client_sid is not None and self.current_client_sid != sid:
                logger.info(f"Disconnecting previous client {self.current_client_sid}")
                try:
                    self.sio.disconnect(self.current_client_sid)
                except Exception as e:
                    logger.error(f"Error disconnecting previous client: {e}")

            # Set the new client as the current one
            self.current_client_sid = sid
            self.client_connected = True
            self.status = "Connected"

            try:
                self.sio.emit("message", "Welcome to the server!", to=sid)
            except Exception as e:
                logger.error(f"Error sending welcome message: {e}")

        @self.sio.event
        def disconnect(sid):
            logger.info(f"Client {sid} disconnected")

            # Only update state if the disconnecting client is the current one
            if sid == self.current_client_sid:
                self.client_connected = False
                self.status = "Waiting for connection..." if self.state == ServerState.RUNNING else "Server stopped"
                self.current_client_sid = None

        @self.sio.event
        def command(sid, data):
            logger.info(f"Received command from {sid}: {data}")

            # Validate command data
            if not isinstance(data, str):
                logger.warning(f"Invalid command type from {sid}: {type(data)}")
                return

            # Only accept commands from the current client
            if sid != self.current_client_sid:
                logger.warning(f"Command rejected from unauthorized client {sid}")
                return

            try:
                success = self.command_handler.handle_command(data)
                if not success:
                    self.sio.emit("error", {"message": f"Unknown command: {data}"}, to=sid)
            except Exception as e:
                logger.error(f"Error handling command '{data}': {e}")
                try:
                    self.sio.emit("error", {"message": "Command execution failed"}, to=sid)
                except Exception:
                    pass

        @self.sio.event
        def laser_pointer_toggle(sid, data):
            """Handle laser pointer enable/disable."""
            if sid != self.current_client_sid:
                logger.warning(f"Laser toggle rejected from unauthorized client {sid}")
                return

            try:
                enabled = data.get('enabled', False) if isinstance(data, dict) else False
                logger.info(f"Laser pointer toggle: {enabled}")

                if enabled:
                    self.laser_overlay.enable()
                else:
                    self.laser_overlay.disable()
            except Exception as e:
                logger.error(f"Error handling laser pointer toggle: {e}")

        @self.sio.event
        def laser_pointer_move(sid, data):
            """Handle laser pointer movement (60 Hz)."""
            if sid != self.current_client_sid:
                return  # Silent reject for high-frequency events

            try:
                if not isinstance(data, dict):
                    return

                x = data.get('x', 0.5)
                y = data.get('y', 0.5)

                # Update overlay position (non-blocking)
                if self.laser_overlay.enabled:
                    self.laser_overlay.update_position(x, y)
            except Exception as e:
                logger.error(f"Error handling laser pointer move: {e}")

    def start(self, port):
        """
        Start the server on the specified port.

        Args:
            port (int): The port to bind the server to

        Raises:
            RuntimeError: If server is already running or in invalid state
            ValueError: If port is invalid
        """
        # Validate port
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValueError(f"Invalid port number: {port}")

        # Check state with lock
        with self._state_lock:
            if self.state != ServerState.STOPPED:
                raise RuntimeError(f"Cannot start server: current state is {self.state.value}")

            self.state = ServerState.STARTING
            self.status = "Starting server..."

        try:
            self.port = port
            self.server = pywsgi.WSGIServer(
                ('0.0.0.0', port),
                self.app,
                handler_class=WebSocketHandler,
                log=logger
            )

            with self._state_lock:
                self.state = ServerState.RUNNING
                self.status = "Waiting for connection..."

            logger.info(f"Server started successfully on port {port}")
            self.server.serve_forever()

        except OSError as e:
            # Port already in use or permission denied
            error_msg = f"Failed to bind to port {port}: {e}"
            logger.error(error_msg)
            with self._state_lock:
                self.state = ServerState.ERROR
                self.status = error_msg
            self.server = None
            raise RuntimeError(error_msg) from e

        except Exception as e:
            error_msg = f"Failed to start server: {e}"
            logger.error(error_msg)
            with self._state_lock:
                self.state = ServerState.ERROR
                self.status = error_msg
            self.server = None
            raise

        finally:
            # Ensure state is updated if server stops
            if self.state == ServerState.RUNNING:
                with self._state_lock:
                    self.state = ServerState.STOPPED
                    self.status = "Server stopped"

    def stop(self, timeout=5.0):
        """
        Stop the server gracefully.

        Args:
            timeout (float): Maximum time to wait for shutdown in seconds
        """
        with self._state_lock:
            if self.state == ServerState.STOPPED:
                logger.info("Server already stopped")
                return

            if self.state != ServerState.RUNNING:
                logger.warning(f"Attempting to stop server in state: {self.state}")

            self.state = ServerState.STOPPING

        logger.info("Stopping server")

        # Disable laser overlay
        if self.laser_overlay:
            try:
                self.laser_overlay.disable()
            except Exception as e:
                logger.error(f"Error disabling laser overlay: {e}")

        # Notify clients about shutdown
        if self.sio and self.client_connected:
            try:
                logger.info("Notifying clients of shutdown")
                self.sio.emit("server_shutdown", {"message": "Server is shutting down"}, namespace='/')
                gevent.sleep(0.5)  # Give clients time to receive notification
            except Exception as e:
                logger.error(f"Error notifying clients of shutdown: {e}")

        # Stop the server
        if self.server is not None:
            try:
                self.server.close()
                self.server.stop(timeout=timeout)
                logger.info("Server stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
            finally:
                self.server = None

        with self._state_lock:
            self.state = ServerState.STOPPED
            self.status = "Server stopped"
            self.client_connected = False
            self.current_client_sid = None

    def get_status(self):
        """
        Get the current server status.

        Returns:
            str: The current status message
        """
        return self.status

    def is_client_connected(self):
        """
        Check if a client is currently connected.

        Returns:
            bool: True if a client is connected, False otherwise
        """
        return self.client_connected
