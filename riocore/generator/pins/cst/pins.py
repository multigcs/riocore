class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"// ### {pname} ###")
            for pin, pin_config in pins.items():
                data.append(f"IO_LOC \"{pin_config['varname']}\" {pin_config['pin']};")
                if pin_config.get("pullup", False):
                    data.append(f"IO_PORT \"{pin_config['varname']}\" IO_TYPE=LVCMOS33 PULL_MODE=UP;")
                else:
                    data.append(f"IO_PORT \"{pin_config['varname']}\" IO_TYPE=LVCMOS33;")
            data.append("")
        data.append("")
        open(f"{path}/pins.cst", "w").write("\n".join(data))
