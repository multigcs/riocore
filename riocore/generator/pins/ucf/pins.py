class Pins:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        data = []
        for pname, pins in self.config["pinlists"].items():
            data.append(f"### {pname} ###")
            for pin, pin_config in pins.items():
                data.append(f"NET \"{pin_config['pin']}\"       LOC = \"{pin_config['varname']}\";")
            data.append("")
        open(f"{path}/pins.ucf", "w").write("\n".join(data))
