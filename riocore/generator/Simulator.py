import copy
import glob
import importlib
import os
import sys

from riocore import halpins

riocore_path = os.path.dirname(os.path.dirname(__file__))


class Simulator:
    def __init__(self, project):
        self.project = project
        self.base_path = f"{self.project.config['output_path']}/Simulator"
        self.component_path = f"{self.base_path}"
        self.addons = {}
        for addon_path in glob.glob(f"{riocore_path}/generator/addons/*/simulator.py"):
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
                output.append(f"void simulate_{plugin_instance.instances_name}() {{")

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    direction = interface["direction"]
                    variable_size = interface["size"]
                    if interface["direction"] == "input":
                        if variable_size > 1:
                            output.append(f"    static float value_{iname} = 0.0;")
                        else:
                            output.append(f"    static uint8_t value_{iname} = 0;")

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    direction = interface["direction"]
                    variable_size = interface["size"]
                    if interface["direction"] == "output":
                        if variable_size > 1:
                            output.append(f"    float value_{iname} = data.{variable};")
                        else:
                            output.append(f"    uint8_t value_{iname} = data.{variable};")

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    direction = interface["direction"]
                    variable_size = interface["size"]
                    if interface["direction"] == "output":
                        if variable_size > 1:
                            output.append(f'    printf("{variable}: %f\\n", value_{iname});')
                        else:
                            output.append(f'    printf("{variable}: %i\\n", value_{iname});')

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    direction = interface["direction"]
                    variable_size = interface["size"]
                    if interface["direction"] == "input":
                        if variable_size > 1:
                            output.append(f"    // value_{iname} = 0.0;")
                        else:
                            output.append(f"    // value_{iname} = 0;")

                    output.append("    " + plugin_instance.simulate_c(iname, interface).strip())

                for iname, interface in plugin_instance.INTERFACE.items():
                    variable = interface["variable"]
                    direction = interface["direction"]
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

        output.append("    // simulated vars to txBuffer")
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
        header_list = ["stdint.h", "unistd.h", "stdlib.h", "stdio.h", "string.h", "math.h", "sys/mman.h"]
        if "serial":
            header_list += ["fcntl.h", "termios.h"]

        protocol = self.project.config["jdata"].get("protocol", "SPI")

        ip = "192.168.10.194"
        port = 2390
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "interface":
                ip = plugin_instance.plugin_setup.get("ip", plugin_instance.option_default("ip"))
                port = plugin_instance.plugin_setup.get("port", plugin_instance.option_default("port"))

        ip = self.project.config["jdata"].get("ip", ip)
        port = self.project.config["jdata"].get("port", port)

        defines = {
            "PREFIX": '"rio"',
            "JOINTS": "3",
            "BUFFER_SIZE": self.project.buffer_bytes,
            "OSC_CLOCK": self.project.config["speed"],
        }
        if port and ip:
            defines["UDP_IP"] = f'"{ip}"'
            defines["UDP_PORT"] = port
        defines["SERIAL_PORT"] = '"/dev/ttyVirt1"'
        defines["SERIAL_BAUD"] = "B1000000"

        defines["SPI_PIN_MOSI"] = "10"
        defines["SPI_PIN_MISO"] = "9"
        defines["SPI_PIN_CLK"] = "11"
        defines["SPI_PIN_CS"] = "7"
        defines["SPI_SPEED"] = "BCM2835_SPI_CLOCK_DIVIDER_256"

        for header in header_list:
            output.append(f"#include <{header}>")
        output.append("")

        for key, value in defines.items():
            output.append(f"#define {key} {value}")
        output.append("")

        output.append("static int 			      comp_id;")
        output.append("static const char 	      *prefix = PREFIX;")
        output.append("")
        output.append("uint32_t pkg_counter = 0;")
        output.append("uint32_t err_counter = 0;")
        output.append("")
        output.append("long stamp_last = 0;")
        output.append("")
        output.append("void rio_readwrite();")
        output.append("int error_handler(int retval);")
        output.append("")

        output += self.component_variables()
        for ppath in glob.glob(f"{riocore_path}/interfaces/*/*_sim.c"):
            if protocol == ppath.split("/")[-2]:
                output.append("/*")
                output.append(f"    interface: {os.path.basename(os.path.dirname(ppath))}")
                output.append("*/")
                fdata = open(ppath, "r").read()
                fdata = fdata.replace("rtapi_print_msg", "printf").replace("RTAPI_MSG_ERR,", "")
                fdata = fdata.replace("rtapi_print", "printf")
                fdata = fdata.replace("errno", "1")
                fdata = fdata.replace("rtapi_get_time()", "1")
                output.append(fdata)

        output.append("int interface_init(void) {")
        if protocol == "UART":
            output.append("    uart_init();")
        elif protocol == "SPI":
            output.append("    spi_init();")
        elif protocol == "UDP":
            output.append("    udp_init();")
        else:
            print("ERROR: unsupported interface")
            sys.exit(1)
        output.append("}")
        output.append("")

        output.append("")
        output.append("/***********************************************************************")
        output.append("*                         PLUGIN GLOBALS                               *")
        output.append("************************************************************************/")
        output.append("")
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "frameio":
                output.append(f"long {plugin_instance.instances_name}_last_rx = 0;")
            for line in plugin_instance.globals_c().strip().split("\n"):
                output.append(line)
        output.append("")
        output.append("/***********************************************************************/")
        output.append("")

        output += self.component_buffer()
        output.append("void rio_readwrite() {")
        output.append("    uint8_t i = 0;")
        output.append("    uint8_t rxBuffer[BUFFER_SIZE * 2];")
        output.append("    uint8_t txBuffer[BUFFER_SIZE * 2];")
        output.append("")
        output.append("    for (i = 0; i < BUFFER_SIZE; i++) {")
        output.append("        txBuffer[i] = 0;")
        output.append("    }")
        output.append("")
        output.append("    if (data.sys_enable_request == 1) {")
        output.append("        data.sys_status = 1;")
        output.append("    }")
        output.append("    long stamp_new = 1;")
        output.append("    data.duration = (stamp_new - stamp_last) / 1000.0;")
        output.append("    stamp_last = stamp_new;")
        output.append("    //if (data.sys_enable == 1 && data.sys_status == 1) {")
        output.append("        pkg_counter += 1;")
        output.append("        write_txbuffer(txBuffer);")

        if protocol == "UART":
            output.append("        uart_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        elif protocol == "SPI":
            output.append("        spi_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        elif protocol == "UDP":
            output.append("        udp_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        else:
            print("ERROR: unsupported interface")
            sys.exit(1)

        output.append("        if (rxBuffer[0] == 116 && rxBuffer[1] == 105 && rxBuffer[2] == 114 && rxBuffer[3] == 119) {")
        output.append("            if (err_counter > 0) {")
        output.append("                err_counter = 0;")
        output.append('                printf("recovered..\\n");')
        output.append("            }")
        output.append("            read_rxbuffer(rxBuffer);")

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE != "interface":
                output.append(f"    simulate_{plugin_instance.instances_name}();")

        output.append("        } else {")
        output.append("            err_counter += 1;")
        output.append('            printf("wronng header (%i): ", err_counter);')
        output.append("            for (i = 0; i < BUFFER_SIZE; i++) {")
        output.append('                printf("%d ",rxBuffer[i]);')
        output.append("            }")
        output.append('            printf("\\n");')
        output.append("            if (err_counter > 3) {")
        output.append('                printf("too much errors..\\n");')
        output.append("                data.sys_status = 0;")
        output.append("            }")
        output.append("        }")
        output.append("    //} else {")
        output.append("    //    data.sys_status = 0;")
        output.append("    //}")
        output.append("}")
        output.append("")
        output.append("int main(void) {")
        output.append("    interface_init();")
        output.append("    while(1) {")
        output.append("        rio_readwrite();")
        output.append("    }")
        output.append("    return 0;")
        output.append("}")
        output.append("")
        output.append("")

        os.system(f"mkdir -p {self.component_path}/")
        open(f"{self.component_path}/rio-simulator.c", "w").write("\n".join(output))
