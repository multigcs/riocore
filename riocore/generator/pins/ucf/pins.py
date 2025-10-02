import os


class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                if not pin_config["pin"]:
                    continue
                iostandard = pin_config.get("iostandard", "LVTTL").upper()
                drive = str(pin_config.get("drive", "4"))
                slew = pin_config.get("slew", "SLOW").upper()
                pinstr = f'"{pin_config["pin"]}"'
                netstr = f'"{pin_config["varname"]}"'
                options = []
                options.append(f"LOC = {pinstr:6s}")
                options.append(f"IOSTANDARD = {iostandard:5s}")
                if pin_config["direction"] == "input":
                    if pin_config.get("pullup", False):
                        print('WARNING: please change your pin-config to : "pull": "up"')
                        options.append("PULLUP")
                    elif pin_config.get("pulldown", False):
                        print('WARNING: please change your pin-config to : "pull": "down"')
                        options.append("PULLDOWN")
                    elif pin_config.get("pull"):
                        options.append(f"PULL{pin_config['pull'].upper()}")
                else:
                    options.append(f"DRIVE = {drive:2s}")
                    options.append(f"SLEW = {slew:4s}")
                data.append(f"NET {netstr:32s} {' | '.join(options)} ;")
                if pin == "sysclk_in":
                    if self.config["osc_clock"]:
                        data.append(f'TIMESPEC TS_CLK = PERIOD "sysclk_in" {self.config["osc_clock"] / 1000000} MHz HIGH 50%;')
                        data.append(f'TIMESPEC TS_CLK = PERIOD "sysclk"    {self.config["speed"] / 1000000} MHz HIGH 50%;')
                    else:
                        data.append(f'TIMESPEC TS_CLK = PERIOD "sysclk_in" {self.config["speed"] / 1000000} MHz HIGH 50%;')
            data.append("")

        # for key, value in self.config["timing_constraints"].items():
        #    mhz = value / 1000000.0 * 100
        #    data.append(f"TIMESPEC TS_CLK = PERIOD \"{key}\"    {mhz:0.3f} MHz HIGH 50%;")
        # for key, value in self.config["timing_constraints_instance"].items():
        #    print("#", key, value)
        # data.append("")

        open(os.path.join(path, "pins.ucf"), "w").write("\n".join(data))
