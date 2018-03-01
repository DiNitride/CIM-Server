import socket
from enum import Enum


class ConnectionStates(Enum):
    """
    An enum class to represent the different possible connection states a connection could be in.
    These can then be referenced by name but compared by value.
    For example ConnectionStates.DISCONNECTED == 0 would return True, as it compares the value
    """
    SERVER = -1
    DISCONNECTED = 0
    CONNECTED = 1
    UNAUTHORISED = 2
    AUTHORISED = 3


class Connection:
    """
    This class represents a connection to the server. It is also a wrapper around the socket objects used to communicate
    between the server and the client. Originally I was going to subclass the socket class however instead having the
    instance as an attribute of a wrapper class worked better.
    """

    def __init__(self, socket, state):
        """
        Constructor for a connection, takes in 2 parameters of the socket object and the connection state.
        """
        self.socket = socket
        self.username = None    # Username and hashed passwords will be stored within the class
        self.password = None
        self.token = ""
        self.state = state
        self.permission = 0

    def fileno(self):
        """
        This method is a wrapper function around the socket function of the same name. This is required by the
        selector object used to check when streams are ready to be read. It requires a function that returns the file
        descriptor of the socket.
        """
        return self.socket.fileno()

    # Setters for attributes of the class

    def set_username(self, username):
        self.username = username
        return self.username

    def set_password(self, password):
        self.password = password
        return password

    def set_token(self, token):
        self.token = token

    def set_state(self, state):
        self.state = state
