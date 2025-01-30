import glob
import sys
import os

riocore_path = os.path.dirname(os.path.dirname(__file__))


class Firmware:
    def __init__(self, project):
        self.project = project
        self.firmware_path = os.path.join(project.config["output_path"], "Firmware")
        os.makedirs(self.firmware_path, exist_ok=True)
        project.config["riocore_path"] = riocore_path

    def generator(self, generate_pll=True):
        self.config = self.project.config.copy()

        self.expansion_pins = []
        for plugin_instance in self.project.plugin_instances:
            for pin in plugin_instance.expansion_outputs():
                self.expansion_pins.append(pin)
            for pin in plugin_instance.expansion_inputs():
                self.expansion_pins.append(pin)

        self.virtual_pins = []
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"].startswith("VIRT:"):
                    pinname = pin_config["pin"]
                    if pinname not in self.virtual_pins:
                        self.virtual_pins.append(pinname)

        self.interface_c()
        self.riocore_h()
        self.riocore_c()
        self.simulation_c()
        self.makefile()

    def interface_c(self):
        protocol = self.project.config["jdata"].get("protocol", "SPI")
        if protocol == "UDP":
            for ppath in glob.glob(os.path.join(riocore_path, "interfaces", "*", "*.c")):
                if protocol == ppath.split(os.sep)[-2]:
                    rdata = open(ppath, "r").read()
                    rdata = rdata.replace("rtapi_print", "printf")
                    rdata = rdata.replace("strerror(errno)", '"error"')
                    rdata = rdata.replace("errno", "1")

                    idata = "\n"
                    idata += "#include <unistd.h>\n"
                    idata += "#include <time.h>\n"
                    idata += "\n"
                    idata += "struct timespec ns_timestamp;\n"
                    idata += "\n"
                    idata += "long rtapi_get_time() {\n"
                    idata += "    clock_gettime(CLOCK_MONOTONIC, &ns_timestamp);\n"
                    idata += "    return (double)ns_timestamp.tv_sec * 1000000000 + ns_timestamp.tv_nsec;\n"
                    idata += "}\n"
                    idata += "\n"
                    idata += "void rtapi_delay(int ns) {\n"
                    idata += "    usleep(ns / 1000);\n"
                    idata += "}\n"
                    idata += "\n"
                    idata += rdata
                    open(os.path.join(self.firmware_path, "interface.c"), "w").write(idata)

    def riocore_h(self):
        sysclk_speed = self.project.config["speed"]
        ip = "192.168.10.194"
        port = 2390
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "interface":
                ip = plugin_instance.plugin_setup.get("ip", plugin_instance.option_default("ip", ip))
                port = plugin_instance.plugin_setup.get("port", plugin_instance.option_default("port", port))

        ip = self.project.config["jdata"].get("ip", ip)
        port = self.project.config["jdata"].get("port", port)
        src_port = self.project.config["jdata"].get("src_port", port)
        dst_port = self.project.config["jdata"].get("dst_port", port)

        output = []
        output.append("#include <stdio.h>")
        output.append("#include <unistd.h>")
        output.append("#include <stdint.h>")
        output.append("#include <stdbool.h>")
        output.append("#include <string.h>")
        output.append("#include <time.h>")
        output.append("")
        output.append(f"#define CLOCK_SPEED {sysclk_speed}")
        output.append(f"#define BUFFER_SIZE {self.project.buffer_size//8} // {self.project.buffer_size} bits")
        if port and ip:
            output.append(f'#define UDP_IP "{ip}"')
            output.append(f"#define SRC_PORT {dst_port}")
            output.append(f"#define DST_PORT {src_port}")
            output.append("")

        output.append("void read_rxbuffer(uint8_t *rxBuffer);")
        output.append("void write_txbuffer(uint8_t *txBuffer);")
        output.append("")

        if self.project.multiplexed_input:
            output.append("extern float MULTIPLEXER_INPUT_VALUE;")
            output.append("extern uint8_t MULTIPLEXER_INPUT_ID;")
        if self.project.multiplexed_output:
            output.append("extern float MULTIPLEXER_OUTPUT_VALUE;")
            output.append("extern uint8_t MULTIPLEXER_OUTPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
            for data_name, data_config in plugin_instance.interface_data().items():
                if not data_config.get("expansion"):
                    variable_name = data_config["variable"]
                    variable_size = data_config["size"]
                    variable_bytesize = variable_size // 8
                    if plugin_instance.TYPE == "frameio":
                        output.append(f"extern uint8_t {variable_name}[{variable_bytesize}];")
                    elif variable_size > 1:
                        variable_size_align = 8
                        for isize in (8, 16, 32, 64):
                            variable_size_align = isize
                            if isize >= variable_size:
                                break
                        output.append(f"extern int{variable_size_align}_t {variable_name};")
                    else:
                        output.append(f"extern bool {variable_name};")
        output.append("")

        open(os.path.join(self.firmware_path, "riocore.h"), "w").write("\n".join(output))

    def riocore_c(self):
        output = []
        output.append("")
        output.append("#include <stdio.h>")
        output.append("#include <unistd.h>")
        output.append("#include <stdint.h>")
        output.append("#include <stdbool.h>")
        output.append("#include <string.h>")
        output.append("#include <time.h>")
        output.append("#include <riocore.h>")
        output.append("")

        if self.project.multiplexed_output:
            output.append("float MULTIPLEXER_INPUT_VALUE;")
            output.append("uint8_t MULTIPLEXER_INPUT_ID;")
        if self.project.multiplexed_input:
            output.append("float MULTIPLEXER_OUTPUT_VALUE;")
            output.append("uint8_t MULTIPLEXER_OUTPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
            for data_name, data_config in plugin_instance.interface_data().items():
                if not data_config.get("expansion"):
                    variable_name = data_config["variable"]
                    variable_size = data_config["size"]
                    multiplexed = data_config.get("multiplexed", False)
                    variable_bytesize = variable_size // 8
                    if plugin_instance.TYPE == "frameio":
                        output.append(f"uint8_t {variable_name}[{variable_bytesize}];")
                    elif variable_size > 1:
                        variable_size_align = 8
                        for isize in (8, 16, 32, 64):
                            variable_size_align = isize
                            if isize >= variable_size:
                                break
                        output.append(f"int{variable_size_align}_t {variable_name} = 0;")
                    else:
                        output.append(f"bool {variable_name} = 0;")
        output.append("")
        output.append("")

        output.append("// PC -> MC")
        output.append("void read_rxbuffer(uint8_t *rxBuffer) {")
        input_pos = self.project.buffer_size

        variable_size = 32
        byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
        byte_start = self.project.buffer_bytes - 1 - byte_start
        output.append(f"    // memcpy(&header, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size}) // {input_pos};")
        input_pos -= variable_size

        if self.project.multiplexed_output:
            variable_size = self.project.multiplexed_output_size
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&MULTIPLEXER_OUTPUT_VALUE, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
            input_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&MULTIPLEXER_OUTPUT_ID, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
            input_pos -= variable_size

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "output":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
                byte_start = self.project.buffer_bytes - 1 - byte_start
                if variable_size > 1:
                    output.append(f"    memcpy(&{variable_name}, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size}); // {input_pos}")
                else:
                    output.append(f"    {variable_name} = (rxBuffer[{byte_start}] & (1<<{bit_offset})); // {input_pos}")
                input_pos -= variable_size

        output.append("}")
        output.append("")

        output.append("// MC -> PC")
        output.append("void write_txbuffer(uint8_t *txBuffer) {")
        output_pos = self.project.buffer_size

        # header
        output.append("    txBuffer[0] = 97;")
        output.append("    txBuffer[1] = 116;")
        output.append("    txBuffer[2] = 97;")
        output.append("    txBuffer[3] = 100;")

        output_pos -= 32
        # timestamp
        output_pos -= 32

        if self.project.multiplexed_input:
            variable_size = self.project.multiplexed_input_size
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &MULTIPLEXER_OUTPUT_VALUE, {byte_size}); // {output_pos}")
            output_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &MULTIPLEXER_OUTPUT_ID, {byte_size}); // {output_pos}")
            output_pos -= variable_size

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            if data_config["direction"] == "input":
                byte_start, byte_size, bit_offset = self.project.get_bype_pos(output_pos, variable_size)
                byte_start = self.project.buffer_bytes - 1 - byte_start
                if variable_size > 1:
                    output.append(f"    memcpy(&txBuffer[{byte_start-(byte_size-1)}], &{variable_name}, {byte_size}); // {output_pos}")
                else:
                    output.append(f"    txBuffer[{byte_start}] |= ({variable_name}<<{bit_offset}); // {output_pos}")
                output_pos -= variable_size

        output.append("")
        output.append("}")
        output.append("")
        print(f"writing firmware to: {self.firmware_path}")
        open(os.path.join(self.firmware_path, "riocore.c"), "w").write("\n".join(output))

    def simulation_c(self):
        buffer_size_bytes = self.project.buffer_size // 8

        output = []
        output.append("#include <stdio.h>")
        output.append("#include <stdint.h>")
        output.append("#include <stdbool.h>")
        output.append("#include <string.h>")
        output.append("#include <riocore.h>")
        output.append("")

        protocol = self.project.config["jdata"].get("protocol", "SPI")

        output.append("int udp_init(const char *dstAddress, int dstPort, int srcPort);")
        output.append("void udp_tx(uint8_t *txBuffer, uint16_t size);")
        output.append("int udp_rx(uint8_t *rxBuffer, uint16_t size);")
        output.append("void udp_exit();")
        output.append("")

        output.append("int interface_init(void) {")
        if protocol == "UART":
            output.append("    uart_init();")
        elif protocol == "SPI":
            output.append("    spi_init();")
        elif protocol == "UDP":
            output.append("    udp_init(UDP_IP, DST_PORT, SRC_PORT);")
        else:
            print("ERROR: unsupported interface")
            sys.exit(1)
        output.append("}")
        output.append("")

        output.append("void interface_exit(void) {")
        if protocol == "UART":
            output.append("    uart_exit();")
        elif protocol == "SPI":
            output.append("    spi_exit();")
        elif protocol == "UDP":
            output.append("    udp_exit();")
        output.append("}")
        output.append("")

        output.append("void simulation(void) {")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            if data_config["direction"] == "input":
                if hasattr(plugin_instance, "simulate_c"):
                    output.append(plugin_instance.simulate_c(1000, data_name))

        output.append("}")
        output.append("")

        buffer_init = ["0"] * buffer_size_bytes
        output.append("int main(void) {")
        output.append("    uint16_t ret = 0;")
        output.append(f"    uint8_t rxBuffer[BUFFER_SIZE] = {{{', '.join(buffer_init)}}};")
        output.append(f"    uint8_t txBuffer[BUFFER_SIZE] = {{{', '.join(buffer_init)}}};")
        output.append("")
        output.append("    interface_init();")
        output.append("")
        output.append("    while (1) {")
        output.append("        ret = udp_rx(rxBuffer, BUFFER_SIZE);")
        output.append("        if (rxBuffer[0] == 0x74 && rxBuffer[1] == 0x69 && rxBuffer[2] == 0x72 && rxBuffer[3] == 0x77) {")
        output.append("            read_rxbuffer(rxBuffer);")
        output.append("            write_txbuffer(txBuffer);")
        output.append("            udp_tx(txBuffer, BUFFER_SIZE);")
        output.append("")
        output.append("            simulation();")
        output.append("        }")
        output.append("    }")
        output.append("    return 0;")
        output.append("}")
        output.append("")
        print(f"writing firmware to: {self.firmware_path}")
        open(os.path.join(self.firmware_path, "simulator.c"), "w").write("\n".join(output))

    def makefile(self):
        output = []
        output.append("")
        output.append("all: simulator")
        output.append("")
        output.append("clean:")
        output.append("	rm -f simulator")
        output.append("")
        output.append("simulator: simulator.c riocore.c interface.c")
        output.append("	gcc -o simulator -Os -I. simulator.c riocore.c interface.c")
        output.append("")
        output.append("simulator_run: simulator")
        output.append("	./simulator")
        output.append("")
        open(os.path.join(self.firmware_path, "Makefile"), "w").write("\n".join(output))
