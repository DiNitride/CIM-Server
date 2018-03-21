from .packet import Packet


class AuthorisationPacket(Packet):

    def __init__(self, *args):
        """
        Override the constructor to separate the payload into the two separate pieces of data
        """
        super().__init__(*args)
        username, password = self.payload.split(".")
        self.auth = {"username": username, "password": password}

    def __getitem__(self, item):
        """
        Internal class that allows the use of [] notation on an instance of this class, letting me access the list
        object directly.
        """
        return self.auth[item]


class TokenReturn(Packet):
    pass
