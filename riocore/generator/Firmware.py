import hashlib
import glob
import importlib
import os


riocore_path = os.path.dirname(os.path.dirname(__file__))


class Firmware:
    def __init__(self, project):
        self.project = project
        self.base_path = f"{self.project.config['output_path']}/Firmware"
        self.firmware_path = f"{self.base_path}"
        self.addons = {}
        for addon_path in glob.glob(f"{riocore_path}/generator/addons/*/firmware.py"):
            addon_name = addon_path.split("/")[-2]
            self.addons[addon_name] = importlib.import_module(".linuxcnc", f"riocore.generator.addons.{addon_name}")

    def generator(self):
        self.component()

    def component_variables(self):
        output = []
        output.append("typedef struct {")
        output.append("    // hal variables")
        output.append("    uint8_t   sys_enable;")
        output.append("    uint8_t   sys_enable_request;")
        output.append("    uint8_t   sys_status;")
        output.append("    float duration;")

        if self.project.multiplexed_output:
            output.append("    float MULTIPLEXER_OUTPUT_VALUE;")
            output.append("    uint8_t MULTIPLEXER_OUTPUT_ID;")
        if self.project.multiplexed_input:
            output.append("    float MULTIPLEXER_INPUT_VALUE;")
            output.append("    uint8_t MULTIPLEXER_INPUT_ID;")

        output.append("    // raw variables")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            variable_bytesize = variable_size // 8
            if plugin_instance.TYPE == "frameio":
                output.append(f"    uint8_t {variable_name}[{variable_bytesize}];")
            elif variable_size > 1:
                output.append(f"    int{variable_size if variable_size != 24 else 32}_t {variable_name};")
            else:
                output.append(f"    uint8_t {variable_name};")
        output.append("")
        output.append("} data_t;")
        output.append("static data_t data;")
        output.append("")

        return output

    def component_buffer(self):
        output = []
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE != "interface":
                string = plugin_instance.firmware_defines()
                if string.strip():
                    output.append(string)
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE != "interface":
                output.append(f"void instance_{plugin_instance.instances_name}() {{")

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    variable_size = interface["size"]
                    if interface["direction"] == "input":
                        if variable_size > 1:
                            output.append(f"    static float value_{iname} = 0.0;")
                        else:
                            output.append(f"    static uint8_t value_{iname} = 0;")

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    variable_size = interface["size"]
                    if interface["direction"] == "output":
                        if variable_size > 1:
                            output.append(f"    float value_{iname} = data.{variable};")
                        else:
                            output.append(f"    uint8_t value_{iname} = data.{variable};")

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    variable_size = interface["size"]
                    if interface["direction"] == "output":
                        if variable_size > 1:
                            output.append(f'    // printf("{variable}: %f\\n", value_{iname});')
                        else:
                            output.append(f'    // printf("{variable}: %i\\n", value_{iname});')

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    variable_size = interface["size"]
                    if interface["direction"] == "input":
                        if variable_size > 1:
                            output.append(f"    // value_{iname} = 0.0;")
                        else:
                            output.append(f"    // value_{iname} = 0;")

                output.append("    " + plugin_instance.firmware_loop().strip())

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    variable_size = interface["size"]
                    if interface["direction"] == "input":
                        output.append(f"    data.{variable} = value_{iname};")

                output.append("}")
                output.append("")

        output.append("void write_txbuffer(uint8_t *txBuffer) {")
        output.append("    int i = 0;")
        output.append("    for (i = 0; i < BUFFER_SIZE; i++) {")
        output.append("        txBuffer[i] = 0;")
        output.append("    }")
        output.append("    txBuffer[0] = 97;")
        output.append("    txBuffer[1] = 116;")
        output.append("    txBuffer[2] = 97;")
        output.append("    txBuffer[3] = 100;")

        output_pos = self.project.buffer_size - self.project.header_size

        if self.project.multiplexed_output:
            output.append("    // copy next multiplexed value")
            output.append(f"    if (data.MULTIPLEXER_OUTPUT_ID < {self.project.multiplexed_output}) {{;")
            output.append("        data.MULTIPLEXER_OUTPUT_ID += 1;")
            output.append("    } else {")
            output.append("        data.MULTIPLEXER_OUTPUT_ID = 0;")
            output.append("    };")
        mpid = 0
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if not multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "output":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
                output.append(f"    if (data.MULTIPLEXER_OUTPUT_ID == {mpid}) {{;")
                byte_start = self.project.buffer_bytes - 1 - byte_start
                output.append(f"        memcpy(&data.MULTIPLEXER_OUTPUT_VALUE, &data.{variable_name}, {byte_size});")
                output.append("    };")
                mpid += 1

        if self.project.multiplexed_output:
            variable_size = self.project.multiplexed_output_size
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &data.MULTIPLEXER_OUTPUT_VALUE, {byte_size});")
            output_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &data.MULTIPLEXER_OUTPUT_ID, {byte_size});")
            output_pos -= variable_size

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]

            if data_config["direction"] == "input":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
                byte_start = self.project.buffer_bytes - 1 - byte_start
                if variable_size > 1:
                    output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &data.{variable_name}, {byte_size});")
                else:
                    output.append(f"    txBuffer[{byte_start}] |= (data.{variable_name}<<{bit_offset});")
                output_pos -= variable_size

        output.append("}")
        output.append("")

        output.append("void read_rxbuffer(uint8_t *rxBuffer) {")
        output.append("    // rxBuffer to raw vars")
        input_pos = self.project.buffer_size - self.project.header_size
        if self.project.multiplexed_input:
            variable_size = self.project.multiplexed_input_size
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&data.MULTIPLEXER_INPUT_VALUE, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
            input_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&data.MULTIPLEXER_INPUT_ID, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
            input_pos -= variable_size

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "output":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
                byte_start = self.project.buffer_bytes - 1 - byte_start
                if variable_size > 1:
                    output.append(f"    memcpy(&data.{variable_name}, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
                else:
                    output.append(f"    if ((rxBuffer[{byte_start}] & (1<<{bit_offset})) != 0) {{")
                    output.append(f"        data.{variable_name} = 1;")
                    output.append("    } else {")
                    output.append(f"        data.{variable_name} = 0;")
                    output.append("    }")
                input_pos -= variable_size

        mpid = 0
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if not multiplexed:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "output":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
                output.append(f"    if (data.MULTIPLEXER_INPUT_ID == {mpid}) {{;")
                byte_start = self.project.buffer_bytes - 1 - byte_start
                output.append(f"        memcpy(&data.{variable_name}, &data.MULTIPLEXER_INPUT_VALUE, {byte_size});")
                output.append("    };")
                mpid += 1

        output.append("}")
        output.append("")
        return output

    def component(self):
        output = []
        protocol = self.project.config["jdata"].get("protocol", "SPI")

        header_list = ["Arduino.h"]
        if protocol == "UDP":
            header_list.append("ETH.h")
            header_list.append("ESPmDNS.h")
            header_list.append("WiFiUdp.h")

        defines = {
            "PREFIX": '"rio"',
            "JOINTS": "3",
            "BUFFER_SIZE": self.project.buffer_bytes,
            "OSC_CLOCK": self.project.config["speed"],
        }

        for header in header_list:
            output.append(f"#include <{header}>")
        output.append("")

        if protocol == "UDP":
            output.append("WiFiUDP Udp;")
            output.append("unsigned int localPort = 2390;")

        for key, value in defines.items():
            output.append(f"#define {key} {value}")
        output.append("")

        output += self.component_variables()
        output += self.component_buffer()
        output.append("")

        output.append("""

uint8_t step = 0;
float frequencyScale;

#define PRU_BASEFREQ 40000
#define STEPBIT 22
#define JOINTS 2
bool isEnabled[JOINTS];
bool isForward[JOINTS];
bool isStepping[JOINTS];
int32_t frequencyCommand[JOINTS];
int32_t rawCount[JOINTS];
int32_t DDSaccumulator[JOINTS];
int32_t DDSaddValue[JOINTS];

int step_pins[JOINTS];
int dir_pins[JOINTS];

int32_t stepgen_velocity[JOINTS];
int32_t stepgen_position[JOINTS];


void makeSteps() {
    int8_t i;
    int32_t stepNow;
    for (i = 0; i < JOINTS; i++) {
        stepNow = 0;
        isEnabled[i] = true;
        if (isEnabled[i] == true) {
            frequencyCommand[i] = stepgen_velocity[i];
            DDSaddValue[i] = frequencyCommand[i] * frequencyScale;
            stepNow = DDSaccumulator[i];
            DDSaccumulator[i] += DDSaddValue[i];
            stepNow ^= DDSaccumulator[i];
            stepNow &= (1L << STEPBIT);
            rawCount[i] = DDSaccumulator[i] >> STEPBIT;

            if (DDSaddValue[i] > 0) {
                isForward[i] = true;
            } else {
                isForward[i] = false;
            }
            if (stepNow) {
                digitalWrite(dir_pins[i], isForward[i]);
                digitalWrite(step_pins[i], 1);
                stepgen_position[i] = DDSaccumulator[i];
                isStepping[i] = true;
            }
        }
    }
}

void resetSteps() {
    int8_t i;
    for (i = 0; i < JOINTS; i++) {
        if (isStepping[i]) {
            digitalWrite(step_pins[i], 0);
        }
    }
}

""")

        output.append("void updateBaseThread() {")
        output.append("    if (!step) {")
        output.append("        frequencyScale = (float)(1 << STEPBIT) / (float)PRU_BASEFREQ;")
        output.append("        stepgen_velocity[0] = data.VAROUT32_STEPDIR4_VELOCITY;")
        output.append("        stepgen_velocity[1] = data.VAROUT32_STEPDIR5_VELOCITY;")
        output.append("        makeSteps();")
        output.append("        data.VARIN32_STEPDIR4_POSITION = stepgen_position[0];")
        output.append("        data.VARIN32_STEPDIR5_POSITION = stepgen_position[1];")
        output.append("        step = true;")
        output.append("    } else {")
        output.append("        resetSteps();")
        output.append("        step = false;")
        output.append("    }")
        output.append("}")
        output.append("")

        output.append("void setup() {")
        if protocol == "UART":
            output.append("    Serial.begin(1000000);")
        else:
            output.append("    Serial.begin(115200);")

        output.append("")

        if protocol == "UDP":
            output.append("    ETH.begin();")
            # output.append("    /*")
            output.append("    // setup static ip")
            output.append("    IPAddress myIP(192, 168, 80, 242);")
            output.append("    IPAddress myGW(192, 168, 80, 1);")
            output.append("    IPAddress mySN(255, 255, 255, 0);")
            output.append("    ETH.config(myIP, myGW, mySN);")
            # output.append("    */")
            output.append("    Udp.begin(localPort);")
            output.append("")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE != "interface":
                string = plugin_instance.firmware_setup()
                if string.strip():
                    output.append(string)
        output.append("}")
        output.append("")

        if protocol == "UART":
            output.append("void loop() {")
            output.append("    uint8_t rxBuffer[BUFFER_SIZE * 2];")
            output.append("    uint8_t txBuffer[BUFFER_SIZE * 2];")
            output.append("    uint8_t rec = Serial.read(rxBuffer, BUFFER_SIZE * 2);")
            output.append("    if (rec == BUFFER_SIZE && rxBuffer[0] == 116 && rxBuffer[1] == 105 && rxBuffer[2] == 114 && rxBuffer[3] == 119) {")
            output.append("        read_rxbuffer(rxBuffer);")
            output.append("        write_txbuffer(txBuffer);")
            output.append("        Serial.write(txBuffer, BUFFER_SIZE);")
            for plugin_instance in self.project.plugin_instances:
                if plugin_instance.TYPE != "interface":
                    output.append(f"            instance_{plugin_instance.instances_name}();")

            output.append("    }")
            output.append("}")
            output.append("")

        elif protocol == "UDP":
            output.append("void loop() {")
            output.append("    uint8_t rxBuffer[BUFFER_SIZE * 2];")
            output.append("    uint8_t txBuffer[BUFFER_SIZE * 2];")
            output.append("    int packetSize = Udp.parsePacket();")
            output.append("    if (packetSize) {")
            output.append("        IPAddress remoteIp = Udp.remoteIP();")
            output.append("        int len = Udp.read(rxBuffer, BUFFER_SIZE);")
            output.append("        if (len == BUFFER_SIZE && rxBuffer[0] == 116 && rxBuffer[1] == 105 && rxBuffer[2] == 114 && rxBuffer[3] == 119) {")
            output.append("            read_rxbuffer(rxBuffer);")
            output.append("            write_txbuffer(txBuffer);")
            output.append("            Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());")
            output.append("            Udp.write((uint8_t*)txBuffer, BUFFER_SIZE);")
            output.append("            Udp.endPacket();")
            output.append("        }")
            output.append("    }")
            output.append("")

            output.append("}")
            output.append("")

        board = self.project.config["jdata"].get("board")
        platform = self.project.config["jdata"].get("platform")

        platformio_ini = []
        platformio_ini.append("")
        platformio_ini.append(f"[env:{board}]")
        platformio_ini.append("framework = arduino")
        platformio_ini.append(f"platform = {platform}")
        platformio_ini.append(f"board = {board}")
        platformio_ini.append("upload_protocol = esptool")
        platformio_ini.append("")

        makefile = []
        makefile.append("")
        makefile.append("all: build load")
        makefile.append("")
        makefile.append("build:")
        makefile.append("	pio run")
        makefile.append("	cp -v hash_new.txt hash_compiled.txt")
        makefile.append("")
        makefile.append("load:")
        makefile.append("	pio run --target upload")
        makefile.append("	cp -v hash_new.txt hash_compiled.txt")
        makefile.append("	cp -v hash_new.txt hash_flashed.txt")
        makefile.append("")

        os.makedirs(f"{self.firmware_path}/src", exist_ok=True)
        os.makedirs(f"{self.firmware_path}/lib", exist_ok=True)
        open(f"{self.firmware_path}/platformio.ini", "w").write("\n".join(platformio_ini))
        open(f"{self.firmware_path}/Makefile", "w").write("\n".join(makefile))
        open(f"{self.firmware_path}/src/main.ino", "w").write("\n".join(output))

        # write hash of rio.v to filesystem
        hash_file_compiled = f"{self.firmware_path}/hash_compiled.txt"
        hash_compiled = ""
        if os.path.isfile(hash_file_compiled):
            hash_compiled = open(hash_file_compiled, "r").read()

        hash_file_flashed = f"{self.firmware_path}/hash_flashed.txt"
        hash_flashed = ""
        if os.path.isfile(hash_file_flashed):
            hash_flashed = open(hash_file_flashed, "r").read()

        hash_md5 = hashlib.md5()
        with open(f"{self.firmware_path}/src/main.ino", "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        hash_new = hash_md5.hexdigest()

        if hash_compiled != hash_new:
            print("!!! firmware changed: needs to be build and flash |||")
        elif hash_flashed != hash_new:
            print("!!! firmware changed: needs to flash |||")
        hash_file_new = f"{self.firmware_path}/hash_new.txt"
        open(hash_file_new, "w").write(hash_new)
