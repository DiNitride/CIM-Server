# THIS WILL NOT BE FUNCTIONAL 90% OF THE TIME I JUST LAUNCH SHIT FROM HERE LOL

import CIM

serv = CIM.Server()

#serv.start()

m = CIM.PacketClasses.Message(3, "grag", "feaf", 1, "aaa")

print(m.get_packet_form())
