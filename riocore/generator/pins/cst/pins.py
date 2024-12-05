import os


class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"// ### {pname} ###")
            for pin, pin_config in pins.items():
                data.append(f"IO_LOC \"{pin_config['varname']}\" {pin_config['pin']};")

                iostandard = pin_config.get("iostandard", "LVCMOS33").upper()
                drive = pin_config.get("drive", "4")
                # slew = pin_config.get("slew", "SLOW").upper()

                if pin_config["direction"] == "input":
                    if pin_config.get("pullup", False) or pin_config.get("pull") == "up":
                        data.append(f"IO_PORT \"{pin_config['varname']}\" PULL_MODE=UP;")
                    elif pin_config.get("pulldown", False) or pin_config.get("pull") == "down":
                        data.append(f"IO_PORT \"{pin_config['varname']}\" PULL_MODE=DOWN;")
                    else:
                        data.append(f"IO_PORT \"{pin_config['varname']}\";")
                else:
                    data.append(f"IO_PORT \"{pin_config['varname']}\" DRIVE={drive};")
                    # IO_TYPE={iostandard} 

            data.append("")
        data.append("")
        open(os.path.join(path, "pins.cst"), "w").write("\n".join(data))
