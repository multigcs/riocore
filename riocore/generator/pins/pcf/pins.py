class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                options = []
                if pin_config.get("pullup", False):
                    options.append("-pullup yes")
                options.append(pin_config["varname"])
                options.append(pin_config["pin"])
                data.append(f"set_io {' '.join(options)}")
            data.append("")
        open(f"{path}/pins.pcf", "w").write("\n".join(data))
