from riocore import PluginImages
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        # some plugin infos (used by make readme's and in the gui for the titles and tooltips)
        self.NAME = "pwmout"
        self.INFO = "pwm output"
        self.DESCRIPTION = "to control AC/DC-Motors or for analog outputs"
        # search strings for the rio-setup gui, but it search also over name, info and description (add new plugin)
        self.KEYWORDS = "joint dcservo acservo 10v 5v dac analog"
        # optional list of possible images (for the flow frontend)
        self.IMAGES = PluginImages.pwmout
        # a link to the orign sources of the verilog code (empty for own code)
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        # list of verilog files in the plugin folder to copy to the GATEWARE folder while generate the Output
        self.VERILOGS = ["pwmout.v"]
        # the plugin type, there are io, joint and expansion
        self.TYPE = "joint"
        # dictionary of all in/out pins for the plugin (optional pins are possible)
        self.PINDEFAULTS = {
            "pwm": {
                "direction": "output",
            },
            "dir": {
                "direction": "output",
                "optional": True,
            },
            "en": {
                "direction": "output",
                "optional": True,
            },
        }
        # plugin options to setup some compile time values
        self.OPTIONS = {
            "frequency": {
                "default": 10000,
                "type": int,
                "min": 10,
                "max": 1000000,
                "unit": "Hz",
                "description": "PWM frequency",
            },
        }

        freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = 24000000 // freq  # 24Mhz is the lowest used FPGA clock
        self.DESCRIPTION += f"\n\n PWM-Resolution: >= {self.clog2(divider) - 1}bit at {freq}Hz and 24Mhz FPGA-Clock"

        # additional options depands on other options
        bitlist = []
        for width in [32, 24, 16, 8]:
            if width < self.clog2(divider):
                break
            bitlist.append(str(width))
        self.OPTIONS.update(
            {
                "bitwidth": {
                    "default": "32",
                    "type": "select",
                    "options": bitlist,
                    "unit": "bits",
                    "description": "bit-width on the interface frequency",
                },
            }
        )

        bitwidth = int(self.plugin_setup.get("bitwidth", self.OPTIONS["bitwidth"]["default"]))
        if bitwidth < self.clog2(divider):
            print(f"  ERROR: {self.instances_name}: please incrase the bitwidth to min. {self.clog2(divider)}bit")
            self.plugin_setup["bitwidth"] = bitlist[-1]
            bitwidth = int(bitlist[-1])

        # all the values that needs to transfare betweed PC and FPGA
        self.INTERFACE = {
            "dty": {
                "size": bitwidth,
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
        }
        # all the linuxcnc hal-pins/hal-signals (normaly the same as in self.INTERFACE)
        self.SIGNALS = {
            "dty": {
                "direction": "output",
                "min": 0,
                "max": 100,
                "unit": "%",
                "absolute": False,
                "setup": {
                    "min": {
                        "default": 0,
                        "type": int,
                        "min": -1000000,
                        "max": 1000000,
                        "unit": "",
                        "description": "minimum value (0% dty)",
                    },
                    "max": {
                        "default": 100,
                        "type": int,
                        "min": -1000000,
                        "max": 1000000,
                        "unit": "",
                        "description": "maximum value (100% dty)",
                    },
                },
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        # here is an example how to modify the above dictionarys depends on the configured options (self.OPTIONS)
        if "dir" in self.plugin_setup.get("pins", {}):
            self.SIGNALS["dty"]["min"] = -self.SIGNALS["dty"]["max"]

    def cfg_info(self):
        freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        return f"{freq} Hz"

    # optional function, only needed if you add parameter to the verilog functions
    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_predefines = instance["predefines"]
        # this will read the frequency configuration
        freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        # and calc the clock cycles that is needed (using the fpga clock (speed))
        divider = self.system_setup["speed"] // freq
        instance_predefines.append(f"// PWM-Resolution: >= {self.clog2(divider) - 1}bit")
        bitwidth = int(self.plugin_setup.get("bitwidth", self.OPTIONS["bitwidth"]["default"]))
        if bitwidth < self.clog2(divider):
            print(f"  ERROR: {self.instances_name}: please incrase the bitwidth to min. {self.clog2(divider)}bit")

        # this will set the parameter in verilog
        instance_parameter["DIVIDER"] = divider
        instance_parameter["BITWIDTH"] = bitwidth
        return instances

    # optional calculation for the signals (self.SIGNALS)
    def convert_c(self, signal_name, signal_setup):
        if signal_name == "dty":
            freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
            vmin = int(signal_setup.get("userconfig", {}).get("min", self.SIGNALS["dty"]["min"]))
            vmax = int(signal_setup.get("userconfig", {}).get("max", self.SIGNALS["dty"]["max"]))
            if "dir" in self.plugin_setup.get("pins", {}):
                return f"value = value * (OSC_CLOCK / {freq}) / ({vmax});"
            return f"value = (value - {vmin}) * (OSC_CLOCK / {freq}) / ({vmax} - {vmin});"
        return ""

    def hal(self, parent):
        if "joint_data" in self.plugin_setup:
            joint_data = self.plugin_setup["joint_data"]
            axis_name = joint_data["axis"]
            joint_n = joint_data["num"]
            pid_num = joint_n
            prefix = (self.PREFIX or self.instances_name).replace(" ", "_")
            cmd_halname = f"{prefix}.dty"
            enable_halname = f"{prefix}.enable"
            scale_halname = f"{prefix}.dty-scale"
            feedback_halname = joint_data["feedback_halname"]
            feedback_scale_halname = f"{joint_data['feedback_halname']}-scale"
            parent.halg.joint_add(
                parent,
                axis_name,
                joint_n,
                "velocity",
                cmd_halname,
                feedback_halname=feedback_halname,
                scale_halname=scale_halname,
                feedback_scale_halname=feedback_scale_halname,
                enable_halname=enable_halname,
                pid_num=pid_num,
            )
