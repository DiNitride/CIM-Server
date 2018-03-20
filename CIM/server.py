import logging
import select
import socket
import threading

from CIM.utils import time


class Server:
    """
    Main server class, handling the incoming and outgoing connection
    """

    def __init__(self):
        """
        Class constructor, defines and initialises all attributes
        """
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
        # Maximum number of connections that can be left waiting to be accepted before the server will refuse
        # new connections
        self.server_socket.listen(5)
        self.logger.debug("Listening for connections")
        self.socket_list.append(self.server_socket)
        # Start threads to handle IO
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

        # Keep running the processing loop until server closes
        while not self.closed:

            # A selector iterates over socket objects and returns a list of sockets with data ready to be read
            ready_to_read, _, _ = select.select(self.socket_list, [], [], 0)

            for sock in ready_to_read:

                # If the socket to be read is the server socket, it's a new connection
                if sock == self.server_socket:
                    # Accept the new connection and add it to the connection list
                    in_socket, addr = self.server_socket.accept()
                    self.socket_list.append(in_socket)
                    self.logger.info(f"Accepted new connection on address {addr}")
                    self.broadcast(f"[{time.pretty_time()}] User {addr[0]} has connected.")
                else:
                    try:
                        self.logger.info(f"Received new message from {sock.getsockname()[0]}")
                        # Receive data in binary form and decode it
                        data = sock.recv(self.recv_buffer)
                        msg = data.decode("utf-8", errors='ignore')
                        self.broadcast(f"[{time.pretty_time()}] [{sock.getsockname()[0]}]: {msg}")
                    except (ConnectionResetError, ConnectionAbortedError):
                        # Catch any connection errors and handle them properly
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

    def broadcast(self, msg: str):
        """
        Broadcasts a message to all current connections
        """
        self.logger.info(f"Broadcasted message {msg}")
        # Iterate through all connections and broadcast message to all but the server
        # to avoid an infinite loop
        for sock in self.socket_list:
            if sock != self.server_socket:
                sock.send(f"{msg}\r\n".encode())
