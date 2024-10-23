from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "arty_mii"
        self.INFO = "udp interface for host comunication - experimental - Arty7-35t only"
        self.DESCRIPTION = ""
        self.KEYWORDS = "network ethernet interface udp"
        self.ORIGIN = "https://github.com/alexforencich/verilog-ethernet"
        self.LIMITATIONS = {
            "boards": ["Arty-a7-35t"],
            "toolchains": ["vivado"],
        }
        self.VERILOGS = [
            "sync_signal.v",
            "ssio_sdr_in.v",
            "mii_phy_if.v",
            "eth_mac_mii_fifo.v",
            "eth_mac_mii.v",
            "eth_mac_1g.v",
            "axis_gmii_rx.v",
            "axis_gmii_tx.v",
            "lfsr.v",
            "eth_axis_rx.v",
            "eth_axis_tx.v",
            "udp_complete.v",
            "udp_checksum_gen.v",
            "udp.v",
            "udp_ip_rx.v",
            "udp_ip_tx.v",
            "ip_complete.v",
            "ip.v",
            "ip_eth_rx.v",
            "ip_eth_tx.v",
            "ip_arb_mux.v",
            "arp.v",
            "arp_cache.v",
            "arp_eth_rx.v",
            "arp_eth_tx.v",
            "eth_arb_mux.v",
            "arbiter.v",
            "priority_encoder.v",
            "axis_fifo.v",
            "axis_async_fifo.v",
            "axis_async_fifo_adapter.v",
            "sync_reset.v",
            "arty_mii.v",
        ]
        self.PINDEFAULTS = {
            "phy_rx_clk": {
                "direction": "input",
                "create_clock": "-period 40.000",
                "default": "F15",
            },
            "phy_rxd0": {
                "direction": "input",
                "default": "D18",
            },
            "phy_rxd1": {
                "direction": "input",
                "default": "E17",
            },
            "phy_rxd2": {
                "direction": "input",
                "default": "E18",
            },
            "phy_rxd3": {
                "direction": "input",
                "default": "G17",
            },
            "phy_rx_dv": {
                "direction": "input",
                "default": "G16",
            },
            "phy_rx_er": {
                "direction": "input",
                "default": "C17",
            },
            "phy_tx_clk": {
                "direction": "input",
                "create_clock": "-period 40.000",
                "default": "H16",
            },
            "phy_txd0": {
                "direction": "output",
                "set_property": "IOSTANDARD LVCMOS33 SLEW SLOW DRIVE 12",
                "default": "H14",
            },
            "phy_txd1": {
                "direction": "output",
                "set_property": "IOSTANDARD LVCMOS33 SLEW SLOW DRIVE 12",
                "default": "J14",
            },
            "phy_txd2": {
                "direction": "output",
                "set_property": "IOSTANDARD LVCMOS33 SLEW SLOW DRIVE 12",
                "default": "J13",
            },
            "phy_txd3": {
                "direction": "output",
                "set_property": "IOSTANDARD LVCMOS33 SLEW SLOW DRIVE 12",
                "default": "H17",
            },
            "phy_tx_en": {
                "direction": "output",
                "default": "H15",
            },
            "phy_col": {
                "direction": "input",
                "default": "D17",
            },
            "phy_crs": {
                "direction": "input",
                "default": "G14",
            },
            "phy_ref_clk": {
                "direction": "output",
                "set_property": "IOSTANDARD LVCMOS33 SLEW SLOW DRIVE 12",
                "default": "G18",
            },
            "phy_reset_n": {
                "direction": "output",
                "set_property": "IOSTANDARD LVCMOS33 SLEW SLOW DRIVE 12",
                "default": "C16",
            },
        }
        self.TYPE = "interface"
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
            "port": {
                "default": 2390,
                "type": int,
                "description": "UDP-Port",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        instance["arguments"]["rst"] = "reset"
        instance["arguments"]["clk25"] = "sysclk25"

        ip = self.plugin_setup.get("ip", self.option_default("ip"))
        mac = self.plugin_setup.get("mac", self.option_default("mac"))
        port = self.plugin_setup.get("port", self.option_default("port"))

        ipl = ip.split(".")
        macl = mac.split(":")
        instance_parameter["IP_ADDR"] = f"{{8'd{ipl[0]}, 8'd{ipl[1]}, 8'd{ipl[2]}, 8'd{ipl[3]}}}"
        instance_parameter["MAC_ADDR"] = f"{{8'h{macl[0]}, 8'h{macl[1]}, 8'h{macl[2]}, 8'h{macl[3]}, 8'h{macl[4]}, 8'h{macl[5]}}}"
        instance_parameter["PORT"] = port

        instance_parameter["BUFFER_SIZE"] = "BUFFER_SIZE"
        instance_parameter["MSGID"] = "32'h74697277"

        return instances
