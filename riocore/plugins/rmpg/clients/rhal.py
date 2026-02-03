import socket
import json

sock = None


def connect(host=None):
    global sock
    if not sock:
        ip = "localhost"
        port = 10000
        if host:
            if ":" in host:
                ip, port = host.split(":")
            else:
                ip = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, int(port))
        print("connecting to {} port {}".format(*server_address))
        sock.connect(server_address)
        ret = rcall(b'{"name": "version"}')
        print(ret)
    return sock


def rcall(message):
    sock.sendall(message)
    data = sock.recv(128000)
    return json.loads(data.decode())


class component:
    def __init__(self, host):
        self._data = {}
        connect(host)
        ret = rcall(b'{"name": "read"}')
        print(ret)
        self._data = ret

    def update(self):
        ret = rcall(b'{"name": "read"}')
        self._data = ret

    def __setitem__(self, name, value):
        if name in self._data:
            self._data[name] = value
            # data = {"name": "write", "data": self._data}
            data = {"name": "write", "data": {name: value}}
            ret = rcall(json.dumps(data).encode())
            if ret:
                self._data = ret

    def __getitem__(self, name):
        if name in self._data:
            # self.update()
            return self._data[name]
