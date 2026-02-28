import os

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpio"
        self.INFO = "mcu based io's"
        self.DESCRIPTION = "mcu based io's"
        self.KEYWORDS = "input output analog adc dac pwm"
        self.NEEDS = ["mcu"]
        self.IMAGE_SHOW = False
        self.OPTIONS.update(
            {
                "node_type": {
                    "default": "",
                    "type": "select",
                    # "options": ["adc", "input", "output", "freqin"],
                    "options": ["adc", "input", "output", "dac", "rcservo", "rgbled"],
                    "description": "io type",
                    "reload": True,
                },
            },
        )

        self.node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if self.node_type == "output":
            self.IMAGES = ["relay", "ssr", "ssr2a", "led", "smdled", "spindle500w", "compressor", "vacuum", "valve", "dinrailplug", "motor"]
            self.SIGNALS = {
                "bit": {
                    "direction": "output",
                    "bool": True,
                },
            }
            self.PINDEFAULTS = {
                "bit": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["GPIO"],
                },
            }
            self.INTERFACE = {
                "bit": {
                    "size": 1,
                    "direction": "output",
                },
            }
        elif self.node_type == "input":
            self.IMAGES = ["proximity", "estop", "probe", "switch", "opto", "smdbutton", "touchprobe", "toggleswitch"]
            self.SIGNALS = {
                "bit": {
                    "direction": "input",
                    "bool": True,
                },
            }
            self.PINDEFAULTS = {
                "bit": {
                    "direction": "input",
                    "edge": "target",
                    "type": ["GPIO"],
                },
            }
            self.INTERFACE = {
                "bit": {
                    "size": 1,
                    "direction": "input",
                },
            }
        elif self.node_type == "adc":
            self.IMAGES = ["potentiometer"]
            self.NEEDS = ["mcu"]
            self.SIGNALS = {
                "value": {
                    "direction": "input",
                },
            }
            self.PINDEFAULTS = {
                "adc": {
                    "direction": "input",
                    "edge": "target",
                    "type": ["ADC"],
                },
            }
            self.INTERFACE = {
                "value": {
                    "size": 16,
                    "direction": "input",
                },
            }
        elif self.node_type == "dac":
            self.IMAGES = ["led"]
            self.NEEDS = ["mcu"]
            self.SIGNALS = {
                "value": {
                    "direction": "output",
                    "min": 0,
                    "max": 65535 // 2,
                },
            }
            self.PINDEFAULTS = {
                "dac": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["GPIO"],
                },
            }
            self.INTERFACE = {
                "value": {
                    "size": 16,
                    "direction": "output",
                },
            }
        elif self.node_type == "rcservo":
            self.IMAGES = ["rcservo"]
            self.NEEDS = ["mcu"]
            self.SIGNALS = {
                "position": {
                    "direction": "output",
                    "min": 0,
                    "max": 180,
                },
            }
            self.PINDEFAULTS = {
                "out": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["GPIO"],
                },
            }
            self.INTERFACE = {
                "position": {
                    "size": 16,
                    "direction": "output",
                },
            }
        if self.node_type == "rgbled":
            self.IMAGES = ["wled1"]
            self.OPTIONS.update(
                {
                    "leds": {
                        "default": 1,
                        "min": 1,
                        "max": 32,
                        "type": int,
                        "description": "number of leds",
                    },
                },
            )
            leds = self.plugin_setup.get("leds", self.option_default("leds"))
            self.PINDEFAULTS = {
                "data": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["GPIO"],
                },
            }
            self.SIGNALS = {
                "level": {
                    "direction": "output",
                    "min": 0,
                    "max": 255,
                },
            }
            self.INTERFACE = {
                "level": {
                    "direction": "output",
                    "size": 8,
                },
            }
            for led in range(leds):
                self.SIGNALS.update(
                    {
                        f"l{led}r": {
                            "direction": "output",
                            "bool": True,
                        },
                        f"l{led}g": {
                            "direction": "output",
                            "bool": True,
                        },
                        f"l{led}b": {
                            "direction": "output",
                            "bool": True,
                        },
                    }
                )
                self.INTERFACE.update(
                    {
                        f"l{led}r": {
                            "size": 1,
                            "direction": "output",
                        },
                        f"l{led}g": {
                            "size": 1,
                            "direction": "output",
                        },
                        f"l{led}b": {
                            "size": 1,
                            "direction": "output",
                        },
                    }
                )
        elif self.node_type == "freqin":
            self.IMAGES = ["proximity", "estop", "probe", "switch", "opto", "smdbutton", "touchprobe", "toggleswitch"]
            self.NEEDS = ["mcu"]
            self.SIGNALS = {
                "value": {
                    "direction": "input",
                },
            }
            self.PINDEFAULTS = {
                "clock": {
                    "direction": "input",
                    "edge": "target",
                    "type": ["PIO_ODD"],
                },
            }
            self.INTERFACE = {
                "value": {
                    "size": 32,
                    "direction": "input",
                },
            }

    def firmware_defines(self, variable_name):
        if self.node_type == "output" or self.node_type == "input":
            pin = self.plugin_setup["pins"]["bit"]["pin"]
            return f"#define {variable_name}_PIN_BIT {pin}"
        if self.node_type == "adc":
            pin = self.plugin_setup["pins"]["adc"]["pin"]
            return f"#define {variable_name}_PIN_ADC {pin}"
        if self.node_type == "dac":
            pin = self.plugin_setup["pins"]["dac"]["pin"]
            return f"#define {variable_name}_PIN_DAC {pin}"
        if self.node_type == "rcservo":
            pin = self.plugin_setup["pins"]["out"]["pin"]
            output = []
            output.append("#include <Servo.h>")
            output.append(f"Servo {variable_name}_SERVO;")
            return "\n".join(output)
        if self.node_type == "rgbled" and variable_name.endswith("_LEVEL"):
            pin = self.plugin_setup["pins"]["data"]["pin"]
            leds = self.plugin_setup.get("leds", self.option_default("leds"))
            name = self.instances_name.upper()
            output = []
            output.append("#include <NeoPixelConnect.h>")
            output.append(f"#define {name}_PIN_DATA {pin}")
            output.append(f"NeoPixelConnect {name}_RGB({name}_PIN_DATA, {leds});")
            return "\n".join(output)
        if self.node_type == "freqin":
            pin = self.plugin_setup["pins"]["clock"]["pin"]
            output = []
            output.append('#include "FreqCountRP2.h"')
            output.append(f"#define {variable_name}_PIN_IN {pin}")
            output.append(f"int {variable_name}_TIMER_MS = 1000;")
            return "\n".join(output)
        return ""

    def firmware_setup(self, variable_name):
        if self.node_type == "output":
            return f"    pinMode({variable_name}_PIN_BIT, OUTPUT);"
        if self.node_type == "input":
            return f"    pinMode({variable_name}_PIN_BIT, INPUT_PULLUP);"
        if self.node_type == "adc":
            return f"    pinMode({variable_name}_PIN_ADC, INPUT);"
        if self.node_type == "rcservo":
            return f"    myservo.attach({variable_name}_PIN_OUT);"
        if self.node_type == "dac":
            freq = 10000
            output = []
            output.append(f"    pinMode({variable_name}_PIN_DAC, OUTPUT);")
            output.append("    // analogWriteRange(65535);")
            output.append("    analogWriteResolution(16);")
            output.append(f"    // analogWriteFreq({freq});")
            return "\n".join(output)

        if self.node_type == "freqin":
            return f"    FreqCountRP2.beginTimer({variable_name}_PIN_IN, {variable_name}_TIMER_MS);"
        return ""

    def firmware_loop(self, pin_name, variable_name):
        if self.node_type == "output":
            inverted = 0
            for modifier in self.plugin_setup.get("pins", {}).get(pin_name, {}).get("modifier", []):
                if modifier["type"] == "invert":
                    inverted = 1 - inverted
            if inverted:
                return f"    digitalWrite({variable_name}_PIN_BIT, 1 - {variable_name});"
            return f"    digitalWrite({variable_name}_PIN_BIT, {variable_name});"
        if self.node_type == "input":
            inverted = 0
            for modifier in self.plugin_setup.get("pins", {}).get(pin_name, {}).get("modifier", []):
                if modifier["type"] == "invert":
                    inverted = 1 - inverted
            if inverted:
                return f"    {variable_name} = 1 - digitalRead({variable_name}_PIN_BIT);"
            return f"    {variable_name} = digitalRead({variable_name}_PIN_BIT);"
        if self.node_type == "adc":
            return f"    {variable_name} = analogRead({variable_name}_PIN_ADC);"
        if self.node_type == "dac":
            return f"    analogWrite({variable_name}_PIN_DAC, {variable_name});"
        if self.node_type == "rcservo":
            return f"    {variable_name}_SERVO.write({variable_name});"
        if self.node_type == "rgbled" and variable_name.endswith("_LEVEL"):
            name = self.instances_name.upper()
            leds = self.plugin_setup.get("leds", self.option_default("leds"))
            output = []
            for led in range(leds):
                output.append(f"    {name}_RGB.neoPixelSetValue({led}, VAROUT1_{name}_L{led}R * VAROUT8_{name}_LEVEL, VAROUT1_{name}_L{led}G * VAROUT8_{name}_LEVEL, VAROUT1_{name}_L{led}B * VAROUT8_{name}_LEVEL, true);")

            return "\n".join(output)
        if self.node_type == "freqin":
            output = []
            output.append("    if (FreqCountRP2.available()) {")
            output.append(f"        {variable_name} = FreqCountRP2.read();")
            output.append("    }")
            return "\n".join(output)
        return ""
