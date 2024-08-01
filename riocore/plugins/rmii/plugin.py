
from riocore.plugins import PluginBase

class Plugin(PluginBase):

    def setup(self):
        self.NAME = "rmii"
        self.INFO = "rmii udp interface (experimental)"
        self.DESCRIPTION = "rmii ethernet - udp interface - only for tangprimer20k with gowin toolchain - problems with yosys (bram)"
        self.VERILOGS = ["udp.v", "rmii.v"]
        self.PINDEFAULTS = {
            "phyrst": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "netrmii_clk50m": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "netrmii_rx_crs": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "netrmii_mdc": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "netrmii_txen": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "netrmii_mdio": {
                "direction": "inout",
                "invert": False,
                "pull": None,
            },
            "netrmii_txd_0": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "netrmii_txd_1": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "netrmii_rxd_0": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "netrmii_rxd_1": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
        }
        self.TYPE = "interface"

        self.TIMING_CONSTRAINTS = {
            "PININ:netrmii_clk50m": 50000000,
        }


    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        freq = 1000000
        divider = self.system_setup["speed"] // freq // 2
        instance_parameter["DIVIDER"] = divider
        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"
        instance_parameter["TIMEOUT"] = f"32'd{self.system_setup['speed'] // 20}"
        #instance_parameter["MAC"] = self.plugin_setup.get("mac", "{8'h06")
        #instance_parameter["IP"] = self.plugin_setup.get("ip", "{8'd192")

        return instances
