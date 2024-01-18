class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path, diamond=False):
        data = []
        if diamond:
            data.append("BLOCK RESETPATHS;")
            data.append("BLOCK ASYNCPATHS;")
            data.append("BANK 0 VCCIO 3.3 V;")
            data.append("BANK 1 VCCIO 3.3 V;")
            data.append("BANK 2 VCCIO 3.3 V;")
            data.append("BANK 3 VCCIO 3.3 V;")
            data.append("BANK 5 VCCIO 3.3 V;")
            data.append("BANK 6 VCCIO 3.3 V;")
            data.append("IOBUF ALLPORTS IO_TYPE=LVCMOS33;")
            data.append(f"SYSCONFIG JTAG_PORT=ENABLE  SDM_PORT=PROGRAMN  I2C_PORT=DISABLE  SLAVE_SPI_PORT=DISABLE  MCCLK_FREQ={self.config['speed'] / 1000000};")
            data.append("")
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                if pin_config["varname"] == "USRMCLK":
                    data.append(f"# this pin ({pin_config['pin']}) is not available in the lpf file, have to use the USRMCLK primitive in the verilog")
                    continue
                data.append(f"LOCATE COMP \"{pin_config['pin']}\" SITE \"{pin_config['varname']}\";")
                data.append(f"IOBUF PORT \"{pin_config['pin']}\" IO_TYPE=LVCMOS33;")
            data.append("")
        data.append("")
        open(f"{path}/pins.lpf", "w").write("\n".join(data))
