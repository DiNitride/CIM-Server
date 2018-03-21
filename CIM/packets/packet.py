from ..utils import time


class Packet:
    """
    Abstract Base Class containing all shared attributes between classes
    """

    def __init__(self, packet_type: str, token: str, payload: str, timestamp = None):
        """
        Constructor class to initialise attributes
        """
        self.timestamp = timestamp or time.iso()
        self.packet_type = packet_type
        self.token = token
        self.payload = payload

    @classmethod
    def from_raw(cls, data: str):
        """
        This is another way of creating constructors for classes, however they are called differently.
        In Python, Classes can only have 1 constructor, under __init__, which is called when an instance is made
        by class(). However you can create other constructors using the @classmethod decorator. This allows you to
        create instances of the class by calling a method on it. For example, to call this constructor for this class,
        it would be Packet.from_raw(), which would return an instance of the class.
        """
        packet_type = data[:3]
        token = data[3:43]
        timestamp = data[43:66]
        payload = data[66:]
        return cls(packet_type, token, payload, timestamp)

    def __str__(self):
        """
        Internal Python method to return the class in a pretty format when printed.
        """
        return self.payload_to_raw()

    def to_raw(self):
        """
        Convert the packet into a string to be sent
        """
        return f"{self.packet_type}{self.token}{self.timestamp}{self.payload_to_raw()}"

    def payload_to_raw(self):
        """
        Method to return payload in more complex subclasses
        """
        return self.payload
