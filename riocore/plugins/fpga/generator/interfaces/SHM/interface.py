class Interface:
    def __init__(self, cstr):
        self.shm = cstr

    def transfare(self, data):
        fd = open(f"{self.shm}.tx", "wb")
        fd.write(bytes(data))
        fd.close()
        fd = open(f"{self.shm}.rx", "rb")
        msgFromServer = fd.read(len(data))
        fd.close()
        rec = list(msgFromServer)
        return rec

    @classmethod
    def check(cls, cstr):
        if cstr.startswith("/dev/shm"):
            return True
        return False
