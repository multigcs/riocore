import ipaddress


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
        except Exception as err:
            print(f"WARNING: can not set timeouts: {err}")

    def transfare(self, data):
        self.socket.sendto(bytes(data), (self.NET_IP, int(self.NET_PORT)))
        self.socket.settimeout(0.2)
        try:
            msgFromServer = self.socket.recvfrom(len(data) * 4)
            if len(msgFromServer[0]) == len(data):
                rec = list(msgFromServer[0])
            else:
                print(f"{self.pkg_out}/{self.pkg_in} WRONG DATASIZE: {len(msgFromServer[0])} / {len(data)}")
                rec = list(msgFromServer[0])
        except TimeoutError:
            print("Network TimeoutError")
            rec = []
        return rec

    @classmethod
    def check(cls, cstr):
        try:
            addr, port = cstr.split(":")
            ipaddress.ip_address(addr)
            return True
        except ValueError:
            return False
