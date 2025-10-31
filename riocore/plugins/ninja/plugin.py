import os
from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "ninja"
        self.COMPONENT = "ninja"
        self.INFO = "stepgen-ninja"
        self.DESCRIPTION = "ninja"
        self.KEYWORDS = "stepgen pwm ninja board pico w5500"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "ninja"
        self.URL = "https://github.com/atrex66/stepper-ninja"
        self.SHORTENER = {
            "latched": "lt",
            "ninja": "nja",
        }
        self.OPTIONS = {
            "node_type": {
                "default": "board",
                "type": "select",
                "options": [
                    "board",
                    "stepper",
                    "pwm",
                    "encoder",
                ],
                "description": "instance type",
            },
        }

        extra_options = {
            "board": {
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
            },
            "stepper": {
                # "mode": {
                #    "default": False,
                #    "type": bool,
                #    "description": "velocity mode",
                # },
            },
            "encoder": {
                "scale": {
                    "default": 80,
                    "type": int,
                    "min": 1,
                    "max": 1000000,
                    "description": "encoder scale",
                },
            },
            "pwm": {
                "frequency": {
                    "default": 10000,
                    "type": int,
                    "min": 1907,
                    "max": 1000000,
                    "description": "pwm frequency",
                },
                "scale": {
                    "default": 100,
                    "type": int,
                    "min": 1,
                    "max": 100000,
                    "description": "max pwm value",
                },
                "min_limit": {
                    "default": 0,
                    "type": int,
                    "min": 0,
                    "max": 100000,
                    "description": "min pwm value",
                },
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        self.OPTIONS.update(extra_options[node_type])
        self.SIGNALS = {}

        if node_type == "board":
            board = self.plugin_setup.get("board", self.option_default("board"))
            self.TYPE = "base"
            self.IMAGE_SHOW = True
            self.IMAGE = f"{board}.png"
            board_pins = {
                "w5500-evb-pico": {
                    "IO:LED": {"pin": f"{self.instances_name}:gp25", "pos": [640, 45], "direction": "all", "edge": "source", "type": ["GPIO"]},
                    "IO:GP15": {"pin": f"{self.instances_name}:gp15", "pos": [259, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP14": {
                        "pin": f"{self.instances_name}:gp14",
                        "pos": [281, 15],
                        "direction": "all",
                        "edge": "source",
                        "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ", "NINJAPwmPwm"],
                    },
                    "IO:GP13": {
                        "pin": f"{self.instances_name}:gp13",
                        "pos": [325, 15],
                        "direction": "all",
                        "edge": "source",
                        "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ", "NINJAPwmPwm"],
                    },
                    "IO:GP12": {"pin": f"{self.instances_name}:gp12", "pos": [347, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP11": {"pin": f"{self.instances_name}:gp11", "pos": [369, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP10": {"pin": f"{self.instances_name}:gp10", "pos": [391, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP9": {"pin": f"{self.instances_name}:gp9", "pos": [435, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderB"]},
                    "IO:GP8": {"pin": f"{self.instances_name}:gp8", "pos": [457, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderA"]},
                    "IO:GP7": {"pin": f"{self.instances_name}:gp7", "pos": [479, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP6": {"pin": f"{self.instances_name}:gp6", "pos": [501, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP5": {"pin": f"{self.instances_name}:gp5", "pos": [545, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP4": {"pin": f"{self.instances_name}:gp4", "pos": [567, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP3": {"pin": f"{self.instances_name}:gp3", "pos": [589, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP2": {"pin": f"{self.instances_name}:gp2", "pos": [611, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP1": {"pin": f"{self.instances_name}:gp1", "pos": [655, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
                    "IO:GP0": {"pin": f"{self.instances_name}:gp0", "pos": [677, 15], "direction": "all", "edge": "source", "type": ["GPIO", "NINJAStepGenStep", "NINJAStepGenDir", "NINJAEncoderZ"]},
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
            self.PINDEFAULTS = board_pins[board]
            self.ninja_num = 0
        elif node_type == "stepper":
            self.TYPE = "joint"
            mode = self.plugin_setup.get("mode", self.option_default("mode"))
            if mode:
                self.JOINT_TYPE = "velocity"
            else:
                self.JOINT_TYPE = "position"
            self.IMAGE_SHOW = True
            self.IMAGES = ["stepper", "servo42"]
            self.SIGNALS = {
                "velocity": {
                    "direction": "output",
                    "absolute": False,
                    "description": "set position",
                },
                "position": {
                    "direction": "input",
                    "unit": "steps",
                    "absolute": False,
                    "description": "position feedback",
                },
                "position-scale": {
                    "direction": "output",
                    "absolute": False,
                    "description": "steps / unit",
                },
            }
            self.PINDEFAULTS = {
                "step": {"direction": "output", "edge": "target", "type": "NINJAStepGenStep"},
                "dir": {"direction": "output", "edge": "target", "type": "NINJAStepGenDir"},
            }
        elif node_type == "encoder":
            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGE_SHOW = False
            self.IMAGES = ["generic", "encoder"]
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            self.SIGNALS = {
                "raw-count": {
                    "direction": "input",
                    "s32": True,
                },
                "position": {
                    "direction": "input",
                },
                "velocity": {
                    "direction": "input",
                },
                "count-latched": {
                    "direction": "input",
                    "s32": True,
                },
                "position-latched": {
                    "direction": "input",
                },
            }
            self.PINDEFAULTS = {
                "a": {"direction": "output", "edge": "target", "type": "NINJAEncoderA"},
                "b": {"direction": "output", "edge": "target", "type": "NINJAEncoderB"},
                "z": {"direction": "output", "edge": "target", "type": "NINJAEncoderZ", "optional": True},
            }

        elif node_type == "pwm":
            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGES = ["spindle500w", "laser", "led"]
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            min_limit = self.plugin_setup.get("min_limit", self.option_default("min_limit"))
            self.SIGNALS = {
                "duty": {
                    "direction": "output",
                    "min": min_limit,
                    "max": scale,
                    "u32": True,
                },
                "enable": {
                    "direction": "output",
                    "bool": True,
                },
            }
            self.PINDEFAULTS = {
                "pwm": {"direction": "output", "edge": "target", "type": "NINJAPwmPwm"},
            }

    def update_prefixes(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                stepgen_num = 0
                pwmgen_num = 0
                encoder_num = 0
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    name = connected_pin["name"]
                    plugin_instance = connected_pin["instance"]
                    if name == "step":
                        plugin_instance.PREFIX = f"stepgen-ninja.{instance.ninja_num}.stepgen.{stepgen_num}"
                        stepgen_num += 1
                    elif name == "pwm":
                        plugin_instance.PREFIX = f"stepgen-ninja.{instance.ninja_num}.pwm.{pwmgen_num}"
                        pwmgen_num += 1
                    elif name == "a":
                        plugin_instance.PREFIX = f"stepgen-ninja.{instance.ninja_num}.encoder.{encoder_num}"
                        encoder_num += 1

    def update_pins(self, parent):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "board":
            self.input_pins = []
            self.input_pullups = []
            self.output_pins = []
            self.pwm_pins = []
            self.pwm_inverts = []
            self.encoder_a_pins = []
            self.encoder_b_pins = []
            self.encoder_z_pins = []
            self.encoder_z_inverts = []
            self.stepgen_steps = []
            self.stepgen_dirs = []
            self.stepgen_dir_inverts = []
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
                name = connected_pin["name"]
                psetup = connected_pin["setup"]
                pin = connected_pin["pin"]
                direction = connected_pin["direction"]
                inverted = connected_pin["inverted"]
                upin = f"GP{int(pin[2:]):02d}"
                if name == "step":
                    self.stepgen_steps.append(upin)
                elif name == "dir":
                    self.stepgen_dirs.append(upin)
                    self.stepgen_dir_inverts.append("0")
                elif name == "pwm":
                    self.pwm_pins.append(upin)
                    self.pwm_inverts.append("0")
                elif name == "a":
                    self.encoder_a_pins.append(upin)
                elif name == "b":
                    self.encoder_b_pins.append(upin)
                elif name == "z":
                    if inverted:
                        self.encoder_z_pins.append("low")
                    else:
                        self.encoder_z_pins.append("high")
                elif direction == "output":
                    self.output_pins.append(upin)
                    psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.output.{pin.lower()}"
                elif direction == "input":
                    self.input_pins.append(upin)
                    self.input_pullups.append("1")
                    if inverted:
                        psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.input.{pin.lower()}-not"
                    else:
                        psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.input.{pin.lower()}"

    def component_loader(cls, instances):
        output = []
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                output.append("# stepgen-ninja")
                ip = instance.plugin_setup.get("ip", instance.option_default("ip"))
                port = instance.plugin_setup.get("port", instance.option_default("port"))
                output.append(f'loadrt stepgen-ninja ip_address="{ip}:{port}"')
                output.append("")
                output.append(f"addf stepgen-ninja.{instance.ninja_num}.watchdog-process servo-thread")
                output.append(f"addf stepgen-ninja.{instance.ninja_num}.process-send servo-thread")
                output.append(f"addf stepgen-ninja.{instance.ninja_num}.process-recv servo-thread")
        return "\n".join(output)

    def hal(self, parent):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "pwm":
            frequency = self.plugin_setup.get("frequency", self.option_default("frequency"))
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            min_limit = self.plugin_setup.get("min_limit", self.option_default("min_limit"))
            parent.halg.setp_add(f"{self.PREFIX}.frequency", frequency)
            parent.halg.setp_add(f"{self.PREFIX}.max-scale", scale)
            parent.halg.setp_add(f"{self.PREFIX}.min-limit", min_limit)
        elif node_type == "encoder":
            scale = self.plugin_setup.get("scale", self.option_default("scale"))
            parent.halg.setp_add(f"{self.PREFIX}.scale", scale)
        elif node_type == "stepper":
            mode = self.plugin_setup.get("mode", self.option_default("mode")) or False
            parent.halg.setp_add(f"{self.PREFIX}.mode", mode)
            if "joint_data" in self.plugin_setup:
                joint_data = self.plugin_setup["joint_data"]
                axis_name = joint_data["axis"]
                joint_n = joint_data["num"]
                pid_num = joint_n
                if self.JOINT_TYPE == "velocity":
                    cmd_halname = f"{self.PREFIX}.command"
                    feedback_halname = f"{self.PREFIX}.feedback"
                    enable_halname = f"{self.PREFIX}.enable"
                    scale_halname = f"{self.PREFIX}.step-scale"
                    parent.halg.joint_add(
                        parent, axis_name, joint_n, "velocity", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, pid_num=pid_num
                    )
                else:
                    cmd_halname = f"{self.PREFIX}.command"
                    feedback_halname = f"{self.PREFIX}.command"
                    enable_halname = f"{self.PREFIX}.enable"
                    scale_halname = f"{self.PREFIX}.step-scale"
                    parent.halg.joint_add(parent, axis_name, joint_n, "position", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname)

    def extra_files(cls, parent, instances):
        output = []
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
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

    #define encoders {len(instance.encoder_a_pins)}
    #define enc_pins {{{", ".join(instance.encoder_a_pins)}}}
    // #define enc_pins_b {{{", ".join(instance.encoder_b_pins)}}}
    #define enc_index_pins {{{", ".join(instance.encoder_z_pins)}}}
    #define enc_index_active_level {{{", ".join(instance.encoder_z_inverts)}}}

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

                # create firmware stuff
                firmware_path = os.path.join(parent.project.config["output_path"], "Firmware")
                os.makedirs(firmware_path, exist_ok=True)
                print(f"{instance.NAME}: create firmware structure: {firmware_path}")

                target = os.path.join(firmware_path, "ninja-config.h")
                open(target, "w").write("\n".join(output))

                makefile = f"""

TOOLCHAIN_PATH := {riocore_path}/toolchains
PICO_SDK_PATH := $(TOOLCHAIN_PATH)/pico-sdk
NINJA_SRC_PATH := $(TOOLCHAIN_PATH)/stepper-ninja

all: clean prepare build install

clean:
	rm -rf build

$(PICO_SDK_PATH):
	mkdir -p $(TOOLCHAIN_PATH)
	cd $(TOOLCHAIN_PATH) && git clone https://github.com/raspberrypi/pico-sdk
	cd $(TOOLCHAIN_PATH)/pico-sdk && git submodule update --init

$(NINJA_SRC_PATH):
	mkdir -p $(TOOLCHAIN_PATH)
	cd $(TOOLCHAIN_PATH) && git clone https://github.com/atrex66/stepper-ninja
	sed -i "s|.*PICO_SDK_PATH.*||g" $(NINJA_SRC_PATH)/firmware/CMakeLists.txt

prepare: $(NINJA_SRC_PATH) $(PICO_SDK_PATH) ninja-config.h
	cp -a ninja-config.h $(NINJA_SRC_PATH)/firmware/inc/config.h
	mkdir -p build

build: prepare ninja-config.h
	rm -rf build/stepper-ninja-*.uf2
	cd build && PICO_SDK_PATH=$(PICO_SDK_PATH) cmake -DBOARD=pico -DWIZCHIP_TYPE=W5500 $(NINJA_SRC_PATH)/firmware
	cd build && make clean
	cd build && make all
	ls build/stepper-ninja-*.uf2

/dev/disk/by-label/RPI-RP2:
	@echo "##### set rpi to bootmode #####"
	@exit 1

halcompile:
	sudo halcompile --install $(NINJA_SRC_PATH)/hal-driver/stepgen-ninja.c

install: halcompile /dev/disk/by-label/RPI-RP2
	mkdir -p fs_pico
	sudo umount fs_pico || true
	sudo mount /dev/disk/by-label/RPI-RP2 fs_pico
	sudo cp build/stepper-ninja-*.uf2 fs_pico || true
	sudo umount fs_pico
	rmdir fs_pico
"""

                target = os.path.join(firmware_path, "Makefile")
                open(target, "w").write(makefile)
