import os

from riocore import PluginImages
from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mcuio"
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
                    "options": [
                        "adc",
                        "input",
                        "output",
                        "dac",
                        "rcservo",
                        "rgbled",
                        "encoder",
                        "mcp4725",
                        "max7219",
                    ],
                    "description": "io type",
                    "reload": True,
                },
            },
        )

        self.node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        self.KICAD_FOLDER = os.path.join("kicad", self.node_type)
        if self.node_type == "output":
            self.IMAGES = PluginImages.bitout
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
                    "type": ["MCUIO"],
                },
            }
            self.INTERFACE = {
                "bit": {
                    "size": 1,
                    "direction": "output",
                },
            }
        elif self.node_type == "input":
            self.IMAGES = PluginImages.bitin
            self.OPTIONS.update(
                {
                    "longpress": {
                        "default": "OFF",
                        "type": "select",
                        "options": ["OFF", "ON"],
                        "description": "allow longpress events (for buttons)",
                    },
                },
            )
            self.SIGNALS = {
                "bit": {
                    "direction": "input",
                    "bool": True,
                },
            }
            longpress = self.plugin_setup.get("longpress", self.option_default("longpress"))
            if longpress == "ON":
                self.SIGNALS.update(
                    {
                        "bit_short": {
                            "direction": "input",
                            "filter": "longpress",
                            "bool": True,
                        },
                        "bit_long1": {
                            "direction": "input",
                            "no_convert": True,
                            "bool": True,
                        },
                        "bit_long2": {
                            "direction": "input",
                            "no_convert": True,
                            "bool": True,
                        },
                    }
                )

            self.PINDEFAULTS = {
                "bit": {
                    "direction": "input",
                    "edge": "target",
                    "type": ["MCUIO"],
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
        elif self.node_type == "mcp4725":
            self.IMAGES = ["led"]
            self.NEEDS = ["mcu"]
            self.SIGNALS = {
                "value": {
                    "direction": "output",
                    "min": 0,
                    "max": 4095,
                },
            }
            self.PINDEFAULTS = {
                "sda": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["MCUIO"],
                },
                "scl": {
                    "direction": "all",
                    "edge": "target",
                    "type": ["MCUIO"],
                },
            }
            self.INTERFACE = {
                "value": {
                    "size": 16,
                    "direction": "output",
                },
            }

        elif self.node_type == "max7219":
            self.IMAGES = ["max7219x1.png", "max7219x2.png", "max7219x3.png", "max7219x4.png"]
            self.NEEDS = ["mcu"]
            self.PINDEFAULTS = {
                "mosi": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["MCUIO"],
                    "pos": (32, 35),
                },
                "sclk": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["MCUIO"],
                    "pos": (32, 46),
                },
                "sel": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["MCUIO"],
                    "pos": (32, 57),
                },
            }
            self.OPTIONS.update(
                {
                    "displays": {
                        "default": 1,
                        "min": 1,
                        "max": 6,
                        "type": int,
                        "description": "number of displays",
                    },
                    "dotpos": {
                        "default": 2,
                        "min": 0,
                        "max": 8,
                        "type": int,
                        "description": "dot position",
                    },
                },
            )
            displays = self.plugin_setup.get("displays", self.option_default("displays"))
            self.SIGNALS = {}
            self.INTERFACE = {}
            for display in range(displays):
                self.SIGNALS[f"value{display}"] = {
                    "direction": "output",
                    "min": -9999999,
                    "max": 9999999,
                }
                self.INTERFACE[f"value{display}"] = {
                    "size": 32,
                    "direction": "output",
                }

        elif self.node_type == "dac":
            self.IMAGES = PluginImages.pwmout
            self.NEEDS = ["mcu"]
            self.SIGNALS = {
                "value": {
                    "direction": "output",
                    "min": 0,
                    "max": 4095,
                },
            }
            self.PINDEFAULTS = {
                "dac": {
                    "direction": "output",
                    "edge": "target",
                    "type": ["MCUIO"],
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
                    "type": ["MCUIO"],
                },
            }
            self.INTERFACE = {
                "position": {
                    "size": 16,
                    "direction": "output",
                },
            }
        elif self.node_type == "encoder":
            self.IMAGES = ["encoder", "encoder_optical"]
            self.SIGNALS = {
                "position": {
                    "direction": "input",
                    "description": "position feedback in steps",
                },
            }
            self.PINDEFAULTS = {
                "a": {
                    "direction": "input",
                    "type": ["MCUIO"],
                },
                "b": {
                    "direction": "input",
                    "type": ["MCUIO"],
                },
            }
            self.INTERFACE = {
                "position": {
                    "size": 32,
                    "direction": "input",
                },
            }
        elif self.node_type == "rgbled":
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
                    "type": ["MCUIO"],
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
            self.IMAGES = PluginImages.biin
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

    @classmethod
    def firmware_type_defines(cls, instances):
        encoders = 0
        for instance in instances:
            if instance.node_type != "encoder":
                continue
            if "mcu" in instance.MASTER_PROVIDES:
                encoders += 1
        if not encoders:
            return ""
        return f"""
#include <ESPRotary.h>
#define NUM_ENCODERS {encoders}

ESPRotary encoder[NUM_ENCODERS];

/*
hw_timer_t *timer = NULL;

void IRAM_ATTR handleLoop() {{
    for (int i = 0; i < NUM_ENCODERS; i++) {{
        encoder[i].loop();
    }}
}}
*/

"""

    def firmware_defines(self, variable_name):
        name = self.instances_name.upper()
        if self.node_type == "output" or self.node_type == "input":
            pin = self.plugin_setup["pins"]["bit"]["pin"]
            return f"#define {name}_PIN_BIT {pin}"
        if self.node_type == "adc":
            pin = self.plugin_setup["pins"]["adc"]["pin"]
            return f"#define {name}_PIN_ADC {pin}"
        if self.node_type == "encoder":
            pin_a = self.plugin_setup["pins"]["a"]["pin"]
            pin_b = self.plugin_setup["pins"]["b"]["pin"]
            return f"#define {name}_PIN_A {pin_a}\n#define {name}_PIN_B {pin_b}"
        if self.node_type == "dac":
            pin = self.plugin_setup["pins"]["dac"]["pin"]
            return f"#define {name}_PIN_DAC {pin}"
        if self.node_type == "mcp4725":
            sda = self.plugin_setup["pins"]["sda"]["pin"]
            scl = self.plugin_setup["pins"]["scl"]["pin"]
            output = []
            output.append("#include <Wire.h>")
            output.append("#include <MCP4725.h>")
            output.append(f"#define {name}_PIN_SDA {sda}")
            output.append(f"#define {name}_PIN_SCL {scl}")
            output.append(f"MbedI2C Wire1({name}_PIN_SDA, {name}_PIN_SCL);")
            output.append("MCP4725 MCP(0x61, &Wire1);")
            return "\n".join(output)
        if self.node_type == "max7219" and variable_name.endswith("0"):
            displays = self.plugin_setup.get("displays", self.option_default("displays"))
            dotpos = self.plugin_setup.get("dotpos", self.option_default("dotpos"))
            mosi = self.plugin_setup["pins"]["mosi"]["pin"]
            sclk = self.plugin_setup["pins"]["sclk"]["pin"]
            sel = self.plugin_setup["pins"]["sel"]["pin"]
            output = []
            output.append(f"#define MAX7219_DISPLAYS {displays}")
            output.append(f"#define MAX7219_DOT_POS {dotpos}")
            output.append(f"#define MAX7219_PIN_MOSI {mosi}")
            output.append(f"#define MAX7219_PIN_SCLK {sclk}")
            output.append(f"#define MAX7219_PIN_SEL {sel}")
            output.append(f"int32_t MAX7219_VALUES[{displays}] = {{{', '.join(['0'] * displays)}}};")

            output.append("""
uint8_t NUM7SEG[] = {
    0b1111110,
    0b0110000,
    0b1101101,
    0b1111001,
    0b0110011,
    0b1011011,
    0b1011111,
    0b1110000,
    0b1111111,
    0b1111011,
    0b0000000,
    0b0000001,
};

static void max7219_write(uint8_t address, uint8_t data) {
    shiftOut(MAX7219_PIN_MOSI, MAX7219_PIN_SCLK, MSBFIRST, address);
    shiftOut(MAX7219_PIN_MOSI, MAX7219_PIN_SCLK, MSBFIRST, data);
}

static void max7219_init(void) {
    int d = 0;
    pinMode(MAX7219_PIN_SEL, OUTPUT);
    digitalWrite(MAX7219_PIN_SEL, HIGH);
    pinMode(MAX7219_PIN_SCLK, OUTPUT);
    digitalWrite(MAX7219_PIN_SCLK, LOW);
    pinMode(MAX7219_PIN_MOSI, OUTPUT);
    digitalWrite(MAX7219_PIN_MOSI, LOW);

    // display test off
    digitalWrite(MAX7219_PIN_SEL, LOW);
    for (d = 0; d < MAX7219_DISPLAYS; d++) {
        max7219_write(0x0F, 0x00);
    }
    digitalWrite(MAX7219_PIN_SEL, HIGH);
    // shutdown register: normal operation
    digitalWrite(MAX7219_PIN_SEL, LOW);
    for (d = 0; d < MAX7219_DISPLAYS; d++) {
        max7219_write(0x0C, 0x01);
    }
    digitalWrite(MAX7219_PIN_SEL, HIGH);
    // decode mode off
    digitalWrite(MAX7219_PIN_SEL, LOW);
    for (d = 0; d < MAX7219_DISPLAYS; d++) {
        max7219_write(0x09, 0x00);
    }
    digitalWrite(MAX7219_PIN_SEL, HIGH);
    // scan limit = 8 digits
    digitalWrite(MAX7219_PIN_SEL, LOW);
    for (d = 0; d < MAX7219_DISPLAYS; d++) {
        max7219_write(0x0B, 0x07);
    }
    digitalWrite(MAX7219_PIN_SEL, HIGH);
    // intensity
    digitalWrite(MAX7219_PIN_SEL, LOW);
    for (d = 0; d < MAX7219_DISPLAYS; d++) {
        max7219_write(0x0A, 0x07);
    }
    digitalWrite(MAX7219_PIN_SEL, HIGH);
    // clear all digits
    for (int i = 0; i < 8; i++) {
        digitalWrite(MAX7219_PIN_SEL, LOW);
        for (d = 0; d < MAX7219_DISPLAYS; d++) {
            max7219_write(i, 0x00);
        }
        digitalWrite(MAX7219_PIN_SEL, LOW);
    }
}

static void max7219_display(int32_t *values) {
    uint8_t d = 0;
    uint8_t neg[MAX7219_DISPLAYS];
    uint32_t tmp[MAX7219_DISPLAYS];
    for (d = 0; d < MAX7219_DISPLAYS; d++) {
        if (values[d] < 0) {
            neg[d] = 1;
        } else {
            neg[d] = 0;
        }
        tmp[d] = abs(values[d]);
    }
    for (int i = 0; i < 8; i++) {
        digitalWrite(MAX7219_PIN_SEL, HIGH);
        for (d = 0; d < MAX7219_DISPLAYS; d++) {
            uint8_t dn = MAX7219_DISPLAYS - d - 1;
            uint8_t digit = 0;
            if (tmp[dn] > 0 || i == 0) {
                digit = NUM7SEG[tmp[dn] % 10];
            } else if (i == 7) {
                if (neg[dn] == 1) {
                    digit = NUM7SEG[11];
                } else {
                    digit = NUM7SEG[10];
                }
            } else {
                digit = NUM7SEG[0];
                // digit = NUM7SEG[10];
            }
            if (i == MAX7219_DOT_POS) {
                digit |= (1<<7);
            }
            max7219_write(i + 1, digit);
            tmp[dn] = tmp[dn] / 10;
        }
        digitalWrite(MAX7219_PIN_SEL, LOW);
    }
}
            """)
            return "\n".join(output)
        if self.node_type == "rcservo":
            pin = self.plugin_setup["pins"]["out"]["pin"]
            output = []
            output.append("#include <Servo.h>")
            output.append(f"#define {name}_PIN_OUT {pin}")
            output.append(f"Servo {name}_SERVO;")
            return "\n".join(output)
        if self.node_type == "rgbled" and variable_name.endswith("_LEVEL"):
            pin = self.plugin_setup["pins"]["data"]["pin"]
            leds = self.plugin_setup.get("leds", self.option_default("leds"))
            output = []
            output.append("#include <NeoPixelConnect.h>")
            output.append(f"#define {name}_PIN_DATA {pin}")
            output.append(f"NeoPixelConnect {name}_RGB({name}_PIN_DATA, {leds});")
            return "\n".join(output)
        if self.node_type == "freqin":
            pin = self.plugin_setup["pins"]["clock"]["pin"]
            output = []
            output.append('#include "FreqCountRP2.h"')
            output.append(f"#define {name}_PIN_IN {pin}")
            output.append(f"int {variable_name}_TIMER_MS = 1000;")
            return "\n".join(output)
        return ""

    def firmware_setup(self, variable_name):
        name = self.instances_name.upper()
        if self.node_type == "output":
            return f"    pinMode({name}_PIN_BIT, OUTPUT);"
        if self.node_type == "input":
            return f"    pinMode({name}_PIN_BIT, INPUT_PULLUP);"
        if self.node_type == "adc":
            return f"    pinMode({name}_PIN_ADC, INPUT);"
        if self.node_type == "rcservo":
            return f"    {name}_SERVO.attach({name}_PIN_OUT);"
        if self.node_type == "max7219" and variable_name.endswith("0"):
            output = []
            output.append("    max7219_init();")
            return "\n".join(output)
        if self.node_type == "mcp4725":
            output = []
            output.append("    Wire1.begin();")
            output.append("    MCP.setValue(10);")
            output.append("    MCP.begin();")
            return "\n".join(output)
        if self.node_type == "dac":
            freq = 10000
            output = []
            output.append(f"    pinMode({name}_PIN_DAC, OUTPUT);")
            output.append("    analogWriteResolution(12);")
            output.append(f"    // analogWriteFreq({freq});")
            return "\n".join(output)
        if self.node_type == "freqin":
            return f"    FreqCountRP2.beginTimer({name}_PIN_IN, {variable_name}_TIMER_MS);"
        return ""

    def firmware_loop(self, pin_name, variable_name):
        name = self.instances_name.upper()
        if self.node_type == "output":
            inverted = 0
            for modifier in self.plugin_setup.get("pins", {}).get(pin_name, {}).get("modifier", []):
                if modifier["type"] == "invert":
                    inverted = 1 - inverted
            if inverted:
                return f"    digitalWrite({name}_PIN_BIT, 1 - {variable_name});"
            return f"    digitalWrite({name}_PIN_BIT, {variable_name});"
        if self.node_type == "input":
            inverted = 0
            for modifier in self.plugin_setup.get("pins", {}).get(pin_name, {}).get("modifier", []):
                if modifier["type"] == "invert":
                    inverted = 1 - inverted
            if inverted:
                return f"    {variable_name} = 1 - digitalRead({name}_PIN_BIT);"
            return f"    {variable_name} = digitalRead({name}_PIN_BIT);"
        if self.node_type == "adc":
            return f"    {variable_name} = analogRead({name}_PIN_ADC);"
        if self.node_type == "dac":
            inverted = 0
            for modifier in self.plugin_setup.get("pins", {}).get("dac", {}).get("modifier", []):
                if modifier["type"] == "invert":
                    inverted = 1 - inverted
            if inverted:
                return f"    analogWrite({name}_PIN_DAC, 4095 - {variable_name});"
            return f"    analogWrite({name}_PIN_DAC, {variable_name});"
        if self.node_type == "max7219" and variable_name.endswith("0"):
            name = self.instances_name.upper()
            displays = self.plugin_setup.get("displays", self.option_default("displays"))
            output = []
            for display in range(displays):
                output.append(f"    MAX7219_VALUES[{display}] = VAROUT32_{name}_VALUE{display};")
            output.append("    max7219_display(MAX7219_VALUES);")
            return "\n".join(output)
        if self.node_type == "mcp4725":
            return f"    MCP.setValue({variable_name});"
        if self.node_type == "rcservo":
            return f"    {name}_SERVO.write({variable_name});"
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

    def firmware_libs(self):
        if self.node_type == "rcservo":
            return ["https://github.com/arduino-libraries/Servo"]
        if self.node_type == "encoder":
            return ["https://github.com/LennartHennigs/ESPRotary"]
        if self.node_type == "rgbled":
            return ["https://github.com/MrYsLab/NeoPixelConnect"]
        if self.node_type == "mcp4725":
            return ["https://github.com/RobTillaart/MCP4725"]

    @classmethod
    def firmware_type_setup(cls, instances):
        output = []
        flag = False
        for inum, instance in enumerate(instances):
            if instance.node_type != "encoder":
                continue
            if "mcu" in instance.MASTER_PROVIDES:
                flag = True
                output.append(f"    encoder[{inum}].begin({instance.instances_name.upper()}_PIN_A, {instance.instances_name.upper()}_PIN_B, 4);")
        if flag:
            output.append("")
            # output.append("    timer = timerBegin(0, 80, true);")
            # output.append("    timerAttachInterrupt(timer, &handleLoop, true);")
            # output.append("    timerAlarmWrite(timer, 100, true);")
            # output.append("    timerAlarmEnable(timer);")
        return "\n".join(output)

    @classmethod
    def firmware_type_loop(cls, instances):
        output = []
        flag = False
        encoders = 0
        for inum, instance in enumerate(instances):
            if "mcu" in instance.MASTER_PROVIDES:
                flag = True
                if instance.node_type == "encoder":
                    encoders += 1
        if encoders:
            output.append("    for (int i = 0; i < NUM_ENCODERS; i++) {")
            output.append("        encoder[i].loop();")
            output.append("    }")
            output.append("")
        if flag:
            for inum, instance in enumerate(instances):
                if instance.node_type != "encoder":
                    continue
                if "mcu" in instance.MASTER_PROVIDES:
                    output.append(f"    VARIN32_{instance.instances_name.upper()}_POSITION = encoder[{inum}].getPosition();")
            output.append("")
        return "\n".join(output)
