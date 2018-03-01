from .packets import Packet, AuthoisationPacket, TokenReturn

# A dictionary that links unique packet codes to their corresponding subclass if required
packet_map = {
    "002": AuthoisationPacket,
    "004": TokenReturn
}


class PacketFactory:

    def __getitem__(self, item):
        """
        The __getitem__ procedure is unique to Python and allows me to use the builtin list/dictionary index
        syntax on my class to access items.

        This allows me to access my packet map like I was accessing it directly like `packet_map["002"]`, however the
        benefit of using __getitem__ means I can specify a default should the index not exist. This means my map only
        needs to have unique packets, as everything else will default
        """
        try:
            packet = packet_map[item]
        except KeyError:
            packet = Packet
        return packet

    def process(self, raw: str):
        """
        Function that wraps around __getitem__ if I want to call it as a method instead of using the [] syntax
        """
        return self.__getitem__(raw[:3]).from_raw(raw)
