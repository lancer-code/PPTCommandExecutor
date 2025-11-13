"""Socket.IO server for handling client connections and commands."""

import logging
import gevent
from flask import Flask
from flask_cors import CORS
import socketio
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import engineio.async_drivers.gevent

from .command_handler import CommandHandler

logger = logging.getLogger(__name__)


class PPTServer:
    """Socket.IO server for PowerPoint remote control."""

    def __init__(self):
        """Initialize the server."""
        self.app = Flask(__name__)
        CORS(self.app)

        self.sio = socketio.Server(cors_allowed_origins="*", async_mode='gevent')
        self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)

        self.command_handler = CommandHandler()
        self.server = None
        self.port = None

        # Connection state
        self.client_connected = False
        self.current_client_sid = None
        self.status = ""

        # Register Socket.IO event handlers
        self._register_events()

    def _register_events(self):
        """Register Socket.IO event handlers."""

        @self.sio.event
        def connect(sid, environ):
            logger.info(f"Client {sid} connected")

            # If there's an existing client, disconnect it
            if self.current_client_sid is not None and self.current_client_sid != sid:
                logger.info(f"Disconnecting previous client {self.current_client_sid}")
                self.sio.disconnect(self.current_client_sid)

            # Set the new client as the current one
            self.current_client_sid = sid
            self.client_connected = True
            self.status = "Connected"
            self.sio.emit("message", "Welcome to the server!", to=sid)

        @self.sio.event
        def disconnect(sid):
            logger.info(f"Client {sid} disconnected")

            # Only update state if the disconnecting client is the current one
            if sid == self.current_client_sid:
                self.client_connected = False
                self.status = "Waiting for connection..."
                self.current_client_sid = None

        @self.sio.event
        def command(sid, data):
            logger.info(f"Received command from {sid}: {data}")
            self.command_handler.handle_command(data)

    def start(self, port):
        """
        Start the server on the specified port.

        Args:
            port (int): The port to bind the server to
        """
        try:
            self.port = port
            self.server = pywsgi.WSGIServer(('0.0.0.0', port), self.app, handler_class=WebSocketHandler)
            self.status = "Waiting for connection..."
            logger.info(f"Server starting on port {port}")
            self.server.serve_forever()
        except Exception as e:
            self.status = f"Failed to start server: {e}"
            logger.error(f"Failed to start server: {e}")
            self.server = None
            raise

    def stop(self):
        """Stop the server."""
        if self.server is not None:
            logger.info("Stopping server")

            # Notify clients about shutdown
            if self.sio:
                logger.info("Emitting server_shutdown event")
                self.sio.emit("server_shutdown", {"message": "Server is shutting down"}, namespace='/')
                gevent.sleep(0.5)

            self.server.close()
            self.server.stop()
            self.server = None
            self.status = "Server stopped"

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
