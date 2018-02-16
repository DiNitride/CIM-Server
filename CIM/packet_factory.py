from .packets import Packet, AuthoisationPacket, TokenReturn

packet_map = {
    "002": AuthoisationPacket,
    "004": TokenReturn
}


class PacketFactory:

    def __getitem__(self, item):
        try:
            packet = packet_map[item]
        except KeyError:
            packet = Packet
        return packet

    def process(self, raw: str):
        return self.__getitem__(raw[:3]).from_raw(raw)
