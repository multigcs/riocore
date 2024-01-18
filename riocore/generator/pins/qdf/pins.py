class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = [""]
        data.append('set_global_assignment -name STRATIX_DEVICE_IO_STANDARD "3.0-V LVTTL"')
        data.append("set_global_assignment -name MIN_CORE_JUNCTION_TEMP 0")
        data.append("set_global_assignment -name MAX_CORE_JUNCTION_TEMP 85")
        data.append("")
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                data.append(f"set_location_assignment {pin_config['pin']} -to {pin_config['varname']}")
                if pin_config.get("pullup", False):
                    data.append(f"set_instance_assignment -name WEAK_PULL_UP_RESISTOR ON -to {pin_config['varname']}")
            data.append("")
        open(f"{path}/pins.qdf", "w").write("\n".join(data))
