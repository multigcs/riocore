from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "hy_vfd"
        self.COMPONENT = "hy_vfd"
        self.INFO = "non-realtime component for Huanyang VFDs"
        self.DESCRIPTION = "This component connects the Huanyang VFD to the LinuxCNC HAL via a serial (RS-485) connection."
        self.KEYWORDS = "jog usb"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.PLUGIN_TYPE = "gpio"
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = []
        self.OPTIONS = {
            "spindle": {
                "type": int,
                "default": 0,
                "min": 0,
                "max": 4,
            },
            "device": {
                "type": str,
                "default": "/dev/ttyUSB0",
            },
            "baud": {
                "type": str,
                "default": "9600",
            },
            "parity": {
                "type": "select",
                "options": ["even", "odd", "none"],
                "default": "even",
            },
        }

    def hal(self, parent):
        spindle = self.plugin_setup.get("spindle", self.option_default("spindle"))
        parent.halg.setp_add(f"hy_vfd{spindle}.enable", 1)
        parent.halg.net_add(f"spindle.{spindle}.speed-out-abs", f"hy_vfd{spindle}.speed-command")
        parent.halg.net_add(f"spindle.{spindle}.forward", f"hy_vfd{spindle}.spindle-forward")
        parent.halg.net_add(f"spindle.{spindle}.reverse", f"hy_vfd{spindle}.spindle-reverse")
        parent.halg.net_add(f"spindle.{spindle}.on", f"hy_vfd{spindle}.spindle-on")

    def component_loader(cls, instances):
        output = []
        for instance in instances:
            spindle = instance.plugin_setup.get("spindle", instance.option_default("spindle"))
            device = instance.plugin_setup.get("device", instance.option_default("device"))
            baud = instance.plugin_setup.get("baud", instance.option_default("baud"))
            parity = instance.plugin_setup.get("parity", instance.option_default("parity"))
            output.append(f"loadusr -Wn hy_vfd{spindle} hy_vfd -n hy_vfd{spindle} -d {device} -p {parity} -r {baud} -t 1")
            output.append("")
        return "\n".join(output)
