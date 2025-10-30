import os
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "stepperninja"
        self.COMPONENT = "stepgen-ninja"
        self.INFO = "stepgen-ninja"
        self.DESCRIPTION = "stepperninja"
        self.KEYWORDS = "stepgen-ninja gpio board"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = "https://github.com/atrex66/stepper-ninja"
        self.OPTIONS = {
            "board": {
                "default": "w5500-evb-pico",
                "type": "select",
                "options": [
                    "w5500-evb-pico",
                ],
                "description": "board type",
            },
            "ip": {
                "default": "192.168.0.177",
                "type": str,
                "description": "IP-Address",
            },
            "port": {
                "default": 8888,
                "type": int,
                "description": "UDP-Port",
            },
        }
        self.SIGNALS = {}

        board_pins = {
            "w5500-evb-pico": {
                "IO:GP15": {"pin": f"{self.instances_name}:gp15", "pos": [259, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP14": {"pin": f"{self.instances_name}:gp14", "pos": [281, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP13": {"pin": f"{self.instances_name}:gp13", "pos": [325, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP12": {"pin": f"{self.instances_name}:gp12", "pos": [347, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP11": {"pin": f"{self.instances_name}:gp11", "pos": [369, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP10": {"pin": f"{self.instances_name}:gp10", "pos": [391, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP9": {"pin": f"{self.instances_name}:gp9", "pos": [435, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP8": {"pin": f"{self.instances_name}:gp8", "pos": [457, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP7": {"pin": f"{self.instances_name}:gp7", "pos": [479, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP6": {"pin": f"{self.instances_name}:gp6", "pos": [501, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP5": {"pin": f"{self.instances_name}:gp5", "pos": [545, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP4": {"pin": f"{self.instances_name}:gp4", "pos": [567, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP3": {"pin": f"{self.instances_name}:gp3", "pos": [589, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP2": {"pin": f"{self.instances_name}:gp2", "pos": [611, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP1": {"pin": f"{self.instances_name}:gp1", "pos": [655, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP0": {"pin": f"{self.instances_name}:gp0", "pos": [677, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP16": {"pin": f"{self.instances_name}:gp16", "pos": [259, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP17": {"pin": f"{self.instances_name}:gp17", "pos": [281, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP18": {"pin": f"{self.instances_name}:gp18", "pos": [325, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP19": {"pin": f"{self.instances_name}:gp19", "pos": [347, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP20": {"pin": f"{self.instances_name}:gp20", "pos": [369, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP21": {"pin": f"{self.instances_name}:gp21", "pos": [391, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP22": {"pin": f"{self.instances_name}:gp22", "pos": [435, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP26": {"pin": f"{self.instances_name}:gp26", "pos": [479, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP27": {"pin": f"{self.instances_name}:gp27", "pos": [501, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP28": {"pin": f"{self.instances_name}:gp28", "pos": [545, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
            }
        }
        board = self.plugin_setup.get("board", self.option_default("board"))
        self.PINDEFAULTS = board_pins[board]

    def update_pins(self, parent):
        self.input_pins = []
        self.input_pullups = []
        self.output_pins = []
        self.stepgen_steps = []
        self.stepgen_dirs = []
        self.stepgen_dir_inverts = []

        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            name = connected_pin["name"]
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            direction = connected_pin["direction"]
            inverted = connected_pin["inverted"]
            plugin_instance = connected_pin["instance"]
            plugin_instance.PREFIX = "stepgen-ninja.0"

            if name == "step":
                self.stepgen_steps.append(pin)
            elif name == "dir":
                self.stepgen_dirs.append(pin)
                self.stepgen_dir_inverts.append("0")

            elif direction == "output":
                self.output_pins.append(pin)
                psetup["pin"] = f"stepgen-ninja.0.output.{pin.lower()}"
            elif direction == "input":
                self.input_pins.append(pin)
                self.input_pullups.append("1")
                if inverted:
                    psetup["pin"] = f"stepgen-ninja.0.input.{pin.lower()}-not"
                else:
                    psetup["pin"] = f"stepgen-ninja.0.input.{pin.lower()}"

    def component_loader(cls, instances):
        output = []
        output.append("# stepgen-ninja")
        for instance in instances:
            ip = instance.plugin_setup.get("ip", instance.option_default("ip"))
            port = instance.plugin_setup.get("port", instance.option_default("port"))
            output.append(f'loadrt stepgen-ninja ip_address="{ip}:{port}"')
            output.append("")
            output.append("addf stepgen-ninja.0.watchdog-process servo-thread")
            output.append("addf stepgen-ninja.0.process-send servo-thread")
            output.append("addf stepgen-ninja.0.process-recv servo-thread")
        return "\n".join(output)

    def extra_files(cls, parent, instances):
        output = []

        for instance in instances:
            ip = instance.plugin_setup.get("ip", instance.option_default("ip"))
            port = instance.plugin_setup.get("port", instance.option_default("port"))

            output.append(f"""
#ifndef CONFIG_H
#define CONFIG_H
#include "internals.h"

    #define DEFAULT_MAC {{0x00, 0x08, 0xDC, 0x12, 0x34, 0x56}}
    #define DEFAULT_IP {{{ip.replace(".", ", ")}}}
    #define DEFAULT_PORT {port}
    #define DEFAULT_GATEWAY {{192, 168, 0, 1}}
    #define DEFAULT_SUBNET {{255, 255, 255, 0}}
    #define DEFAULT_TIMEOUT 1000000

    #define breakout_board 0
    #define io_expanders 0

    #define stepgens {len(min(instance.stepgen_steps, instance.stepgen_dirs))}
    #define stepgen_steps {{{", ".join(instance.stepgen_steps)}}}
    #define stepgen_dirs {{{", ".join(instance.stepgen_dirs)}}}
    #define step_invert {{{", ".join(instance.stepgen_dir_inverts)}}}
    #define default_pulse_width 2000
    #define default_step_scale 1000

    #define encoders 0
    #define enc_pins {{PIN_11}} // uses 2 pins, you need to set the first pin (PIN_11 + PIN_12)
    #define enc_index_pins {{PIN_NULL}}
    #define enc_index_active_level {{high}}

    #define in_pins {{{", ".join(instance.input_pins)}}}
    #define in_pullup {{{", ".join(instance.input_pullups)}}}

    #define out_pins {{{", ".join(instance.output_pins)}}}

    #define use_pwm 0
    #define pwm_count 0
    #define pwm_pin {{PIN_19}}
    #define pwm_invert {{0}}
    #define default_pwm_frequency 10000
    #define default_pwm_maxscale 4096
    #define default_pwm_min_limit 0

    #define raspberry_pi_spi 0
    #define raspi_int_out 25
    #define raspi_inputs {{2, 3, 4, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 27}}
    #define raspi_input_pullups {{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}}
    #define raspi_outputs {{0, 1, 5, 6, 12, 13, 19, 26}}
    //#define KBMATRIX

#include "footer.h"
#include "kbmatrix.h"
#endif
""")

        target = os.path.join(parent.component_path, "ninja-config.h")
        open(target, "w").write("\n".join(output))
