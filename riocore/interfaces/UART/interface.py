class Interface:
    def __init__(self, cstr):
        import serial

        if ":" in cstr:
            (device, baud) = cstr.split(":")
        else:
            device = cstr
            baud = 1000000

        self.ser = serial.Serial(device, baud, timeout=0.1)
        # clean_buffer
        while self.ser.inWaiting() > 0:
            self.ser.read(1)

    def transfare(self, data):
        self.ser.write(bytes(data))
        msgFromServer = self.ser.read(len(data))
        rec = list(msgFromServer)
        return rec

    @classmethod
    def check(cls, cstr):
        if cstr.startswith("/dev/tty"):
            return True
        return False
