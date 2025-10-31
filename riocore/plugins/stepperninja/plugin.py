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
            "mac": {
                "default": "00:08:DC:12:34:56",
                "type": str,
                "description": "MAC-Address",
            },
            "ip": {
                "default": "192.168.0.177",
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
                "default": 8888,
                "type": int,
                "description": "UDP-Port",
            },
        }
        self.SIGNALS = {}

        board_pins = {
            "w5500-evb-pico": {
                # "IO:LED": {"pin": f"{self.instances_name}:gp25", "pos": [259, 15], "direction": "all", "edge": "source", "type": ["GPIO"]},
                "IO:GP15": {"pin": f"{self.instances_name}:gp15", "pos": [259, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP14": {"pin": f"{self.instances_name}:gp14", "pos": [281, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAPwmPwm"]},
                "IO:GP13": {"pin": f"{self.instances_name}:gp13", "pos": [325, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAPwmPwm"]},
                "IO:GP12": {"pin": f"{self.instances_name}:gp12", "pos": [347, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP11": {"pin": f"{self.instances_name}:gp11", "pos": [369, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP10": {"pin": f"{self.instances_name}:gp10", "pos": [391, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP9": {"pin": f"{self.instances_name}:gp9", "pos": [435, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP8": {"pin": f"{self.instances_name}:gp8", "pos": [457, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderA"]},
                "IO:GP7": {"pin": f"{self.instances_name}:gp7", "pos": [479, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderB"]},
                "IO:GP6": {"pin": f"{self.instances_name}:gp6", "pos": [501, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP5": {"pin": f"{self.instances_name}:gp5", "pos": [545, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP4": {"pin": f"{self.instances_name}:gp4", "pos": [567, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP3": {"pin": f"{self.instances_name}:gp3", "pos": [589, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP2": {"pin": f"{self.instances_name}:gp2", "pos": [611, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP1": {"pin": f"{self.instances_name}:gp1", "pos": [655, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP0": {"pin": f"{self.instances_name}:gp0", "pos": [677, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                # W5500 - SPI pins
                # "IO:GP16": {"pin": f"{self.instances_name}:gp16", "pos": [259, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                # "IO:GP17": {"pin": f"{self.instances_name}:gp17", "pos": [281, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                # "IO:GP18": {"pin": f"{self.instances_name}:gp18", "pos": [325, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                # "IO:GP19": {"pin": f"{self.instances_name}:gp19", "pos": [347, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                # "IO:GP20": {"pin": f"{self.instances_name}:gp20", "pos": [369, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                # "IO:GP21": {"pin": f"{self.instances_name}:gp21", "pos": [391, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP22": {"pin": f"{self.instances_name}:gp22", "pos": [435, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP26": {"pin": f"{self.instances_name}:gp26", "pos": [479, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP27": {"pin": f"{self.instances_name}:gp27", "pos": [501, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
                "IO:GP28": {"pin": f"{self.instances_name}:gp28", "pos": [545, 166], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir"]},
            }
        }
        board = self.plugin_setup.get("board", self.option_default("board"))
        self.PINDEFAULTS = board_pins[board]
        self.ninja_num = 0

    def update_prefixes(cls, parent, instances):
        for instance in instances:
            stepgen_num = 0
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                name = connected_pin["name"]
                plugin_instance = connected_pin["instance"]
                if name == "step":
                    plugin_instance.PREFIX = f"stepgen-ninja.{instance.ninja_num}.stepgen.{stepgen_num}"
                    stepgen_num += 1
                elif name == "pwm":
                    plugin_instance.PREFIX = f"stepgen-ninja.{instance.ninja_num}.pwm"

    def update_pins(self, parent):
        self.input_pins = []
        self.input_pullups = []
        self.output_pins = []
        self.pwm_pins = []
        self.pwm_inverts = []
        self.stepgen_steps = []
        self.stepgen_dirs = []
        self.stepgen_dir_inverts = []

        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            name = connected_pin["name"]
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            direction = connected_pin["direction"]
            inverted = connected_pin["inverted"]

            if name == "step":
                self.stepgen_steps.append(pin)
            elif name == "dir":
                self.stepgen_dirs.append(pin)
                self.stepgen_dir_inverts.append("0")
            elif name == "pwm":
                self.pwm_pins.append(pin)
                self.pwm_inverts.append("0")

            elif direction == "output":
                self.output_pins.append(pin)
                psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.output.{pin.lower()}"
            elif direction == "input":
                self.input_pins.append(pin)
                self.input_pullups.append("1")
                if inverted:
                    psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.input.{pin.lower()}-not"
                else:
                    psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.input.{pin.lower()}"

    def component_loader(cls, instances):
        output = []
        output.append("# stepgen-ninja")
        for instance in instances:
            ip = instance.plugin_setup.get("ip", instance.option_default("ip"))
            port = instance.plugin_setup.get("port", instance.option_default("port"))
            output.append(f'loadrt stepgen-ninja ip_address="{ip}:{port}"')
            output.append("")
            output.append(f"addf stepgen-ninja.{instance.ninja_num}.watchdog-process servo-thread")
            output.append(f"addf stepgen-ninja.{instance.ninja_num}.process-send servo-thread")
            output.append(f"addf stepgen-ninja.{instance.ninja_num}.process-recv servo-thread")
        return "\n".join(output)

    def extra_files(cls, parent, instances):
        output = []

        for instance in instances:
            mac = instance.plugin_setup.get("mac", instance.option_default("mac"))
            ip = instance.plugin_setup.get("ip", instance.option_default("ip"))
            mask = instance.plugin_setup.get("mask", instance.option_default("mask"))
            gw = instance.plugin_setup.get("gw", instance.option_default("gw"))
            port = instance.plugin_setup.get("port", instance.option_default("port"))

            output.append(f"""
#ifndef CONFIG_H
#define CONFIG_H
#include "internals.h"

    #define DEFAULT_MAC {{{mac.replace(":", ", 0x")}}}
    #define DEFAULT_IP {{{ip.replace(".", ", ")}}}
    #define DEFAULT_PORT {port}
    #define DEFAULT_GATEWAY {{{gw.replace(".", ", ")}}}
    #define DEFAULT_SUBNET {{{mask.replace(".", ", ")}}}
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
    #define enc_pins {{PIN_11}}
    #define enc_index_pins {{PIN_NULL}}
    #define enc_index_active_level {{high}}

    #define in_pins {{{", ".join(instance.input_pins)}}}
    #define in_pullup {{{", ".join(instance.input_pullups)}}}

    #define out_pins {{{", ".join(instance.output_pins)}}}

    #define use_pwm {1 if instance.pwm_pins else 0}
    #define pwm_count {len(instance.pwm_pins)}
    #define pwm_pin {{{", ".join(instance.pwm_pins)}}}
    #define pwm_invert {{{", ".join(instance.pwm_inverts)}}}
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
