from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rmii"
        self.INFO = "rmii udp interface (experimental)"
        self.DESCRIPTION = "rmii ethernet - udp interface - only for tangprimer20k with gowin toolchain - problems with yosys (bram)"
        self.KEYWORDS = "interface network ethernet udp"
        self.ORIGIN = "https://github.com/sipeed/TangPrimer-20K-example/tree/main/Ethernet/verilog_UDP"
        self.VERILOGS = ["udp.v", "rmii.v"]
        self.LIMITATIONS = {
            "boards": ["TangPrimer20K"],
            "toolchains": ["gowin"],
        }
        self.PINDEFAULTS = {
            "netrmii_clk50m": {
                "direction": "input",
            },
            "netrmii_rx_crs": {
                "direction": "input",
            },
            "netrmii_mdc": {
                "direction": "output",
            },
            "netrmii_txen": {
                "direction": "output",
            },
            "netrmii_mdio": {
                "direction": "inout",
            },
            "netrmii_txd_0": {
                "direction": "output",
            },
            "netrmii_txd_1": {
                "direction": "output",
            },
            "netrmii_rxd_0": {
                "direction": "input",
            },
            "netrmii_rxd_1": {
                "direction": "input",
            },
            "phyrst": {
                "direction": "output",
                "optional": True,
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
        }
        self.TYPE = "interface"

        self.TIMING_CONSTRAINTS = {
            "PININ:netrmii_clk50m": 50000000,
        }

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

        macl = mac.split(":")
        ipl = ip.split(".")
        gwl = gw.split(".")
        maskl = mask.split(".")

        freq = 1000000
        divider = self.system_setup["speed"] // freq // 2
        instance_parameter["DIVIDER"] = divider
        instance_parameter["MAC_ADDR"] = f"{{8'h{macl[0]}, 8'h{macl[1]}, 8'h{macl[2]}, 8'h{macl[3]}, 8'h{macl[4]}, 8'h{macl[5]}}}"
        instance_parameter["IP_ADDR"] = f"{{8'd{ipl[0]}, 8'd{ipl[1]}, 8'd{ipl[2]}, 8'd{ipl[3]}}}"
        instance_parameter["NET_MASK"] = f"{{8'd{maskl[0]}, 8'd{maskl[1]}, 8'd{maskl[2]}, 8'd{maskl[3]}}}"
        instance_parameter["GW_ADDR"] = f"{{8'd{gwl[0]}, 8'd{gwl[1]}, 8'd{gwl[2]}, 8'd{gwl[3]}}}"
        instance_parameter["PORT"] = port
        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"
        # instance_parameter["MAC"] = self.plugin_setup.get("mac", "{8'h06")
        # instance_parameter["IP"] = self.plugin_setup.get("ip", "{8'd192")

        return instances
