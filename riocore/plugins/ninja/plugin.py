import json
import copy
import os
from riocore.plugins import PluginBase

import riocore

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
        self.SIGNALS = {}

        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "board":
            self.OPTIONS.update(
                {
                    "board": {
                        "default": "w5500-evb-pico",
                        "type": "select",
                        "options": [
                            "w5500-evb-pico",
                            "w5500-evb-pico-parport",
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
            )
            board = self.plugin_setup.get("board", self.option_default("board"))
            self.TYPE = "base"
            self.BUILDER = ["build", "install"]
            self.IMAGE_SHOW = True
            self.IMAGE = f"{board}.png"
            self.PINDEFAULTS = {}
            pin_file = os.path.join(os.path.dirname(__file__), f"{board}.json")
            if os.path.exists(pin_file):
                pins = json.loads(open(pin_file, "r").read())
                for pin_name, pin_data in pins.items():
                    pin_data["pin"] = f"{self.instances_name}:{pin_data['pin']}"
                    self.PINDEFAULTS[pin_name] = pin_data
            else:
                riocore.log(f"ERROR: ninja: pinfile not found: {pin_file}")

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
            self.OPTIONS.update(
                {
                    "scale": {
                        "default": 80,
                        "type": int,
                        "min": 1,
                        "max": 1000000,
                        "description": "encoder scale",
                    },
                }
            )
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
            self.OPTIONS.update(
                {
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
                }
            )
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
                gpin = pin.replace("GP0", "GP").lower()
                if name == "step":
                    self.stepgen_steps.append(pin)
                elif name == "dir":
                    self.stepgen_dirs.append(pin)
                    self.stepgen_dir_inverts.append("0")
                elif name == "pwm":
                    self.pwm_pins.append(pin)
                    self.pwm_inverts.append("0")
                elif name == "a":
                    self.encoder_a_pins.append(pin)
                elif name == "b":
                    self.encoder_b_pins.append(pin)
                elif name == "z":
                    if inverted:
                        self.encoder_z_pins.append("low")
                    else:
                        self.encoder_z_pins.append("high")
                elif direction == "output":
                    self.output_pins.append(pin)
                    psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.output.{gpin}"
                elif direction == "input":
                    self.input_pins.append(pin)
                    self.input_pullups.append("1")
                    if inverted:
                        psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.input.{gpin}-not"
                    else:
                        psetup["pin"] = f"stepgen-ninja.{self.ninja_num}.input.{gpin}"

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

    def builder(self, config, command):
        project = riocore.Project(copy.deepcopy(config))
        firmware_path = os.path.join(project.config["output_path"], "Firmware", self.instances_name)
        cmd = f"cd {firmware_path} && make {command}"
        return cmd

    def extra_files(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "board":
                mac = instance.plugin_setup.get("mac", instance.option_default("mac"))
                ip = instance.plugin_setup.get("ip", instance.option_default("ip"))
                mask = instance.plugin_setup.get("mask", instance.option_default("mask"))
                gw = instance.plugin_setup.get("gw", instance.option_default("gw"))
                port = instance.plugin_setup.get("port", instance.option_default("port"))

                output = []
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
                firmware_path = os.path.join(parent.project.config["output_path"], "Firmware", instance.instances_name)
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
