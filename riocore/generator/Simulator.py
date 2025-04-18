import glob
import sys
import os
import stat
import shutil

from riocore.generator import cclient

riocore_path = os.path.dirname(os.path.dirname(__file__))


class Simulator:
    def __init__(self, project):
        self.project = project
        self.webots_home = "/usr/local/webots"
        self.webots = False
        self.glsim = False
        self.simulator_path = os.path.join(project.config["output_path"], "Simulator")
        os.makedirs(self.simulator_path, exist_ok=True)
        project.config["riocore_path"] = riocore_path

    def generator(self, generate_pll=True):
        self.config = self.project.config.copy()
        jdata = self.config["jdata"]
        linuxcnc_config = jdata.get("linuxcnc", {})
        machinetype = linuxcnc_config.get("machinetype", "mill")

        if machinetype in {"melfa"}:
            self.webots = True
            self.glsim = True
            source = os.path.join(riocore_path, "", "generator", "glsim", f"webots-{machinetype}.c")
            target = os.path.join(self.simulator_path, "glsim.c")
            shutil.copy(source, target)
        elif machinetype in {"mill", "corexy", "melfa"}:
            self.glsim = True
            source = os.path.join(riocore_path, "", "generator", "glsim", f"{machinetype}.c")
            target = os.path.join(self.simulator_path, "glsim.c")
            shutil.copy(source, target)

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
        self.simulation_h()
        self.main_c()
        self.makefile()
        self.startscript()

    def startscript(self):
        output = ["#!/bin/sh"]
        output.append("")
        output.append("set -e")
        output.append("set -x")
        output.append("")
        output.append('DIRNAME=`dirname "$0"`')
        output.append("")
        if self.webots:
            # output.append(f"export WEBOTS_HOME={self.webots_home}")
            # output.append(f"export LD_LIBRARY_PATH={self.webots_home}/lib/controller/")
            output.append("")
        output.append("(")
        output.append('    cd "$DIRNAME/"')
        output.append("    make simulator_run")
        output.append(")")
        output.append("")
        output.append("")
        os.makedirs(self.simulator_path, exist_ok=True)
        target = os.path.join(self.simulator_path, "start.sh")
        open(target, "w").write("\n".join(output))
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

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

    def simulation_h(self):
        output = []
        output.append("#include <stdint.h>")
        output.append("")
        output.append(f"#define NUM_JOINTS {self.joints}")
        output.append(f"#define NUM_HOMESWS {self.homes}")
        output.append(f"#define NUM_BITOUTS {self.bitouts}")
        output.append("")
        output.append("extern uint8_t sim_running;")
        output.append("")
        output.append("extern volatile int32_t joint_position[NUM_JOINTS];")
        output.append("extern volatile int32_t home_switch[NUM_HOMESWS];")
        output.append("extern volatile int32_t bitout_stat[NUM_BITOUTS];")
        output.append("")

        for axis, data in self.project.axis_dict.items():
            joints = list(data.get("joints", {}))
            output.append(f"#define NUM_JOINTS_{axis} {len(joints)}")
        output.append("")

        for axis, data in self.project.axis_dict.items():
            joints = list(data.get("joints", {}))
            output.append(f"#define NUM_JOINTS_{axis} {len(joints)}")
            output.append(f"extern int {axis.lower()}_joints[NUM_JOINTS_{axis}];")
        output.append("")

        output.append("void* simThread(void* vargp);")
        open(os.path.join(self.simulator_path, "simulator.h"), "w").write("\n".join(output))

    def simulation_c(self):
        jdata = self.config["jdata"]
        linuxcnc_config = jdata.get("linuxcnc", {})
        machinetype = linuxcnc_config.get("machinetype", "mill")

        output = []
        output.append("#include <stdio.h>")
        output.append("#include <stdint.h>")
        output.append("#include <stdbool.h>")
        output.append("#include <string.h>")
        output.append("#include <simulator.h>")
        output.append("#include <riocore.h>")
        output.append("")
        output.append("uint8_t sim_running = 1;")
        output.append("")

        protocol = self.project.config["jdata"].get("protocol", "SPI")

        output.append("int udp_init(const char *dstAddress, int dstPort, int srcPort);")
        output.append("void udp_tx(uint8_t *txBuffer, uint16_t size);")
        output.append("int udp_rx(uint8_t *rxBuffer, uint16_t size);")
        output.append("void udp_exit();")
        output.append("")

        output.append("volatile int32_t joint_position[NUM_JOINTS];")
        output.append("volatile int32_t home_switch[NUM_HOMESWS];")
        output.append("volatile int32_t bitout_stat[NUM_BITOUTS];")
        output.append("")

        for axis, data in self.project.axis_dict.items():
            joints = list(data.get("joints", {}))
            output.append(f"int {axis.lower()}_joints[NUM_JOINTS_{axis}] = {{{', '.join([str(j) for j in joints])}}};")
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

        joint_n = 0
        output.append("void simulation(void) {")
        output.append("    float offset = 0.0;")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            interface_data = plugin_instance.interface_data()
            signal_config = plugin_instance.signals().get(data_name, {})
            if plugin_instance.TYPE == "joint" and data_config["direction"] == "input" and data_name == "position":
                position_var = interface_data["position"]["variable"]
                if "velocity" in interface_data:
                    enable_var = interface_data.get("enable", {}).get("variable", "1")
                    velocity_var = interface_data["velocity"]["variable"]
                    output.append(f"    if ({enable_var} == 1 && {velocity_var} != 0) {{")
                    output.append(f"        offset = ((float)CLOCK_SPEED / (float){velocity_var} / 2.0) / 1000.0;")
                    output.append("        // for testing")
                    output.append("        if ((int32_t)offset == 0 && offset > 0.0) {")
                    output.append("            offset = 1.0;")
                    output.append("        } else if ((int32_t)offset == 0 && offset < 0.0) {")
                    output.append("            offset = -1.0;")
                    output.append("        }")
                    output.append(f"        {position_var} += (int32_t)offset;")
                    output.append("    }")
                output.append(f"    joint_position[{joint_n}] = {position_var};")
                joint_n += 1

        self.joints = joint_n

        home_n = 0
        bitout_n = 0
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            interface_data = plugin_instance.interface_data()
            signal_config = plugin_instance.signals().get(data_name, {})
            userconfig = signal_config.get("userconfig", {})
            net = userconfig.get("net")
            if data_config["direction"] == "input":
                if net and net.startswith("joint.") and net.endswith(".home-sw-in"):
                    jn = net.split(".")[1]
                    var = interface_data["bit"]["variable"]
                    if self.project.axis_dict.get("Z", {}).get("joints", {}).get(int(jn)) and machinetype not in {"melfa", "melfa_nogl"}:
                        # Z-Axis
                        output.append(f"    if (joint_position[{jn}] > 2000.0) {{")
                    else:
                        output.append(f"    if (joint_position[{jn}] < 0.0) {{")
                    output.append(f"        {var} = 1;")
                    output.append("    } else {")
                    output.append(f"        {var} = 0;")
                    output.append("    }")
                    output.append(f"    home_switch[{home_n}] = {var};")
                    home_n += 1
            if data_config["direction"] == "output":
                if data_name == "bit":
                    var = interface_data["bit"]["variable"]
                    output.append(f"    bitout_stat[{bitout_n}] = {var};")
                    bitout_n += 1

        self.homes = home_n
        self.bitouts = bitout_n

        output.append("")
        output.append('    printf("\\n\\n");')
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            # multiplexed = data_config.get("multiplexed", False)
            # expansion = data_config.get("expansion", False)
            variable_name = data_config["variable"]
            if data_config["direction"] == "output":
                if plugin_instance.TYPE != "frameio":
                    output.append(f'    printf("> {plugin_instance.instances_name}.{data_name} %i\\n", {variable_name});')
        output.append('    printf("\\n");')
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            # multiplexed = data_config.get("multiplexed", False)
            # expansion = data_config.get("expansion", False)
            variable_name = data_config["variable"]
            if data_config["direction"] == "input":
                if plugin_instance.TYPE != "frameio":
                    output.append(f'    printf("< {plugin_instance.instances_name}.{data_name} %i\\n", {variable_name});')
        output.append("}")
        output.append("")

        output.append("void* simThread(void* vargp) {")
        output.append("    uint16_t ret = 0;")
        output.append("")
        output.append("    interface_init();")
        output.append("")
        output.append("    while (sim_running) {")
        output.append("        ret = udp_rx(rxBuffer, BUFFER_SIZE);")
        output.append("        if (ret == BUFFER_SIZE && rxBuffer[0] == 0x74 && rxBuffer[1] == 0x69 && rxBuffer[2] == 0x72 && rxBuffer[3] == 0x77) {")
        output.append("            read_rxbuffer(rxBuffer);")
        output.append("            write_txbuffer(txBuffer);")
        output.append("            udp_tx(txBuffer, BUFFER_SIZE);")
        output.append("")
        output.append("            simulation();")
        output.append("        }")
        output.append("    }")
        output.append("    return NULL;")
        output.append("}")
        output.append("")
        open(os.path.join(self.simulator_path, "simulator.c"), "w").write("\n".join(output))

    def main_c(self):
        output = []
        output.append("#include <pthread.h>")
        output.append("#include <simulator.h>")
        output.append("")
        output.append("int glsim_run(int argc, char** argv);")
        output.append("")
        output.append("int main(int argc, char** argv) {")
        output.append("    pthread_t thread_id;")
        output.append("    pthread_create(&thread_id, NULL, simThread, NULL);")
        output.append("")
        if self.glsim:
            output.append("    glsim_run(argc, argv);")
        else:
            output.append("    while(1) {}")

        output.append("    sim_running = 0;")
        output.append("    pthread_join(thread_id, NULL);")
        output.append("    return 0;")
        output.append("}")
        output.append("")
        open(os.path.join(self.simulator_path, "main.c"), "w").write("\n".join(output))

    def makefile(self):
        output = []
        gcc_options = ""

        if self.webots:
            output.append("")
            output.append(f"WEBOTS_HOME ?= {self.webots_home}")
            output.append("LD_LIBRARY_PATH ?= $(WEBOTS_HOME)/lib/controller/")
            output.append("")
            gcc_options = "-I$(WEBOTS_HOME)/include/controller/c/ -L$(WEBOTS_HOME)/lib/controller/ -lController"

        output.append("")
        output.append("all: simulator")
        output.append("")
        output.append("clean:")
        output.append("	rm -f simulator")
        output.append("")
        if self.glsim:
            output.append("simulator: main.c simulator.c glsim.c riocore.c interface.c")
            output.append(f"	gcc -o simulator -Os -I. main.c simulator.c glsim.c riocore.c interface.c {gcc_options} -lm -lGL -lGLU -lglut")
        else:
            output.append("simulator: main.c simulator.c riocore.c interface.c")
            output.append(f"	gcc -o simulator -Os -I. main.c simulator.c riocore.c interface.c {gcc_options} -lm")
        output.append("")
        output.append("simulator_run: simulator")
        if self.webots:
            output.append("	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH) WEBOTS_HOME=$(WEBOTS_HOME) ./simulator")
        else:
            output.append("	./simulator")
        output.append("")
        open(os.path.join(self.simulator_path, "Makefile"), "w").write("\n".join(output))
