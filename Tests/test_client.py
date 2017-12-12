import socket
import select
import threading


class Client:

    def __init__(self):
        self.port = 46400
        self.host = "localhost"
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec_thread = threading.Thread(target=self.rec)
        self.send_thread = threading.Thread(target=self.send)

    def conn(self):
        self.s.connect((self.host, self.port))
        self.rec_thread.start()
        self.send_thread.start()

    def rec(self):
        socket_list = [self.s]

        while True:
            ready_to_read, _, _ = select.select(socket_list, [], [])

            for sock in ready_to_read:

                if sock == self.s:

                    data = sock.recv(4096)

                    if not data:
                        self.s.close()
                        print("lost conn")

                    msg = data.decode("utf-8", errors='ignore')
                    msg = msg.strip()
                    print(msg)

    def send(self):
        while True:
            msg = input("")
            msg = msg.strip()
            self.s.send(msg.encode())

if __name__ == "__main__":
    c = Client()
    c.conn()
