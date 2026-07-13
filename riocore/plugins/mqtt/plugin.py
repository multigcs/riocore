from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mqtt"
        self.INFO = "mqtt to hal"
        self.DESCRIPTION = "reads mqtt values and writes to hal pins"
        self.KEYWORDS = "mqtt"
        self.TYPE = "base"
        self.NEEDS = []
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = ["mqtt.py"]
        self.OPTIONS = {
            "server": {
                "type": str,
                "default": "localhost",
            },
            "port": {
                "type": int,
                "default": 1883,
            },
            "config": {
                "type": str,
                "default": "topic1:float:pin1,topic2:float:pin2",
                "comment": "topic:float:pin",
            },
        }

        self.SIGNALS = {}
        config = self.plugin_setup.get("config", self.option_default("config"))
        for part in config.split(","):
            _topic, _vtype, pin = part.strip().split(":")
            self.SIGNALS[pin] = {
                "direction": "input",
            }

    @classmethod
    def component_loader(cls, instances):
        output = []
        for inum, instance in enumerate(instances):
            server = instance.plugin_setup.get("server", instance.option_default("server"))
            port = instance.plugin_setup.get("port", instance.option_default("port"))
            config = instance.plugin_setup.get("config", instance.option_default("config"))
            output.append(f"loadusr -Wn mqtt.{inum} ./mqtt.py -n mqtt.{inum} -s {server} -p {port} -c {config}")
        output.append("")
        return "\n".join(output)
