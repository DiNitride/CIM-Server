import logging
import select
import socket
import threading
import time as builtin_time

from .utils.db import check_authorise_user
from .packet_factory import PacketFactory
from .utils import time
from .connection import Connection, ConnectionStates
from .packets import Packet, Message
from .token_generator import generate_session_token


class Server:

    def __init__(self):
        """
        Constructor method for the server. Requires no parameters as none of configurable
        """

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
        Starts the server. It begins by interally 'turning it on' by changing the closed attribute to True, then a
        server token is generated to send with packets, and the server binds to the external port of the host.
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
        Accepts console input to pass commands to the server. Currently unused.
        """
        self.logger.debug("Started console input thread")
        while not self.closed:
            cmd = input()
            if cmd == "stop":
                self.closed = True

    def loop(self):
        """
        Main loop listening for new connections, and for new data packets being sent.
        """
        self.logger.debug("Starting main loop thread")
        while not self.closed:

            # This selector takes a list of socket objects and returns a list that is ready to be read
            # This means I only ever have to check connections I already know have data waiting
            ready_to_read, _, _ = select.select(self.conn_list, [], [], 0)

            for conn in ready_to_read:

                try:
                    if conn.state == ConnectionStates.SERVER:
                        # New connection, as the connection that has waiting data is the server socket
                        # Accepts the new connecton, connecting it to the server and passes the socket
                        # into the handshake function
                        self.handshake(conn.socket.accept()[0])
                    elif conn.state == ConnectionStates.UNAUTHORISED:
                        # The second stage of the handshake, this will be a packet returning authorisation data
                        # as it is currently unauthorised
                        self.authorise_connection(self.recieve_data(conn), conn)
                    elif conn.state == ConnectionStates.AUTHORISED:
                        # This will be a packet returning a conformation message that it has
                        # received it's token
                        self.complete_handshake(self.recieve_data(conn), conn)
                    elif conn.state == ConnectionStates.CONNECTED:
                        # New packet has been sent, so receive the data and parse it
                        packet = self.recieve_data(conn)
                        if packet.packet_type == "100":
                            # If the packet is a standard message
                            # Broadcast it to the server
                            self.broadcast(Packet(
                                packet_type="100",
                                token=self.server_conn.token,
                                payload=f"{packet.payload}"
                            ))
                except (ConnectionResetError, ConnectionAbortedError):
                    # This error is thrown if a client disconnects midway through a connection
                    if conn in self.conn_list:
                        self.conn_list.remove(conn)

        self.shutdown()

    def disconnect(self, conn):
        """
        Disconnects a specific connection from the server
        """
        conn.socket.close()
        if conn in self.conn_list:
            self.conn_list.remove(conn)

    def shutdown(self):
        """
        Closes all connections and shuts the server down
        """
        self.logger.info("Closing all connections")
        for conn in self.conn_list:
            self.disconnect(conn)
        self.logger.info("All connections closed")

        self.server_conn.socket.close()
        self.logger.info("Server socket closed, exiting. . .")
        quit(0)

    def get_new_token(self):
        """
        Requests a new token from the generator until it receives a unique one
        """
        while True:
            t = generate_session_token()
            if self.check_for_token_dup(t):
                return t

    def check_for_token_dup(self, token):
        """
        Function to check if a token is currently attached to a connection
        """
        for conn in self.conn_list:
            if conn.token == token:
                return False
        return True

    def get_connection_index(self, conn):
        """
        Returns the index of a connection in the connection list
        """
        # Enumerate() returns every item in a list along with it's index
        for i, c in enumerate(self.conn_list):
            if c.socket == conn.socket:
                return i

    def update_connection(self, conn):
        """
        Updates a connection instance inside the servers internal connection storage
        """
        i = self.get_connection_index(conn)
        self.conn_list[i] = conn

    def recieve_data(self, conn):
        """
        This method recieves data from a connection.
        First it receives the data, which is then utf-8 decoded and stripped of whitespace. Finally the string
        is passed into the packet factory to be turned into an instance of the relavent packet class
        """
        return self.factory.process(conn.socket.recv(self.recv_buffer).decode("utf-8", errors='ignore').strip())

    def handshake(self, socket):
        """
        First stage of the handshake procedure. Responds to an initial connection by sending a request for it's
        authorisation.
        """
        conn = Connection(socket, ConnectionStates.UNAUTHORISED)
        self.conn_list.append(conn)
        resp = Packet(packet_type="001", token=self.server_conn.token, payload="null")
        self.send(conn, resp)

    def authorise_connection(self, auth, conn):
        """
        After a connection has responded with authorisation data, this method validates it and
        acts accordingly.
        """
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
        """
        Sends a packet to a specific connection
        """
        builtin_time.sleep(2)
        destination.socket.send(f"{packet.to_raw()}\r\n".encode())
        self.logger.debug(f"Sent {packet} to {destination}")

    def broadcast(self, packet):
        """
        Broadcasts a message to all current connections.
        """
        self.logger.info(f"Broadcasted message \"{packet}\"")
        msg = packet.to_raw()
        for conn in self.conn_list:
            if conn.state == ConnectionStates.CONNECTED:
                conn.socket.send(f"{msg}\r\n".encode())
