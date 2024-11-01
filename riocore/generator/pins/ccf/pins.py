class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path, diamond=False):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                options = []

                if pin_config["direction"] == "input":
                    if pin_config.get("pullup", False) or pin_config.get("pull") == "up":
                        options.append("PULLUP=true")
                    elif pin_config.get("pull") == "down":
                        options.append("PULLDOWN=true")

                else:
                    drive = pin_config.get("drive", "4")
                    options.append(f"DRIVE={drive}")
                    slew = pin_config.get("slew", "SLOW").lower()
                    options.append(f"DRIVE={slew}")

                data.append(f"Net \"{pin_config['varname']}\" Loc = \"{pin_config['pin']}\" {' '.join(options)};")

            data.append("")
        data.append("")
        open(f"{path}/pins.ccf", "w").write("\n".join(data))
