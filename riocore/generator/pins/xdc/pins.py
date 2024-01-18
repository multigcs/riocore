class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        # vivado style
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                data.append(f"set_property LOC {pin_config['pin']} [get_ports {pin_config['varname']}]")
                data.append(f"set_property IOSTANDARD LVCMOS33 [get_ports {pin_config['varname']}]")
                if pin_config.get("pullup", False):
                    data.append(f"set_property PULLUP TRUE [get_ports {pin_config['varname']}]")
            data.append("")
        open(f"{path}/pins.xdc", "w").write("\n".join(data))
