import glob
import sys
import os
from riocore.generator import cclient

riocore_path = os.path.dirname(os.path.dirname(__file__))


class Simulator:
    def __init__(self, project):
        self.project = project
        self.simulator_path = os.path.join(project.config["output_path"], "Simulator")
        os.makedirs(self.simulator_path, exist_ok=True)
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

        cclient.riocore_h(self.project, self.simulator_path)
        cclient.riocore_c(self.project, self.simulator_path)
        self.interface_c()
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
                    open(os.path.join(self.simulator_path, "interface.c"), "w").write(idata)

    def simulation_c(self):
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

        output.append("")
        output.append('    printf("\\n\\n");')
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            # multiplexed = data_config.get("multiplexed", False)
            # expansion = data_config.get("expansion", False)
            variable_name = data_config["variable"]
            if data_config["direction"] == "output":
                output.append(f'    printf("> {plugin_instance.instances_name}.{data_name} %i\\n", {variable_name});')
        output.append('    printf("\\n");')
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            # multiplexed = data_config.get("multiplexed", False)
            # expansion = data_config.get("expansion", False)
            variable_name = data_config["variable"]
            if data_config["direction"] == "input":
                output.append(f'    printf("< {plugin_instance.instances_name}.{data_name} %i\\n", {variable_name});')
        output.append("}")
        output.append("")

        output.append("int main(void) {")
        output.append("    uint16_t ret = 0;")
        output.append("")
        output.append("    interface_init();")
        output.append("")
        output.append("    while (1) {")
        output.append("        ret = udp_rx(rxBuffer, BUFFER_SIZE);")
        output.append("        if (ret == BUFFER_SIZE && rxBuffer[0] == 0x74 && rxBuffer[1] == 0x69 && rxBuffer[2] == 0x72 && rxBuffer[3] == 0x77) {")
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
        open(os.path.join(self.simulator_path, "simulator.c"), "w").write("\n".join(output))

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
        open(os.path.join(self.simulator_path, "Makefile"), "w").write("\n".join(output))
