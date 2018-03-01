from ..utils import time


class Packet:

    def __init__(self, packet_type: str, token: str, payload: str, timestamp = None):
        self.timestamp = timestamp or time.iso()
        self.packet_type = packet_type
        self.token = token
        self.payload = payload

    @classmethod
    def from_raw(cls, data: str):
        packet_type = data[:3]
        token = data[3:43]
        timestamp = data[43:66]
        payload = data[66:]
        return cls(packet_type, token, payload, timestamp)

    def to_raw(self):
        return f"{self.packet_type}{self.token}{self.timestamp}{self.payload_to_raw()}"

    def payload_to_raw(self):
        return self.payload
