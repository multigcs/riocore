import copy
import glob
import json
import os

import riocore

from riocore.plugins import PluginBase

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "satmcu"
        self.COMPONENT = "fpga"
        self.INFO = "mcu based satellite"
        self.DESCRIPTION = "mcu based satellite connected via RS422"
        self.KEYWORDS = ""
        self.NEEDS = ["fpga"]
        self.PROVIDES = ["gpio", "mcu"]
        self.TYPE = "base"
        self.IMAGE_SHOW = False
        self.PLUGIN_TYPE = "mcu"
        self.VERILOGS = ["satmcu.v", "uart_baud.v", "uart_rx.v", "uart_tx.v"]
        self.URL = ""
        self.SIGNALS = {}
        self.jdata = {
            "speed": 0,
            "toolchain": None,
        }

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
                "baud": {
                    "default": 2500000,
                    "type": int,
                    "min": 9600,
                    "max": 10000000,
                    "unit": "bit/s",
                    "description": "serial baud rate",
                },
            },
        )

        self.PINDEFAULTS = {
            "SAT:OUT": {
                "direction": "output",
                "edge": "source",
                "bus": True,
                "type": ["SATCON"],
            },
        }

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
        self.master = self.instances_name
        self.gmaster = "board0"
        self.gmaster = None

    def update_pins(self, parent):
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            connected_pin["setup"]["pin"] = connected_pin["pin"]

    def builder(self, config, command):
        if not isinstance(config, dict):
            project = config
        else:
            project = riocore.Project(copy.deepcopy(config))
        firmware_path = os.path.join(project.config["output_path"], "Firmware", self.title)
        if not os.path.exists(firmware_path):
            riocore.log(f"ERROR: path not exist, please run generator first: {firmware_path}")
            return None
        return f"cd {firmware_path} && make {command}"

    def firmware(self, parent, instances):
        subname = self.instances_name

        output = []
        output.append("")
        output.append("int rxPin = 18;")
        output.append("int txPin = 19;")
        output.append("")

        sym_io = False
        if self.gateware.instance.protocol == "SPI":
            # input and output frames with has same size
            sym_io = True

        self.gateware.calc_buffersize(parent.project, sym_io=sym_io)
        self.gateware.calc_buffersize_sub(parent.project, subname, sym_io=sym_io, firmware=True)
        output.append(f"#define MCU_BUFFER_SIZE_TX {self.gateware.sub_buffer_size_in // 8}")
        output.append(f"#define MCU_BUFFER_SIZE_RX {self.gateware.sub_buffer_size_out // 8}")
        output.append("")
        in_bytes = self.gateware.sub_buffer_size_in // 8
        out_bytes = self.gateware.sub_buffer_size_out // 8
        output.append(f"uint8_t tx_buffer[MCU_BUFFER_SIZE_TX + 2] = {{0x64, 0x61, 0x74, 0x61,  {', '.join(['0'] * (in_bytes - 4))},  0, 0}};")
        output.append(f"uint8_t rx_buffer[MCU_BUFFER_SIZE_RX + 2] = {{0, 0, 0, 0,  {', '.join(['0'] * (out_bytes - 4))},  0, 0}};")
        output.append("")

        # Variables
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "output" or data_config["direction"] == "input":
                if not data_config.get("expansion"):
                    if size in {8, 16, 32}:
                        output.append(f"int{size}_t {variable_name} = 0;")
                    elif size == 1:
                        output.append(f"bool {variable_name} = 0;")
                    else:
                        output.append(f"//int{size}_t {variable_name} = 0;")
        output.append("")

        # write tx_buffer
        output.append("void rio_rtx(void) {")
        output.append("    // write tx_buffer")
        input_pos = 32
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "input":
                if data_config.get("expansion"):
                    continue
                if size in {16, 32}:
                    output.append(f"    memcpy(tx_buffer + {input_pos // 8}, &{variable_name}, {size // 8});")
                elif size == 8:
                    output.append(f"    tx_buffer[{input_pos // 8}] = variable_name;")
                elif size == 1:
                    bit = 7 - (input_pos - (input_pos // 8 * 8))
                    output.append(f"    if ({variable_name} == 1) {{")
                    output.append(f"        tx_buffer[{input_pos // 8}] |= (1<<{bit});")
                    output.append("    } else {")
                    output.append(f"        tx_buffer[{input_pos // 8}] &= ~(1<<{bit});")
                    output.append("    }")
                input_pos += size
        output.append("")
        output.append("    // send tx_buffer")
        output.append("    uint16_t csum = 0;")
        output.append("    for (int i = 0; i < MCU_BUFFER_SIZE_TX; i++) {")
        output.append("        csum += tx_buffer[i] + 1;")
        output.append("    }")
        output.append("    tx_buffer[MCU_BUFFER_SIZE_TX] = (csum >> 8 & 0xFF);")
        output.append("    tx_buffer[MCU_BUFFER_SIZE_TX + 1] = (csum & 0xFF);")
        output.append("    Serial2.write(tx_buffer, MCU_BUFFER_SIZE_TX + 2);")
        output.append("")

        # read rx_buffer
        output.append("    // receive rx_buffer")
        output.append("    int flen = Serial2.readBytes(rx_buffer, MCU_BUFFER_SIZE_RX + 2);")
        output.append("    if (flen == MCU_BUFFER_SIZE_RX + 2) {")
        output.append("        // read rx_buffer")
        output_pos = 32
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "output":
                if data_config.get("expansion"):
                    continue
                if size in {16, 32}:
                    output.append(f"        memcpy(&{variable_name}, rx_buffer + {output_pos // 8}, {size // 8});")
                elif size == 8:
                    output.append(f"        rx_buffer[{output_pos // 8}] = variable_name;")
                elif size == 1:
                    bit = 7 - (output_pos - (output_pos // 8 * 8))
                    output.append(f"        if ((rx_buffer[{output_pos // 8}] & (1<<{bit})) != 0) {{")
                    output.append(f"            {variable_name} = 1;")
                    output.append("        } else {")
                    output.append(f"            {variable_name} = 0;")
                    output.append("        }")
                output_pos += size
        output.append("    }")
        output.append("}")
        output.append("")

        # defines by plugin type
        ptypes = {}
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            if plugin_instance.NAME not in ptypes:
                ptypes[plugin_instance.NAME] = []
            ptypes[plugin_instance.NAME].append(plugin_instance)

        # defines
        for plugin_type, instances in ptypes.items():
            if hasattr(instances[0], "firmware_type_defines"):
                output.append(instances[0].firmware_type_defines(instances))
        output.append("")
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            variable_name = data_config["variable"]
            if hasattr(plugin_instance, "firmware_defines"):
                output.append(plugin_instance.firmware_defines(variable_name))
        output.append("")

        # setup
        output.append("void setup() {")
        output.append("")
        for plugin_type, instances in ptypes.items():
            if hasattr(instances[0], "firmware_type_setup"):
                output.append(instances[0].firmware_type_setup(instances))
        output.append("")
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            variable_name = data_config["variable"]
            if hasattr(plugin_instance, "firmware_setup"):
                output.append(plugin_instance.firmware_setup(variable_name))
        output.append("")

        output.append("    Serial.begin(115200);")
        output.append("    Serial.setTimeout(10);")
        output.append("    Serial2.begin(1000000, SERIAL_8N1, rxPin, txPin);")
        output.append("    Serial2.setTimeout(1);")
        output.append("    delay(100);")
        output.append("}")
        output.append("")

        # main loop
        output.append("void loop() {")
        output.append("")

        for plugin_type, instances in ptypes.items():
            if data_config["direction"] == "input":
                if hasattr(instances[0], "firmware_type_loop"):
                    output.append(instances[0].firmware_type_loop(instances))
        output.append("")
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "input":
                if hasattr(plugin_instance, "firmware_loop"):
                    output.append(plugin_instance.firmware_loop(variable_name))
        output.append("")
        output.append("    rio_rtx();")
        output.append("")
        for plugin_type, instances in ptypes.items():
            if data_config["direction"] == "output":
                if hasattr(instances[0], "firmware_type_loop"):
                    output.append(instances[0].firmware_type_loop(instances))
        output.append("")
        for size, plugin_instance, data_name, data_config in self.gateware.get_interface_data(parent.project):
            if plugin_instance.master != subname:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "output":
                if hasattr(plugin_instance, "firmware_loop"):
                    output.append(plugin_instance.firmware_loop(variable_name))
        output.append("")
        output.append("}")
        output.append("")

        src_path = os.path.join(self.jdata["output_path"], "src")
        lib_path = os.path.join(self.jdata["output_path"], "lib")
        os.makedirs(src_path, exist_ok=True)
        os.makedirs(lib_path, exist_ok=True)
        open(os.path.join(src_path, "main.ino"), "w").write("\n".join(output))

        makefile = """
all: build

~/.platformio/penv/bin/pio:
	wget -O /tmp/__get-platformio.py https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py
	python3 /tmp/__get-platformio.py
	rm -rf /tmp/__get-platformio.py

build: ~/.platformio/penv/bin/pio
	pio run

load: ~/.platformio/penv/bin/pio
	pio run --target=upload

"""
        open(os.path.join(self.jdata["output_path"], "Makefile"), "w").write(makefile)

        platformio = """
[env:esp32dev]
framework = arduino
board = esp32dev
platform = espressif32
#upload_speed = 115200
upload_speed = 500000
monitor_speed = 115200
upload_port = /dev/ttyUSB0

"""
        open(os.path.join(self.jdata["output_path"], "platformio.ini"), "w").write(platformio)
