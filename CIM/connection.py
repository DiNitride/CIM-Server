import socket
from enum import Enum


class ConnectionStates(Enum):
    SERVER = -1
    DISCONNECTED = 0
    CONNECTED = 1
    UNAUTHORISED = 2
    AUTHORISED = 3


class Connection():

    def __init__(self, socket, state):
        self.socket = socket
        self.username = None
        self.password = None
        self.token = ""
        self.state = state
        self.permission = 0

    def fileno(self):
        return self.socket.fileno()

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
