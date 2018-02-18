import logging
import select
import socket
import threading

from .utils.db import check_authorise_user
from .packet_factory import PacketFactory
from .utils import time
from .connection import Connection, ConnectionStates
from .packets import Packet, Message
from .token_generator import generate_session_token


class Server:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.server_conn = Connection(socket.socket(socket.AF_INET, socket.SOCK_STREAM), ConnectionStates.SERVER)
        self.conn_list = []
        self.recv_buffer = 4096
        self.port = 46400
        self.closed = False
        self.factory = PacketFactory()
        self.input_thread = threading.Thread(group=None, target=self.console_input, name="console")
        self.main_thread = threading.Thread(group=None, target=self.loop, name="loop")

    def start(self):
        """
        Starts the server
        """
        self.closed = False
        self.server_conn.set_token(generate_session_token())
        self.server_conn.socket.bind(("0.0.0.0", self.port))
        self.logger.debug("Bound to host and port")
        self.server_conn.socket.listen(5)
        self.logger.debug("Listening for connections")
        self.conn_list.append(self.server_conn)
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

            ready_to_read, _, _ = select.select(self.conn_list, [], [], 0)

            for conn in ready_to_read:

                try:
                    if conn.state == ConnectionStates.SERVER:
                        # New connection
                        self.handshake(conn.accept())
                    elif conn.state == ConnectionStates.UNAUTHORISED:
                        self.authorise_connection(self.recieve_data(conn), conn)
                    elif conn.state == ConnectionStates.AUTHORISED:
                        self.complete_handshake(self.recieve_data(conn), conn)
                    elif conn.state == ConnectionStates.CONNECTED:
                        packet = self.recieve_data(conn)
                        if packet.packet_type == "100":
                            self.broadcast(Packet(
                                packet_type="100",
                                token=self.server_conn.token,
                                payload=f"{packet.payload}"
                            ))
                except (ConnectionResetError, ConnectionAbortedError):
                    if conn in self.conn_list:
                        self.conn_list.remove(conn)

        self.logger.info("Closing all connections")
        for conn in self.conn_list:
            conn.socket.close()
        self.logger.info("All connections closed")

        self.server_conn.socket.close()
        self.logger.info("Server socket closed, exiting. . .")
        quit(0)

    def disconnect(self, conn):
        conn.socket.close()
        if conn in self.conn_list:
            self.conn_list.remove(conn)

    def get_new_token(self):
        while True:
            t = generate_session_token()
            if self.check_for_token_dup(t):
                return t

    def check_for_token_dup(self, token):
        for conn in self.conn_list:
            if conn.token == token:
                return False
        return True

    def get_connection_index(self, conn):
        for i, c in enumerate(self.conn_list):
            if c.socket == conn.socket:
                return i

    def update_connection(self, conn):
        i = self.get_connection_index(conn)
        self.conn_list[i] = conn

    def recieve_data(self, conn):
        return self.factory.process(conn.socket.recv(self.recv_buffer).decode("utf-8", errors='ignore').strip())

    def handshake(self, conn):
        conn = Connection(conn, ConnectionStates.UNAUTHORISED)
        self.conn_list.append(conn)
        resp = Packet(packet_type="001", token=self.server_conn.token, payload="null")
        self.send(conn, resp)

    def authorise_connection(self, auth, conn):
        if check_authorise_user(auth["username"], auth["password"]):
            resp = Packet(
                packet_type="004",
                token=self.server_conn.token,
                payload=self.get_new_token()
            )
            conn.set_state(ConnectionStates.AUTHORISED)
            self.update_connection(conn)
            self.send(conn, resp)
            self.disconnect(conn)
        else:
            resp = Packet(packet_type="003", token=self.server_conn.token, payload="null")
            self.send(conn, resp)

    def complete_handshake(self, packet, conn):
        if packet.token == conn.token:
            conn.set_state(ConnectionStates.CONNECTED)
            self.update_connection(conn)
            resp = Packet(packet_type="006", token=self.server_conn.token, payload="null")
            self.send(conn, resp)

    def send(self, destination, packet):
        destination.socket.send(packet.to_raw())

    def broadcast(self, packet):
        """
        Broadcasts a message to all current connections
        """
        self.logger.info(f"Broadcasted message \"{packet}\"")
        msg = packet.to_raw()
        for conn in self.conn_list:
            if conn.state == ConnectionStates.CONNECTED:
                conn.socket.send(f"{msg}\r\n".encode())
