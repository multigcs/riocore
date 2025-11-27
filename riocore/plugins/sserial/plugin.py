import copy
import glob
import json
import os
import shutil

import riocore
from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "sserial"
        self.COMPONENT = "sserial"
        self.INFO = "support for custom mesa-sserial devices"
        self.DESCRIPTION = ""
        self.KEYWORDS = "smart-serial rgb wled rs422"
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "sserial"
        self.URL = ""
        self.OPTIONS = {
            "node_type": {
                "default": "sserial",
                "type": "select",
                "options": [
                    "sserial",
                    "rgb",
                    "adc",
                ],
                "description": "instance type",
                "reload": True,
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        self.SIGNALS = {}

        if node_type == "sserial":
            board_list = []
            for jboard in glob.glob(os.path.join(os.path.dirname(__file__), "boards", "*.json")):
                board_list.append(os.path.basename(jboard).replace(".json", ""))
            self.OPTIONS.update(
                {
                    "board": {
                        "default": board_list[0],
                        "type": "select",
                        "options": board_list,
                        "description": "board type",
                        "reload": True,
                    },
                    "cardname": {
                        "default": "9r01",
                        "type": "select",
                        "options": ["9r01", "9r02", "9r03", "9r04"],
                        "description": "card name",
                    },
                },
            )

            board = self.plugin_setup.get("board", self.option_default("board"))
            board_file = os.path.join(os.path.dirname(__file__), "boards", f"{board}.json")
            self.board_data = json.loads(open(board_file).read())

            self.PINDEFAULTS = {}
            for pin_name, pin_data in self.board_data["pins"].items():
                pin_data["pin"] = f"{self.instances_name}:{pin_data['pin']}"
                self.PINDEFAULTS[pin_name] = pin_data

            self.OPTIONS.update(self.board_data.get("options", {}))
            type_mapping = {"str": str, "bool": bool, "int": int, "float": float}
            for option in self.OPTIONS.values():
                option["type"] = type_mapping.get(option["type"], option["type"])

            self.SUB_PLUGINS = []
            for spn, sub_plugin in enumerate(self.board_data.get("plugins", [])):
                if "uid" not in sub_plugin:
                    sub_plugin["uid"] = f"{sub_plugin['type']}{spn}"
                self.SUB_PLUGINS.append(sub_plugin)

            self.IMAGE_SHOW = True
            self.IMAGE = f"boards/{board}.png"
            self.BUILDER = [
                "build",
                "load",
            ]

        elif node_type == "rgb":
            self.OPTIONS.update(
                {
                    "leds": {
                        "default": 8,
                        "type": "select",
                        "options": ["8", "16"],
                        "description": "number of leds",
                    },
                }
            )

            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGES = ["led"]
            self.SIGNALS = {}
            self.PINDEFAULTS = {
                "rgb": {"direction": "output", "edge": "target", "type": ["GPIO"]},
            }

        elif node_type == "adc":
            self.OPTIONS.update()

            self.TYPE = "io"
            self.IMAGE_SHOW = True
            self.IMAGES = ["spindle500w", "laser", "led"]
            self.SIGNALS = {
                "value": {
                    "direction": "input",
                    "min": 0,
                    "max": 2048,
                },
            }
            self.PINDEFAULTS = {
                "adc": {"direction": "input", "edge": "target", "type": ["GPIO"]},
            }

    def builder(self, config, command):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "sserial":
            if not isinstance(config, dict):
                project = config
            else:
                project = riocore.Project(copy.deepcopy(config))
            firmware_path = os.path.join(project.config["output_path"], "Firmware", self.title)
            cmd = f"cd {firmware_path} && make {command}"
            return cmd

    def update_prefixes(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "sserial":
                cardname = instance.plugin_setup.get("cardname", instance.option_default("cardname"))
                pwm_n = 0
                rgb_n = 0
                adc_n = 0
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    plugin_instance = connected_pin["instance"]
                    if hasattr(instance, "SSERIAL_NUM"):
                        plugin_instance.hm2_prefix = f"{instance.PREFIX}.{cardname}.{instance.SSERIAL_NUM}"
                        if connected_pin["name"] == "pwm":
                            plugin_instance.PREFIX = f"{instance.PREFIX}.{cardname}.{instance.SSERIAL_NUM}"
                            plugin_instance.SIGNALS[f"pwm{pwm_n}"] = plugin_instance.SIGNALS["value"]
                            del plugin_instance.SIGNALS["value"]
                            del plugin_instance.SIGNALS["enable"]
                            pwm_n += 1
                        elif connected_pin["name"] == "rgb":
                            leds = int(plugin_instance.plugin_setup.get("leds", plugin_instance.option_default("leds")))
                            instance.leds = leds
                            plugin_instance.PREFIX = f"{instance.PREFIX}.{cardname}.{instance.SSERIAL_NUM}"
                            for n in range(0, leds):
                                plugin_instance.SIGNALS[f"red-{n:02d}"] = {"direction": "output", "bool": True}
                                plugin_instance.SIGNALS[f"green-{n:02d}"] = {"direction": "output", "bool": True}
                                plugin_instance.SIGNALS[f"blue-{n:02d}"] = {"direction": "output", "bool": True}
                            rgb_n += 1
                        elif connected_pin["name"] == "adc":
                            plugin_instance.PREFIX = f"{instance.PREFIX}.{cardname}.{instance.SSERIAL_NUM}"
                            plugin_instance.SIGNALS[f"adc{adc_n}"] = plugin_instance.SIGNALS["value"]
                            del plugin_instance.SIGNALS["value"]
                            adc_n += 1

    def update_pins(self, parent):
        self.outputs = []
        self.output_inverts = []
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "sserial":
            self.pins_input = []
            self.pins_output = []
            self.pins_pwm = []
            self.pins_rgb = []
            self.pins_adc = []
            self.leds = 0
            input_pin_n = 0
            output_pin_n = 0
            pwm_pin_n = 0
            rgb_pin_n = 0
            adc_pin_n = 0
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
                plugin_instance = connected_pin["instance"]
                if not hasattr(plugin_instance, "hm2_prefix"):
                    riocore.log(f"ERROR: no hm2_prefix found: {connected_pin}")
                    continue
                psetup = connected_pin["setup"]
                pin = connected_pin["pin"]
                direction = connected_pin["direction"]
                inverted = connected_pin["inverted"]
                if connected_pin["name"] == "pwm":
                    self.pins_pwm.append(pin)
                    psetup["pin"] = f"{plugin_instance.hm2_prefix}.pwm-{pwm_pin_n:02d}"
                    pwm_pin_n += 1
                elif connected_pin["name"] == "rgb":
                    self.pins_rgb.append(pin)
                    psetup["pin"] = f"{plugin_instance.hm2_prefix}.rgb-{rgb_pin_n:02d}"
                    rgb_pin_n += 1
                elif connected_pin["name"] == "adc":
                    self.pins_adc.append(pin)
                    psetup["pin"] = f"{plugin_instance.hm2_prefix}.adc-{adc_pin_n:02d}"
                    adc_pin_n += 1
                elif direction == "input":
                    self.pins_input.append(pin)
                    if inverted:
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}-not"
                    else:
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}"
                    input_pin_n += 1
                else:
                    self.pins_output.append(pin)
                    if inverted:
                        self.output_inverts.append(f"{plugin_instance.hm2_prefix}.output-{output_pin_n:02d}")
                    psetup["pin"] = f"{plugin_instance.hm2_prefix}.output-{output_pin_n:02d}"
                    output_pin_n += 1
        elif node_type == "rgb":
            self.leds = int(self.plugin_setup.get("leds", self.option_default("leds")))

    def hal(self, parent):
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        if node_type == "sserial":
            for pin in self.output_inverts:
                parent.halg.setp_add(f"{pin}-invert", 1)

    def pdd_entry(cls, name, direction, ptype, size, offset, param_min=0.0, param_max=0.0):
        output = []
        output.append("    {")
        output.append("        .pdd = {")
        output.append("            .RecordType    = LBP_PDD_RECORD_TYPE_NORMAL,")
        output.append(f"            .DataSize      = {size},")
        output.append(f"            .DataType      = LBP_PDD_DATA_TYPE_{ptype.upper()},")
        output.append(f"            .DataDirection = LBP_PDD_DIRECTION_{direction.upper()},")
        output.append(f"            .ParamMin      = {param_min},")
        output.append(f"            .ParamMax      = {param_max},")
        output.append(f"            .ParamAddress  = PARAM_BASE_ADDRESS + {offset},")
        output.append(f'            "None\\0{name}"')
        output.append("        }")
        output.append("    },")
        return output

    def extra_files(cls, parent, instances):
        for instance in instances:
            node_type = instance.plugin_setup.get("node_type", instance.option_default("node_type"))
            if node_type == "sserial":
                board = instance.plugin_setup.get("board", instance.option_default("board"))
                cardname = instance.plugin_setup.get("cardname", instance.option_default("cardname"))
                bits_out = len(instance.pins_output)
                bits_in = len(instance.pins_input)
                leds = instance.leds
                int_size_in = 8
                int_size_out = 8
                int_size_leds = 8
                for int_size in (8, 16, 32):
                    if bits_in <= int_size:
                        int_size_in = int_size
                        break
                for int_size in (8, 16, 32):
                    if bits_out <= int_size:
                        int_size_out = int_size
                        break
                for int_size in (8, 16, 32):
                    if leds <= int_size:
                        int_size_leds = int_size
                        break

                byte_size_in = int_size_in // 8
                byte_size_out = int_size_out // 8
                byte_size_leds = int_size_leds // 8

                input_pin_n = 0
                output_pin_n = 0
                for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                    plugin_instance = connected_pin["instance"]
                    if not hasattr(plugin_instance, "hm2_prefix"):
                        riocore.log(f"ERROR: no hm2_prefix found: {connected_pin}")
                        continue
                    psetup = connected_pin["setup"]
                    pin = connected_pin["pin"]
                    direction = connected_pin["direction"]
                    inverted = connected_pin["inverted"]
                    if direction == "input":
                        if inverted:
                            psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}-not"
                        else:
                            psetup["pin"] = f"{plugin_instance.hm2_prefix}.input-{input_pin_n:02d}"
                        input_pin_n += 1
                    else:
                        psetup["pin"] = f"{plugin_instance.hm2_prefix}.output-{output_pin_n:02d}"
                        output_pin_n += 1

                # create firmware stuff
                firmware_path = os.path.join(parent.project.config["output_path"], "Firmware", instance.title)
                os.makedirs(firmware_path, exist_ok=True)
                instance.BUILDER_PATH = firmware_path
                os.makedirs(os.path.join(firmware_path, "src"), exist_ok=True)
                os.makedirs(os.path.join(firmware_path, "lib"), exist_ok=True)
                riocore.log(f"  {instance.instances_name} ({instance.title}): create firmware structure: {firmware_path}")
                output = []
                source = os.path.join(os.path.dirname(__file__), "sserial", "TEMPLATE.ino")
                for line in open(source).read().split("\n"):
                    if line.strip() == "//defines":
                        output.append(f'#define BOARD "{board}"')
                        if instance.board_data.get("multithread"):
                            output.append("#define MULTITHREAD")
                        led = instance.board_data.get("led")
                        if led:
                            output.append(f"#define STATUS_LED {led}")
                        output.append(f"#define SSerial {instance.board_data['sserial']}")

                        if instance.pins_rgb:
                            leds = instance.leds
                            output.append("#include <Adafruit_NeoPixel.h>")
                            output.append(f"Adafruit_NeoPixel pixels({leds}, 15, NEO_GRB + NEO_KHZ800);")
                        output.append("")
                    elif line.strip() == "//LBP_Discovery_Data":
                        output.append("static const LBP_Discovery_Data DISCOVERY_DATA =")
                        output.append("{")
                        output.append("  .RxSize = sizeof(ProcessDataOut)+1, // +1 for the fault status, remote transmits")
                        if bits_out or instance.pins_pwm or instance.pins_rgb:
                            output.append("  .TxSize = sizeof(ProcessDataIn), // remote receives")
                        else:
                            output.append("  .TxSize = 0, // remote receives")
                        output.append("  .ptoc   = PTOC_BASE_ADDRESS,")
                        output.append("  .gtoc   = GTOC_BASE_ADDRESS")
                        output.append("};")
                        output.append("")
                    elif line.strip() == "//ProcessDataOut":
                        output.append("static struct ProcessDataOut {")
                        output.append("    uint8_t fault;")
                        if bits_in:
                            output.append(f"    uint{int_size_in}_t input;")
                        if instance.pins_adc:
                            for adc_num, adc in enumerate(instance.pins_adc):
                                output.append(f"    float adc{adc_num};")
                        output.append("} pdata_out = {0x00000000};")
                        output.append("")
                    elif line.strip() == "//ProcessDataIn":
                        if bits_out or instance.pins_pwm or instance.pins_rgb:
                            output.append("static struct ProcessDataIn {")
                            if bits_out:
                                output.append(f"    uint{int_size_out}_t output;")
                            for pwm_num, pwm in enumerate(instance.pins_pwm):
                                output.append(f"    float pwm{pwm_num};")
                            for rgb_num, rgb in enumerate(instance.pins_rgb):
                                output.append(f"    uint{int_size_leds}_t  red;")
                                output.append(f"    uint{int_size_leds}_t  green;")
                                output.append(f"    uint{int_size_leds}_t  blue;")
                            output.append("} pdata_in = {0x00000000};")
                            output.append("")
                    elif line.strip() == "//CARD_NAME":
                        output.append(f'static const char CARD_NAME[] = "{cardname}";')
                        output.append("")
                    elif line.strip() == "//PDD":
                        offset = 0
                        if bits_out:
                            output += cls.pdd_entry("Output", "output", "bits", bits_out, offset)
                            offset += byte_size_out
                        if bits_in:
                            output += cls.pdd_entry("Input", "input", "bits", bits_out, offset)
                            offset += byte_size_in
                        for pwm_num, pwm in enumerate(instance.pins_pwm):
                            output += cls.pdd_entry(f"Pwm{pwm_num}", "output", "float", 32, offset)
                            offset += 4
                        for rgb_num, rgb in enumerate(instance.pins_rgb):
                            leds = instance.leds
                            for color in ("Red", "Green", "Blue"):
                                output += cls.pdd_entry(color, "output", "bits", leds, offset)
                                offset += byte_size_leds
                        for adc_num, adc in enumerate(instance.pins_adc):
                            output += cls.pdd_entry(f"Adc{adc_num}", "input", "float", 32, offset)
                            offset += 4
                        output.append("")
                    elif line.strip() == "//PTOC":
                        output.append("static const uint16_t PTOC[] = {")
                        offset = 2
                        if bits_out:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        if bits_in:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        for pwm in instance.pins_pwm:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        for rgb in instance.pins_rgb:
                            for color in ("Red", "Green", "Blue"):
                                output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                                offset += 1
                        for adc in instance.pins_adc:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        output.append("    0x0000")
                        output.append("};")
                        output.append("")
                    elif line.strip() == "//GTOC":
                        output.append("static const uint16_t GTOC[] = {")
                        output.append("    PDD_BASE_ADDRESS,")
                        offset = 1
                        output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                        offset += 1
                        if bits_out:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        if bits_in:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        for pwm in instance.pins_pwm:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        for rgb in instance.pins_rgb:
                            for color in ("Red", "Green", "Blue"):
                                output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                                offset += 1
                        for adc in instance.pins_adc:
                            output.append(f"    PDD_BASE_ADDRESS+{offset}*sizeof(LBP_PDD),")
                            offset += 1
                        output.append("    0x0000")
                        output.append("};")
                        output.append("")
                    elif line.strip() == "//setup":
                        for pin_num, pin in enumerate(instance.pins_output):
                            output.append(f"    pinMode({pin}, OUTPUT); // Output({pin_num:02d})")
                        for pin_num, pin in enumerate(instance.pins_input):
                            output.append(f"    pinMode({pin}, INPUT_PULLUP); // Input({pin_num:02d})")
                        for pin_num, pin in enumerate(instance.pins_pwm):
                            output.append(f"    pinMode({pin}, OUTPUT); // PWM({pin_num})")
                        for pin_num, pin in enumerate(instance.pins_adc):
                            output.append(f"    pinMode({pin}, INPUT);  // Adc({pin_num:02d})")
                        if instance.pins_rgb:
                            output.append("    pixels.begin();")
                            output.append("    pixels.clear();")
                        output.append("")
                    elif line.strip() == "//pdata_in_next":
                        if bits_out or instance.pins_pwm or instance.pins_rgb:
                            output.append("            uint8_t pdata_in_next[sizeof(pdata_in)];")
                            output.append("            if (cmd.value == LBP_COMMAND_RPC_SMARTSERIAL_PROCESS_DATA) {")
                            output.append("                for (size_t i = 0; i < sizeof(pdata_in); i++) {")
                            output.append("                    while (!SSerial.available()) {yield();}")
                            output.append("                    const uint8_t c = SSerial.read();")
                            output.append("                    crc = LBP_CalcNextCRC(c, crc);")
                            output.append("                    pdata_in_next[i] = c;")
                            output.append("                }")
                            output.append("            }")
                            output.append("")
                    elif line.strip() == "//pdata_out.input":
                        if bits_in:
                            output.append("    pdata_out.input = 0;")
                            for pin_num, pin in enumerate(instance.pins_input):
                                output.append(f"    if (digitalRead({pin})) {{")
                                output.append(f"        pdata_out.input |= (1<<{pin_num});")
                                output.append("    }")
                        for pin_num, pin in enumerate(instance.pins_adc):
                            output.append(f"    pdata_out.adc{pin_num} = analogRead({pin});")
                    elif line.strip() == "//pdata_in.output":
                        for pin_num, pin in enumerate(instance.pins_output):
                            output.append(f"    digitalWrite({pin}, (pdata_in.output & (1<<{pin_num})) ? HIGH : LOW);")
                        for pwm_num, pwm in enumerate(instance.pins_pwm):
                            output.append(f"    analogWrite({pwm}, pdata_in.pwm{pwm_num});")
                        if instance.pins_rgb:
                            leds = instance.leds
                            for led in range(0, leds):
                                output.append(f"    pixels.setPixelColor({led}, pixels.Color(")
                                output.append(f"        (pdata_in.red & (1<<{led})) ? 255 : 0,")
                                output.append(f"        (pdata_in.green & (1<<{led})) ? 255 : 0,")
                                output.append(f"        (pdata_in.blue & (1<<{led})) ? 255 : 0")
                                output.append("    ));")
                            output.append("    pixels.show();")
                    else:
                        output.append(line)
                target = os.path.join(firmware_path, "src", "main.ino")
                open(target, "w").write("\n".join(output))

                output = [""]
                output.append(f"[env:{board}]")
                output.append("framework = arduino")
                output.append(f"board = {instance.board_data['board']}")
                output.append(f"platform = {instance.board_data['platform']}")

                upload_port = instance.plugin_setup.get("upload_port", instance.option_default("upload_port"))
                if upload_port:
                    output.append("#upload_speed = 115200")
                    output.append("upload_speed = 500000")
                    output.append("monitor_speed = 115200")
                    output.append(f"upload_port = {upload_port}")

                output.append("")
                output.append("")
                target = os.path.join(firmware_path, "platformio.ini")
                open(target, "w").write("\n".join(output))

                output = [""]
                output.append("all: build")
                output.append("")

                deps = ""
                if instance.board_data["platform"] == "raspberrypi":
                    deps = " ~/.platformio/penv/bin/pio"
                    output.append("~/.platformio/penv/bin/pio:")
                    output.append("	wget -O /tmp/__get-platformio.py https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py")
                    output.append("	python3 /tmp/__get-platformio.py")
                    output.append("	rm -rf /tmp/__get-platformio.py")
                    output.append("")

                output.append(f"build:{deps}")
                output.append("	pio run")
                output.append("")
                output.append(f"load:{deps}")
                output.append("	pio run -t nobuild -t upload")
                output.append("")
                output.append("")
                target = os.path.join(firmware_path, "Makefile")
                open(target, "w").write("\n".join(output))

                for filename in ("LBP.cpp", "LBP.h"):
                    source = os.path.join(os.path.dirname(__file__), "sserial", filename)
                    target = os.path.join(firmware_path, "src", filename)
                    shutil.copy(source, target)
