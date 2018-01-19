import logging
import select
import socket
import threading

from .utils import time


class Server:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_list = []
        self.recv_buffer = 4096
        self.port = 46400
        self.closed = False
        self.input_thread = threading.Thread(group=None, target=self.console_input, name="console")
        self.main_thread = threading.Thread(group=None, target=self.loop, name="loop")

    def start(self):
        """
        Starts the server
        """
        self.closed = False
        self.server_socket.bind(("0.0.0.0", self.port))
        self.logger.debug("Bound to host and port")
        # Maximum number of client connections is 5
        self.server_socket.listen(5)
        self.logger.debug("Listening for connections")
        self.socket_list.append(self.server_socket)
        self.input_thread.start()
        self.main_thread.start()

    def console_input(self):
        """
        Accepts console input to pass commands to the server
        """
        self.logger.debug("Started console input thread")
        while not self.closed:
            cmd = input()
            if cmd == "stop":
                self.closed = True

    def loop(self):
        """
        Main loop listening for connections
        """
        self.logger.debug("Starting main loop thread")
        while not self.closed:

            ready_to_read, _, _ = select.select(self.socket_list, [], [], 0)

            for sock in ready_to_read:

                if sock == self.server_socket:
                    in_socket, addr = self.server_socket.accept()
                    self.socket_list.append(in_socket)
                    self.logger.info(f"Accepted new connection on address {addr}")
                    self.broadcast(f"[{time.pretty_time()}] User {addr[0]} has connected.")
                else:
                    try:
                        # Receive data
                        self.logger.info(f"Received new message from {sock.getpeername()[0]}")
                        data = sock.recv(self.recv_buffer)
                        msg = data.decode("utf-8", errors='ignore')
                        msg = msg.strip()

                        # Pass to message handling
                        if msg == "":
                            continue

                        # Return to broadcast
                        self.broadcast(f"[{time.pretty_time()}] [{sock.getpeername()[0]}]: {msg}")

                    except (ConnectionResetError, ConnectionAbortedError):
                        if sock in self.socket_list:
                            self.socket_list.remove(sock)
                        self.broadcast(f"[{time.pretty_time()}] User {sock.getsockname()[0]} has disconnected.")

        self.logger.info("Closing all connections")
        for sock in self.socket_list:
            sock.close()
        self.logger.info("All connections closed")

        self.server_socket.close()
        self.logger.info("Server socket closed, exiting. . .")
        quit(0)

    def broadcast(self, msg):
        """
        Broadcasts a message to all current connections
        """
        msg = msg.strip()
        self.logger.info(f"Broadcasted message \"{msg}\"")
        for sock in self.socket_list:
            if sock != self.server_socket:
                sock.send(f"{msg}\r\n".encode())
