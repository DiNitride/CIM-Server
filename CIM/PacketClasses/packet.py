

class BasePacket:

    def __init__(self, type: int, token: str, timestamp: str, payload: str):
        self.timestamp = timestamp
        self.type = type
        self.token = token
        self.payload = payload

    
