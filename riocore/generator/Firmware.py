import glob
import hashlib
import importlib
import os
import shutil
import stat
import json

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

        self.linked_pins = []
        self.top()

    def top(self):
        output = []
        
        buffer_size_bytes = self.project.buffer_size // 8
        
        sysclk_speed = self.project.config["speed"]
        input_variables_list = ["header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24]"]
        input_variables_list += ["timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24]"]
        self.iface_in = []
        self.iface_out = []
        output_pos = self.project.buffer_size


        output.append("")
        output.append("#include <stdio.h>")
        output.append("#include <stdint.h>")
        output.append("#include <stdbool.h>")
        output.append("#include <string.h>")
        output.append("#include <time.h>")
        output.append("struct timespec ns_timestamp;")

        output.append("")
        output.append("long rtapi_get_time() {")
        output.append("    clock_gettime(CLOCK_REALTIME, &ns_timestamp);")
        output.append("    return ns_timestamp.tv_nsec;")
        output.append("}")
        output.append("")
        output.append("void rtapi_delay() {")
        output.append("")
        output.append("}")
        output.append("")



        protocol = self.project.config["jdata"].get("protocol", "SPI")

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

        if port and ip:
            output.append(f"#define UDP_IP \"{ip}\"")
            output.append(f"#define SRC_PORT {dst_port}")
            output.append(f"#define DST_PORT {src_port}")


        output.append("")
        output.append(f"#define CLOCK_SPEED {sysclk_speed}")
        output.append(f"#define BUFFER_SIZE {self.project.buffer_size//8} // {self.project.buffer_size} bits")
        output.append("")


        generic_spi = self.project.config["jdata"].get("generic_spi", False)
        rpi5 = self.project.config["jdata"].get("rpi5", False)
        if protocol == "SPI" and generic_spi is True:
            for ppath in glob.glob(os.path.join(riocore_path, "interfaces", "*", "*.c_generic")):
                if protocol == ppath.split(os.sep)[-2]:
                    output.append("/*")
                    output.append(f"    interface: {os.path.basename(os.path.dirname(ppath))}")
                    output.append("*/")
                    output.append(open(ppath, "r").read())
        elif protocol == "SPI" and rpi5 is True:
            for ppath in glob.glob(os.path.join(riocore_path, "interfaces", "*", "*.c_rpi5")):
                if protocol == ppath.split(os.sep)[-2]:
                    output.append("/*")
                    output.append(f"    interface: {os.path.basename(os.path.dirname(ppath))}")
                    output.append("*/")
                    output.append(open(ppath, "r").read())
        else:
            for ppath in glob.glob(os.path.join(riocore_path, "interfaces", "*", "*.c")):
                if protocol == ppath.split(os.sep)[-2]:
                    output.append("/*")
                    output.append(f"    interface: {os.path.basename(os.path.dirname(ppath))}")
                    output.append("*/")
                    idata = open(ppath, "r").read()
                    idata = idata.replace("rtapi_print", "printf")
                    idata = idata.replace("strerror(errno)", "\"error\"")
                    idata = idata.replace("errno", "1")
                    output.append(idata)






        output.append("""

int udp_rx(uint8_t *rxBuffer, uint16_t size) {
    int i;
    int ret;
    long t1;
    long t2;
    uint8_t rxBufferTmp[BUFFER_SIZE*2];

    // Receive incoming datagram
    t1 = rtapi_get_time();
    do {
        ret = recv(udpSocket, rxBufferTmp, BUFFER_SIZE*2, 0);
        if (ret < 0) {
            rtapi_delay(READ_PCK_DELAY_NS);
        }
        t2 = rtapi_get_time();
    }
    while ((ret < 0) && ((t2 - t1) < 2*1000*1000));

    if (ret > 0) {
        errCount = 0;
        if (ret == BUFFER_SIZE) {
            memcpy(rxBuffer, rxBufferTmp, BUFFER_SIZE);
        } else {
            printf("wrong size = %d\\n", ret);
            for (i = 0; i < ret; i++) {
                printf("%d ", rxBufferTmp[i]);
            }
            printf("\\n");
        }
        /*
        printf("rx:");
        for (i = 0; i < ret; i++) {
            printf(" %d,", rxBuffer[i]);
        }
        printf("\\n");
        */
    } else {
        errCount++;
        printf("Ethernet TIMEOUT: N = %d (ret: %d)\\n", errCount, ret);
    }

    return ret;
}


int udp_tx(uint8_t *txBuffer, uint16_t size) {
    uint16_t ret = 0;
    // Send datagram
    ret = send(udpSocket, txBuffer, BUFFER_SIZE, 0);

    return ret;
}

""")






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

        output.append("void interface_exit(void) {")
        if protocol == "UART":
            output.append("    uart_exit();")
        elif protocol == "SPI":
            output.append("    spi_exit();")
        elif protocol == "UDP":
            output.append("    udp_exit();")
        output.append("}")
        output.append("")












        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"] in self.virtual_pins:
                    pinname = pin_config["pin"].replace(":", "_")
                    if pin_config["direction"] == "output":
                        output.append(f"    wire {pin_config['varname']};")
                        output.append(f"    assign {pinname} = {pin_config['varname']}; // {pin_config['direction']}")
                    elif pin_config["direction"] == "input":
                        output.append(f"    wire {pin_config['varname']};")
                        output.append(f"    assign {pin_config['varname']} = {pinname}; // {pin_config['direction']}")

        # multiplexing
        if self.project.multiplexed_input:
            output.append(f"    reg [{self.project.multiplexed_input_size-1}:0] MULTIPLEXED_INPUT_VALUE;")
            output.append("    reg [7:0] MULTIPLEXED_INPUT_ID;")
        if self.project.multiplexed_output:
            output.append(f"    wire [{self.project.multiplexed_output_size-1}:0] MULTIPLEXED_OUTPUT_VALUE;")
            output.append("    wire [7:0] MULTIPLEXED_OUTPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
            for data_name, data_config in plugin_instance.interface_data().items():
                if not data_config.get("expansion"):
                    variable_name = data_config["variable"]
                    variable_size = data_config["size"]
                    direction = data_config["direction"]
                    multiplexed = data_config.get("multiplexed", False)
                    if variable_size > 1:
                        if multiplexed and direction == "output":
                            output.append(f"uint{variable_size}_t {variable_name} = 0;")
                        else:
                            output.append(f"uint{variable_size}_t {variable_name} = 0;")
                    else:
                        if multiplexed and direction == "output":
                            output.append(f"bool {variable_name} = 0;")
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
            output.append(f"    memcpy(&MULTIPLEXER_INPUT_VALUE, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
            input_pos -= variable_size
            variable_size = 8
            byte_start, byte_size, bit_offset = self.project.get_bype_pos(input_pos, variable_size)
            byte_start = self.project.buffer_bytes - 1 - byte_start
            output.append(f"    memcpy(&MULTIPLEXER_INPUT_ID, &rxBuffer[{byte_start-(byte_size-1)}], {byte_size});")
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
        output_pos -= 32
        # timestamp
        output_pos -= 32

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




        output.append("int main(void) {")
        output.append("")
        
        buffer_init = ["0"] * buffer_size_bytes
        
        output.append(f"    uint8_t rxBuffer[BUFFER_SIZE] = {{{', '.join(buffer_init)}}};")
        output.append(f"    uint8_t txBuffer[BUFFER_SIZE] = {{{', '.join(buffer_init)}}};")
        output.append(f"    uint16_t ret = 0;")
        output.append("")
        output.append("    udp_init();")
        output.append("")
        output.append("")
        output.append("    while (1) {")
        output.append("        ret = udp_rx(rxBuffer, BUFFER_SIZE);")
        output.append("        printf(\"ret = %i\\n\", ret);")
        output.append("")
        output.append("        read_rxbuffer(rxBuffer);")
        output.append("        write_txbuffer(txBuffer);")
        output.append("")
        output.append("        udp_tx(txBuffer, BUFFER_SIZE);")
        output.append("    }")
        output.append("}")
        output.append("")
        output.append("")


        output.append("")
        output.append("")
        print(f"writing firmware to: {self.firmware_path}")
        open(os.path.join(self.firmware_path, "main.c"), "w").write("\n".join(output))

