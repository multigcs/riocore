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
                drive = pin_config.get("drive", "4")
                iostandard = pin_config.get("iostandard", "").upper()
                io_type = ""
                if iostandard and iostandard != "LVTTL":
                    io_type = f" IO_TYPE={iostandard}"

                if pin_config["direction"] == "input":
                    if pin_config.get("pullup", False) or pin_config.get("pull") == "up":
                        data.append(f"IO_PORT \"{pin_config['varname']}\" PULL_MODE=UP{io_type};")
                    elif pin_config.get("pulldown", False) or pin_config.get("pull") == "down":
                        data.append(f"IO_PORT \"{pin_config['varname']}\" PULL_MODE=DOWN{io_type};")
                    elif io_type:
                        data.append(f"IO_PORT \"{pin_config['varname']}\"{io_type};")
                else:
                    data.append(f"IO_PORT \"{pin_config['varname']}\" DRIVE={drive}{io_type};")

            data.append("")
        data.append("")
        open(os.path.join(path, "pins.cst"), "w").write("\n".join(data))
