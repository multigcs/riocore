from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "w5500"
        self.INFO = "udp interface for host comunication"
        self.DESCRIPTION = "w5500 driver for the interface communication over UDP"
        self.KEYWORDS = "ethernet network udp interface"
        self.ORIGIN = "https://github.com/harout/concurrent-data-capture"
        self.TYPE = "interface"
        self.VERILOGS = ["w5500.v"]

        self.PINDEFAULTS = {
            "mosi": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "slew": "fast",
                "pos": (200, 126),
            },
            "miso": {
                "direction": "input",
                "invert": False,
                "pull": None,
                "pos": (15, 60),
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "slew": "fast",
                "pos": (200, 104),
            },
            "sel": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "pos": (200, 82),
            },
            "rst": {
                "direction": "output",
                "optional": True,
                "pos": (15, 82),
            },
            "intr": {
                "direction": "input",
                "optional": True,
                "pos": (200, 60),
            },
        }
        self.OPTIONS = {
            "mac": {
                "default": "AA:AF:FA:CC:E3:1C",
                "type": str,
                "description": "MAC-Address",
            },
            "ip": {
                "default": "192.168.10.194",
                "type": str,
                "description": "IP-Address",
            },
            "mask": {
                "default": "255.255.255.0",
                "type": str,
                "description": "Network-Mask",
            },
            "gw": {
                "default": "192.168.10.1",
                "type": str,
                "description": "Gateway IP-Address",
            },
            "port": {
                "default": 2390,
                "type": int,
                "description": "UDP-Port",
            },
            "speed": {
                "default": 10000000,
                "type": int,
                "description": "SPI clock",
            },
            "image": {
                "default": "generic",
                "type": "select",
                "options": ["generic", "w5500-mini", "w5500"],
                "description": "hardware type",
            },
        }
        speed = self.plugin_setup.get("speed", self.option_default("speed"))
        self.TIMING_CONSTRAINTS = {
            "mclk": speed,
        }
        image = self.plugin_setup.get("image", self.option_default("image"))
        if image == "w5500-mini":
            self.IMAGE_SHOW = True
            self.IMAGE = "w5500-mini.png"
        elif image == "w5500":
            self.IMAGE_SHOW = True
            self.IMAGE = "w5500.png"
            self.PINDEFAULTS["mosi"]["pos"] = (44, 184)
            self.PINDEFAULTS["miso"]["pos"] = (44, 206)
            self.PINDEFAULTS["sclk"]["pos"] = (44, 140)
            self.PINDEFAULTS["sel"]["pos"] = (44, 162)
            self.PINDEFAULTS["rst"]["pos"] = (22, 184)
            self.PINDEFAULTS["intr"]["pos"] = (22, 160)

    def cfg_info(self):
        ip = self.plugin_setup.get("ip", self.option_default("ip"))
        return f"IP: {ip}"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]

        mac = self.plugin_setup.get("mac", self.option_default("mac"))
        ip = self.plugin_setup.get("ip", self.option_default("ip"))
        gw = self.plugin_setup.get("gw", self.option_default("gw"))
        mask = self.plugin_setup.get("mask", self.option_default("mask"))
        port = self.plugin_setup.get("port", self.option_default("port"))
        speed = self.plugin_setup.get("speed", self.option_default("speed"))

        macl = mac.split(":")
        ipl = ip.split(".")
        gwl = gw.split(".")
        maskl = mask.split(".")
        instance_parameter["MAC_ADDR"] = f"{{8'h{macl[0]}, 8'h{macl[1]}, 8'h{macl[2]}, 8'h{macl[3]}, 8'h{macl[4]}, 8'h{macl[5]}}}"
        instance_parameter["IP_ADDR"] = f"{{8'd{ipl[0]}, 8'd{ipl[1]}, 8'd{ipl[2]}, 8'd{ipl[3]}}}"
        instance_parameter["NET_MASK"] = f"{{8'd{maskl[0]}, 8'd{maskl[1]}, 8'd{maskl[2]}, 8'd{maskl[3]}}}"
        instance_parameter["GW_ADDR"] = f"{{8'd{gwl[0]}, 8'd{gwl[1]}, 8'd{gwl[2]}, 8'd{gwl[3]}}}"
        instance_parameter["PORT"] = port
        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"

        divider = self.system_setup["speed"] // speed // 5
        instance_parameter["DIVIDER"] = divider

        return instances
