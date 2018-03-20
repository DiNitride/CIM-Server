from . import BasePacket


class Message(BasePacket):

    def __init__(self, type: int, token: str, timestamp, channel: int, message: str):
        """
        Modify constructor to
        """
        super().__init__(type, token, timestamp, None)
        self.channel = channel
        self.message = message

    def get_packet_form(self):
        """
        Return the packet in a string form to be sent
        """
        return f"{self.type:03d}{self.token}{self.timestamp}{self.channel:03d}{self.message}"
