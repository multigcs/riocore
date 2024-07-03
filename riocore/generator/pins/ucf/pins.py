class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                iostandard = pin_config.get("iostandard", "LVTTL").upper()
                drive = pin_config.get("drive", "4")
                slew = pin_config.get("slew", "SLOW").upper()
                if pin_config["direction"] == "input":
                    if pin_config.get("pullup", False):
                        data.append(f"NET \"{pin_config['varname']}\"       PULLUP | LOC = \"{pin_config['pin']}\" | IOSTANDARD = {iostandard} ;")
                    else:
                        data.append(f"NET \"{pin_config['varname']}\"       LOC = \"{pin_config['pin']}\" | IOSTANDARD = {iostandard} ;")
                else:
                    data.append(f"NET \"{pin_config['varname']}\"       LOC = \"{pin_config['pin']}\" | IOSTANDARD = {iostandard} | DRIVE = {drive} | SLEW = {slew} ;")
            data.append("")
        open(f"{path}/pins.ucf", "w").write("\n".join(data))
