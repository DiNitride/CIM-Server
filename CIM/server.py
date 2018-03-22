import logging
import select
import socket
import threading

from .utils.db import check_authorise_user, Login
from .packet_factory import PacketFactory
from .connection import Connection, ConnectionStates
from .packets import Packet, Message
from .token_generator import generate_session_token

# v2


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
        # This allows up to 5 connections to be waiting on the server to accept them before the server
        # will reject new connections. This is to stop the server becoming overloaded with new connections
        # In reality, this limit will not be reached as connections are accepted immidiately
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
                        self.logger.debug("Received new connection, accepting")
                        self.handshake(conn.socket.accept()[0])
                    elif conn.state == ConnectionStates.UNAUTHORISED:
                        # The second stage of the handshake, this will be a packet returning authorisation data
                        # as it is currently unauthorised
                        self.logger.debug(f"Received packet from unauthorised connection {conn}")
                        self.authorise_connection(self.recieve_data(conn), conn)
                    elif conn.state == ConnectionStates.AUTHORISED:
                        # This will be a packet returning a conformation message that it has
                        # received it's token
                        self.logger.debug(f"Received packet from unauthorised connection {conn}")
                        self.complete_handshake(self.recieve_data(conn), conn)
                    elif conn.state == ConnectionStates.CONNECTED:
                        # New packet has been sent, so receive the data and parse it
                        packet = self.recieve_data(conn)
                        if packet is None:
                            return
                        if Server.validate_packet(packet, conn.token):
                            self.process_packet(packet)

                except (ConnectionResetError, ConnectionAbortedError):
                    # This error is thrown if a client disconnects midway through a connection
                    self.disconnect(conn)

        self.shutdown()

    def disconnect(self, conn):
        """
        Disconnects a specific connection from the server
        """
        # Close connection then remove it from the socket list
        conn.socket.close()
        if conn in self.conn_list:
            self.conn_list.remove(conn)
        self.logger.info(f"Disconnected connection {conn}")

    def shutdown(self):
        """
        Closes all connections and shuts the server down
        """
        self.logger.info("Closing all connections")
        for conn in self.conn_list:
            # Disconnect every connection
            self.disconnect(conn)
        self.logger.info("All connections closed")

        # Finally close the server socket
        self.server_conn.socket.close()
        self.logger.info("Server socket closed, exiting. . .")
        quit(0)

    @staticmethod
    def validate_packet(packet, token):
        """
        This is just a static method that compares two strings. I could manually do this comparision, however
        it was easier to abstract it out into a method.
        I made it a static method of the class because it makes sense to belong here however does not depend on
        an instance
        """
        return packet.token == token

    def get_new_token(self):
        """
        Requests a new token from the generator until it receives a unique one
        """
        self.logger.debug("Generating new token")
        while True:
            # Generate a random new token
            t = generate_session_token()
            # Check if it is already in use this session
            if self.check_for_token_dup(t):
                self.logger.debug(f"Generated new token {t}")
                return t

    def check_for_token_dup(self, token):
        """
        Function to check if a token is currently attached to a connection
        """
        for conn in self.conn_list:
            # Iterate over every connection and compare tokens
            # if they match, return False
            # otherwise it will continue until the for loop is exited and return True
            if conn.token == token:
                return False
        return True

    def get_connection_index(self, conn):
        """
        Returns the index of a connection in the connection list
        """
        # Enumerate() returns every item in a list along with it's index
        # When the correct connection is found, the index is returned
        for i, c in enumerate(self.conn_list):
            if c.socket == conn.socket:
                return i

    def get_conn_from_token(self, token):
        """
        Returns the connection object referencing a token
        """
        # This method returns a connection based on it's token
        # In the event that the connection does not exist, return None
        for c in self.conn_list:
            if c.token == token:
                return c
        return None

    def update_connection(self, conn):
        """
        Updates a connection instance inside the servers internal connection storage
        """
        i = self.get_connection_index(conn)
        self.conn_list[i] = conn

    def recieve_data(self, conn):
        """
        This method receives data from a connection.
        First it receives the data, which is then utf-8 decoded and stripped of whitespace. Finally the string
        is passed into the packet factory to be turned into an instance of the relavent packet class
        """
        raw = conn.socket.recv(self.recv_buffer).decode("utf-8", errors='ignore').strip()
        self.logger.debug(f"Recieved packet from {conn.username} with data: {raw}")
        return self.factory.process(raw)

    def handshake(self, socket):
        """
        First stage of the handshake procedure. Responds to an initial connection by sending a request for it's
        authorisation.
        """
        # Create new connection object for the user
        conn = Connection(socket, ConnectionStates.UNAUTHORISED)
        # Add them to the list of connections
        self.conn_list.append(conn)
        self.logger.debug("Accepted new connection as unauthorised connection, awaiting authorisation")
        # Create a response packet requesting authorisation data
        resp = Packet(packet_type="001", token=self.server_conn.token, payload="Credentials Request")
        self.send(conn, resp)

    def authorise_connection(self, auth, conn):
        """
        After a connection has responded with authorisation data, this method validates it and
        acts accordingly.
        """
        self.logger.debug(f"Attempting to authorise user with username {auth['username']} "
                          f"and password {auth['password']}")
        # Check if the username and password presented is valid
        if check_authorise_user(auth["username"], auth["password"]) == Login.AUTHORISED:
            # Generate a new token for them
            token = self.get_new_token()
            # Create a response packet
            resp = Packet(
                packet_type="004",
                token=self.server_conn.token,
                payload=token
            )
            # Modify their connection state
            conn.set_state(ConnectionStates.AUTHORISED)
            conn.token = token
            conn.username = auth["username"]
            conn.password = auth["password"]
            self.update_connection(conn)
            # Send response
            self.send(conn, resp)
        else:
            # If invalid, respond with a disconnect packet
            resp = Packet(packet_type="003", token=self.server_conn.token, payload="Disconnect notification")
            self.send(conn, resp)
            self.disconnect(conn)

    def complete_handshake(self, packet, conn):
        """
        To complete the handhsake the client must send a message containing their new token to confirm it has been
        recieved.
        """
        if packet.token == conn.token:
            conn.set_state(ConnectionStates.CONNECTED)
            self.update_connection(conn)
            resp = Packet(packet_type="006", token=self.server_conn.token, payload="Client connected")
            self.send(conn, resp)

    def process_packet(self, packet):
        """
        This method handles all incoming packets to the server
        """
        # If the packet object is none, it means it was an invalid packet
        if packet is None:
            return
        if packet.packet_type == "100":
            # If the packet is a standard message
            # Broadcast it to the clients
            author = self.get_conn_from_token(packet.token)
            self.broadcast(Packet(
                packet_type="100",
                token=self.server_conn.token,
                payload=f"{author.username}: {packet.payload}"
            ))

    def send(self, destination, packet):
        """
        Sends a packet to a specific connection
        """
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
