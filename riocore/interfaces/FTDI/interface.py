class Interface:
    def __init__(self, cstr):

        if not cstr:
            cstr = "ftdi://ftdi:2232h/2"

        from pyftdi.spi import SpiController

        self.spi = SpiController(cs_count=2)
        self.spi.configure(cstr)
        SPI_FTDI = self.spi.get_port(cs=0, freq=1e6, mode=0)

    def transfare(self, data):
        rec = list(SPI_FTDI.exchange(data, duplex=True))
        return rec

    @classmethod
    def check(cls, cstr):
        if cstr.startswith("ftdi://"):
            return True
        return False
