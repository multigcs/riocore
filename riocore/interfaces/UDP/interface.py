class Interface:
    def __init__(self, cstr):
        (self.NET_IP, self.NET_PORT) = cstr.split(":")

        self.pkg_out = 0
        self.pkg_in = 0

        import socket

        print("IP:", self.NET_IP)
        print("PORT:", self.NET_PORT)

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", int(self.NET_PORT)))
        # clear buffer
        try:
            self.socket.settimeout(0.2)
            self.socket.recvfrom(100000)
        except:
            pass

    def transfare(self, data):
        self.socket.sendto(bytes(data), (self.NET_IP, int(self.NET_PORT)))
        self.socket.settimeout(0.2)
        msgFromServer = self.socket.recvfrom(len(data) * 4)
        if len(msgFromServer[0]) == len(data):
            rec = list(msgFromServer[0])
        else:
            print(f"{self.pkg_out}/{self.pkg_in} WRONG DATASIZE: {len(msgFromServer[0])} / {len(data)}")
            rec = list(msgFromServer[0])
        return rec

    @classmethod
    def check(cls, cstr):
        if cstr.startswith("192."):
            return True
        return False
