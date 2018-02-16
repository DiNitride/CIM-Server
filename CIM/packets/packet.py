from ..utils import time


class Packet:

    def __init__(self, packet_type: str, token: str, payload: str):
        self.timestamp = time.iso()
        self.packet_type = packet_type
        self.token = token
        self.payload = payload

    @classmethod
    def from_raw(cls, data: str):
        packet_type = data[:3]
        token = data[3:43]
        timestamp = data[43:69]
        payload = data[69:]
        return cls(packet_type, token, timestamp, payload)

    def to_raw(self):
        return f"{self.packet_type:03d}{self.token}{self.timestamp}{self.payload_to_raw()}"

    def payload_to_raw(self):
        return self.payload
