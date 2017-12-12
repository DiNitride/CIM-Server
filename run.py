import CIM

serv = CIM.Server()

#serv.start()

m = CIM.PacketClasses.Message(3, "grag", "feaf", 1, "aaa")

print(m.getPacketForm())
