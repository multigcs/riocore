class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                options = []
                if pin_config.get("pull") == "up":
                    options.append("-pullup yes")
                elif pin_config.get("pullup", False):
                    print('WARNING: please change your pin-config to : "pull": "up"')
                    options.append("-pullup yes")
                options.append(pin_config["varname"])
                options.append(pin_config["pin"])

                # iostandard = pin_config.get("iostandard", "LVTTL").upper()
                # drive = pin_config.get("drive", "4")
                # slew = pin_config.get("slew", "SLOW").upper()

                data.append(f"set_io {' '.join(options)}")
            data.append("")
        open(f"{path}/pins.pcf", "w").write("\n".join(data))
