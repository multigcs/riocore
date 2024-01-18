class Interface:
    def __init__(self, cstr):
        import spidev

        if cstr:
            (bus, device) = cstr.split("/")[-1][-3].split(".")
        else:
            bus = 0
            device = 1

        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0
        self.spi.lsbfirst = False

    def transfare(self, data):
        rec = self.spi.xfer2(data)
        return rec

    @classmethod
    def check(cls, cstr):
        if cstr.startswith("/dev/spidev"):
            return True
        return False
