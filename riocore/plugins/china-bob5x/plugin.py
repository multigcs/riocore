from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "china-bob5x"
        self.INFO = "5axis breakout board"
        self.KEYWORDS = "breakout board levelshifter"
        self.DESCRIPTION = ""
        self.ORIGIN = ""
        self.IMAGE_SHOW = True
        self.VERILOGS = []
        self.TYPE = "breakout"

        self.PINDEFAULTS = {
            "SLOT:P1": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 375]},
            "SLOT:P2": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 394]},
            "SLOT:P3": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 413]},
            "SLOT:P4": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 432]},
            "SLOT:P5": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 451]},
            "SLOT:P6": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 470]},
            "SLOT:P7": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 489]},
            "SLOT:P8": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 508]},
            "SLOT:P9": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 527]},
            "SLOT:P10": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 546]},
            "SLOT:P11": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 565]},
            "SLOT:P12": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 584]},
            "SLOT:P13": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [21, 603]},
            "SLOT:P14": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [40, 375]},
            "SLOT:P15": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [40, 394]},
            "SLOT:P16": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [40, 413]},
            "SLOT:P17": {"direction": "all", "edge": "target", "type": ["GPIO", "FPGA"], "optional": True, "pos": [40, 432]},
            "OPTO:in0": {"source": "SLOT:P10", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [212, 771]},
            "OPTO:in1": {"source": "SLOT:P11", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [257, 771]},
            "OPTO:in2": {"source": "SLOT:P12", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [302, 771]},
            "OPTO:in3": {"source": "SLOT:P13", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [347, 771]},
            "OPTO:in4": {"source": "SLOT:P15", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [392, 771]},
            "RELAIS:out": {"source": "SLOT:P17", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [190, 28]},
            "PWM:analog": {"source": "SLOT:P1", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [327, 28]},
            "PWM:digital": {"source": "SLOT:P1", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 223]},
            "B:dir": {"source": "SLOT:P17", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 268]},
            "B:step": {"source": "SLOT:P16", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 313]},
            "ALL:en": {"source": "SLOT:P14", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 358]},
            "A:dir": {"source": "SLOT:P9", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 403]},
            "A:step": {"source": "SLOT:P8", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 448]},
            "Z:dir": {"source": "SLOT:P7", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 493]},
            "Z:step": {"source": "SLOT:P6", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 538]},
            "Y:dir": {"source": "SLOT:P5", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 583]},
            "Y:step": {"source": "SLOT:P4", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 628]},
            "X:dir": {"source": "SLOT:P3", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 673]},
            "X:step": {"source": "SLOT:P2", "direction": "all", "edge": "source", "type": "PASSTHROUGH", "optional": True, "pos": [592, 718]},
        }
