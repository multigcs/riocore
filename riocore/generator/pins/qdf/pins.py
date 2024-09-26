class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        family = self.config.get("family")
        data = [""]
        if family != "Cyclone II":
            data.append('set_global_assignment -name STRATIX_DEVICE_IO_STANDARD "3.0-V LVTTL"')
        data.append("set_global_assignment -name MIN_CORE_JUNCTION_TEMP 0")
        data.append("set_global_assignment -name MAX_CORE_JUNCTION_TEMP 85")
        data.append("")
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                data.append(f"set_location_assignment {pin_config['pin']} -to {pin_config['varname']}")
                if pin_config.get("pull") == "up":
                    data.append(f"set_instance_assignment -name WEAK_PULL_UP_RESISTOR ON -to {pin_config['varname']}")
                elif pin_config.get("pullup", False):
                    print('WARNING: please change your pin-config to : "pull": "up"')
                    data.append(f"set_instance_assignment -name WEAK_PULL_UP_RESISTOR ON -to {pin_config['varname']}")

                if family != "Cyclone II":
                    iostandard = pin_config.get("iostandard", "3.3-V LVTTL").upper()
                    # drive = pin_config.get("drive", "4")
                    # slew = pin_config.get("slew", "SLOW").upper()
                    data.append(f"set_instance_assignment -name IO_STANDARD \"{iostandard}\" -to {pin_config['varname']}")

            data.append("")
        open(f"{path}/pins.qdf", "w").write("\n".join(data))
