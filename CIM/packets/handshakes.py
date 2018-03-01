from .packet import Packet


class AuthorisationPacket(Packet):

    def __init__(self, *args):
        super().__init__(*args)
        username, password = self.payload.split(".")
        self.auth = {"username": username, "password": password}

    def __getitem__(self, item):
        return self.auth[item]


class TokenReturn(Packet):
    pass