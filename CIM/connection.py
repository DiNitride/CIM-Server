import socket
from enum import Enum


class ConnectionStates(Enum):
    CONNECTED = 1
    SHAKING = 2
    DISCONNECTED = 0


class Connection(socket.socket):

    def __init__(self, state, username):
        super().__init__()
        self.username = username
        self.session_token = ""
        self.state = state



