import glob
import os
import sys
import stat

riocore_path = os.path.dirname(os.path.dirname(__file__))

from riocore.generator.cbase import cbase


class rosbridge(cbase):
    typemap = {
        "float": "float",
        "bool": "uint8_t",
        "s32": "int32_t",
        "u32": "uint32_t",
    }

    def __init__(self, project):
        self.project = project
        self.ros_path = os.path.join(self.project.config["output_path"], "ROS")
        self.base_path = os.path.join(self.ros_path, "src", "rosbridge")
        output = []
        output.append("// Generated by rio-generator")
        header_list = ["ros/ros.h", "std_msgs/String.h", "std_msgs/Float32.h", "sstream", "unistd.h", "stdlib.h", "stdbool.h", "stdio.h", "string.h", "math.h", "sys/mman.h", "errno.h"]
        if "serial":
            header_list += ["fcntl.h", "termios.h"]

        module_info = {
            "AUTHOR": "Oliver Dippel",
            "DESCRIPTION": "Driver for RIO FPGA boards",
            "LICENSE": "GPL v2",
        }

        protocol = self.project.config["jdata"].get("protocol", "SPI")

        ip = "192.168.10.194"
        port = 2390
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.TYPE == "interface":
                ip = plugin_instance.plugin_setup.get("ip", plugin_instance.option_default("ip", ip))
                port = plugin_instance.plugin_setup.get("port", plugin_instance.option_default("port", port))

        ip = self.project.config["jdata"].get("ip", ip)
        port = self.project.config["jdata"].get("port", port)
        dst_port = self.project.config["jdata"].get("dst_port", port)
        src_port = self.project.config["jdata"].get("src_port", str(int(port) + 1))

        defines = {
            "MODNAME": '"rio"',
            "PREFIX": '"rio"',
            "JOINTS": "3",
            "BUFFER_SIZE": self.project.buffer_bytes,
            "OSC_CLOCK": self.project.config["speed"],
        }

        if port and ip:
            defines["UDP_IP"] = f'"{ip}"'
            defines["SRC_PORT"] = src_port
            defines["DST_PORT"] = dst_port
        defines["SERIAL_PORT"] = '"/dev/ttyUSB1"'
        defines["SERIAL_BAUD"] = "B1000000"

        defines["SPI_PIN_MOSI"] = "10"
        defines["SPI_PIN_MISO"] = "9"
        defines["SPI_PIN_CLK"] = "11"
        defines["SPI_PIN_CS"] = "8"  # CE1 = 7
        defines["SPI_SPEED"] = "BCM2835_SPI_CLOCK_DIVIDER_256"

        for header in header_list:
            output.append(f"#include <{header}>")
        output.append("")

        for key, value in defines.items():
            output.append(f"#define {key} {value}")
        output.append("")

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
        output.append(idata)

        output.append("static int 			      comp_id;")
        output.append("static const char 	      *modname = MODNAME;")
        output.append("static const char 	      *prefix = PREFIX;")
        output.append("")
        output.append("uint32_t pkg_counter = 0;")
        output.append("uint32_t err_total = 0;")
        output.append("uint32_t err_counter = 0;")
        output.append("")
        output.append("long stamp_last = 0;")
        output.append("float fpga_stamp_last = 0;")
        output.append("uint32_t fpga_timestamp = 0;")
        output.append("")
        output.append("void rio_readwrite();")
        output.append("int error_handler(int retval);")
        output.append("")

        output += self.rosbridge_variables()

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
                    rdata = open(ppath, "r").read()
                    rdata = rdata.replace("rtapi_print", "printf")
                    rdata = rdata.replace("strerror(errno)", '"error"')
                    rdata = rdata.replace("errno", "1")
                    output.append(rdata)

                    # output.append(open(ppath, "r").read())

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
        output.append("    return 0;")
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

        output.append("")
        output.append("/*")
        output.append("    hal functions")
        output.append("*/")

        output.append(open(os.path.join(riocore_path, "files", "ros_functions.c"), "r").read())

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

        output += self.c_signal_converter()
        output += self.c_buffer_converter()
        output += self.c_buffer()
        output.append("void rio_readwrite() {")
        output.append("    int ret = 0;")
        output.append("    uint8_t i = 0;")
        output.append("    uint8_t rxBuffer[BUFFER_SIZE * 2];")
        output.append("    uint8_t txBuffer[BUFFER_SIZE * 2];")
        output.append("    if (*data->sys_enable_request == 1) {")
        output.append("        *data->sys_status = 1;")
        output.append("    }")
        output.append("    long stamp_new = rtapi_get_time();")
        output.append("    float duration2 = (stamp_new - stamp_last) / 1000.0;")
        output.append("    stamp_last = stamp_new;")

        output.append("    float timestamp = (float)fpga_timestamp / (float)OSC_CLOCK;")
        output.append("    *data->duration = timestamp - fpga_stamp_last;")
        output.append("    fpga_stamp_last = timestamp;")
        # output.append("    printf(\" %f %f  \\n\", duration2, *data->duration);")

        output.append("    if (*data->sys_enable == 1 && *data->sys_status == 1) {")
        output.append("        pkg_counter += 1;")
        output.append("        convert_outputs();")
        output.append("        if (*data->sys_simulation != 1) {")
        output.append("            write_txbuffer(txBuffer);")

        if protocol == "UART":
            output.append("            uart_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        elif protocol == "SPI":
            output.append("            spi_trx(txBuffer, rxBuffer, BUFFER_SIZE);")
        elif protocol == "UDP":
            output.append("            udp_tx(txBuffer, BUFFER_SIZE);")
            output.append("            ret = udp_rx(rxBuffer, BUFFER_SIZE);")
        else:
            print("ERROR: unsupported interface")
            sys.exit(1)

        if protocol == "UDP":
            output.append("            if (ret == BUFFER_SIZE && rxBuffer[0] == 97 && rxBuffer[1] == 116 && rxBuffer[2] == 97 && rxBuffer[3] == 100) {")
        else:
            output.append("            if (rxBuffer[0] == 97 && rxBuffer[1] == 116 && rxBuffer[2] == 97 && rxBuffer[3] == 100) {")
        output.append("                if (err_counter > 0) {")
        output.append("                    err_counter = 0;")
        output.append('                    printf("recovered..\\n");')
        output.append("                }")
        output.append("                read_rxbuffer(rxBuffer);")
        output.append("                convert_inputs();")
        output.append("            } else {")
        output.append("                err_counter += 1;")
        output.append("                err_total += 1;")
        if protocol == "UDP":
            output.append("                if (ret != BUFFER_SIZE) {")
            output.append(
                '                    printf("%i: wrong data size (len %i/%i err %i/3) - (%i %i - %0.4f %%)", stamp_new, ret, BUFFER_SIZE, err_counter, err_total, pkg_counter, (float)err_total * 100.0 / (float)pkg_counter);'
            )
            output.append("                } else {")
            output.append('                    printf("%i: wrong header (%i/3) - (%i %i - %0.4f %%):", stamp_new, err_counter, err_total, pkg_counter, (float)err_total * 100.0 / (float)pkg_counter);')
            output.append("                }")
        else:
            output.append('            printf("wronng data (%i/3): ", err_counter);')
        if protocol == "UDP":
            output.append("                for (i = 0; i < ret; i++) {")
        else:
            output.append("                for (i = 0; i < BUFFER_SIZE; i++) {")
        output.append('                    printf("%d ",rxBuffer[i]);')
        output.append("                }")
        output.append('                printf("\\n");')
        output.append("                if (err_counter > 3) {")
        output.append('                    printf("too many errors..\\n");')
        output.append("                    *data->sys_status = 0;")
        output.append("                }")
        output.append("            }")
        output.append("        } else {")
        output.append("            convert_inputs();")
        output.append("        }")
        output.append("    } else {")
        output.append("        *data->sys_status = 0;")
        output.append("    }")
        output.append("}")
        output.append("")
        output.append("")

        self.rosbridge_path = os.path.join(self.base_path, "src")
        os.makedirs(self.rosbridge_path, exist_ok=True)
        open(os.path.join(self.rosbridge_path, "rosbridge.cpp"), "w").write("\n".join(output))

        output = []
        output.append("cmake_minimum_required(VERSION 3.0.2)")
        output.append("project(riobridge)")
        output.append("")
        output.append("find_package(catkin REQUIRED COMPONENTS")
        output.append("  roscpp")
        output.append("  rospy")
        output.append("  std_msgs")
        output.append(")")
        output.append("")
        output.append("catkin_package(")
        output.append(")")
        output.append("")
        output.append("include_directories(")
        output.append("  ${catkin_INCLUDE_DIRS}")
        output.append(")")
        output.append("")
        output.append("add_executable(rosbridge src/rosbridge.cpp)")
        output.append("target_link_libraries(rosbridge ${catkin_LIBRARIES})")
        output.append("")
        open(os.path.join(self.base_path, "CMakeLists.txt"), "w").write("\n".join(output))

        output = ['<?xml version="1.0"?>']
        output.append('<package format="2">')
        output.append("  <name>riobridge</name>")
        output.append("  <version>0.0.0</version>")
        output.append(f"  <description>{module_info['DESCRIPTION']}</description>")
        output.append(f'  <maintainer email="odippel@gmx.de">{module_info["AUTHOR"]}</maintainer>')
        output.append(f"  <license>{module_info['LICENSE']}</license>")
        output.append("  <buildtool_depend>catkin</buildtool_depend>")
        output.append("  <build_depend>roscpp</build_depend>")
        output.append("  <build_depend>rospy</build_depend>")
        output.append("  <build_depend>std_msgs</build_depend>")
        output.append("  <build_export_depend>roscpp</build_export_depend>")
        output.append("  <build_export_depend>rospy</build_export_depend>")
        output.append("  <build_export_depend>std_msgs</build_export_depend>")
        output.append("  <exec_depend>roscpp</exec_depend>")
        output.append("  <exec_depend>rospy</exec_depend>")
        output.append("  <exec_depend>std_msgs</exec_depend>")
        output.append("  <export></export>")
        output.append("</package>")
        open(os.path.join(self.base_path, "package.xml"), "w").write("\n".join(output))

        self.rosbridge_startscript()

    def rosbridge_startscript(self):
        jdata = self.project.config["jdata"]
        startup = jdata.get("startup")
        output = ["#!/bin/sh"]
        output.append("")
        output.append("set -e")
        output.append("set -x")
        output.append("")
        output.append('DIRNAME=`dirname "$0"`')
        output.append("")
        output.append('echo "compile package:"')
        output.append('(cd "$DIRNAME" && catkin_make)')
        output.append("")
        output.append('echo "running rosbridge:"')
        output.append("$DIRNAME/devel/lib/riobridge/rosbridge")
        output.append("")
        output.append("")
        os.makedirs(self.ros_path, exist_ok=True)
        target = os.path.join(self.ros_path, "start.sh")
        open(target, "w").write("\n".join(output))
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def rosbridge_variables(self):
        output = []
        output.append("// Generated by rosbridge_variables()")
        output.append("typedef struct {")
        output.append("    // hal variables")
        output.append("    uint8_t   *sys_enable;")
        output.append("    uint8_t   *sys_enable_request;")
        output.append("    uint8_t   *sys_status;")
        output.append("    uint8_t   *sys_simulation;")
        output.append("    uint32_t   *fpga_timestamp;")
        output.append("    float *duration;")

        if self.project.multiplexed_output:
            output.append("    float MULTIPLEXER_OUTPUT_VALUE;")
            output.append("    uint8_t MULTIPLEXER_OUTPUT_ID;")
        if self.project.multiplexed_input:
            output.append("    float MULTIPLEXER_INPUT_VALUE;")
            output.append("    uint8_t MULTIPLEXER_INPUT_ID;")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                var_prefix = signal_config["var_prefix"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                signal_source = signal_config.get("source")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                vtype = self.typemap.get(hal_type, hal_type)
                virtual = signal_config.get("virtual")
                component = signal_config.get("component")
                if virtual and component:
                    # swap direction vor virt signals in component
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                elif virtual:
                    continue
                if not boolean:
                    output.append(f"    {vtype} *{varname};")
                    if not signal_source and not signal_config.get("helper", False):
                        if direction == "input" and vtype == "float":
                            output.append(f"    {vtype} *{varname}_ABS;")
                            output.append(f"    int32_t *{varname}_S32;")
                            output.append(f"    uint32_t *{varname}_U32_ABS;")
                        if not virtual:
                            output.append(f"    float *{varname}_SCALE;")
                            output.append(f"    float *{varname}_OFFSET;")
                else:
                    output.append(f"    uint8_t   *{varname};")
                    if direction == "input":
                        output.append(f"    uint8_t   *{varname}_not;")
                    if signal_config.get("is_index_out"):
                        output.append(f"    uint8_t   *{var_prefix}_INDEX_RESET;")
                        output.append(f"    uint8_t   *{var_prefix}_INDEX_WAIT;")

        output.append("    // raw variables")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            expansion = data_config.get("expansion", False)
            if expansion:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            variable_bytesize = variable_size // 8
            if plugin_instance.TYPE == "frameio":
                output.append(f"    uint8_t {variable_name}[{variable_bytesize}];")
            elif variable_size > 1:
                variable_size_align = 8
                for isize in (8, 16, 32, 64):
                    variable_size_align = isize
                    if isize >= variable_size:
                        break
                output.append(f"    int{variable_size_align}_t {variable_name};")
            else:
                output.append(f"    uint8_t {variable_name};")
        output.append("")
        output.append("} data_t;")
        output.append("static data_t *data;")
        output.append("")

        output.append("void register_signals(void) {")
        output.append("    int retval = 0;")

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            expansion = data_config.get("expansion", False)
            if expansion:
                continue
            variable_name = data_config["variable"]
            variable_size = data_config["size"]
            variable_bytesize = variable_size // 8
            if plugin_instance.TYPE == "frameio":
                output.append(f"    memset(&data->{variable_name}, 0, {variable_bytesize});")
            elif variable_size > 1:
                output.append(f"    data->{variable_name} = 0;")
            else:
                output.append(f"    data->{variable_name} = 0;")
        output.append("")

        output.append("    data->sys_status = (uint8_t*)malloc(sizeof(uint8_t));")
        output.append("    data->sys_enable = (uint8_t*)malloc(sizeof(uint8_t));")
        output.append("    data->sys_enable_request = (uint8_t*)malloc(sizeof(uint8_t));")
        output.append("    data->sys_simulation = (uint8_t*)malloc(sizeof(uint8_t));")
        output.append("    data->duration = (float*)malloc(sizeof(float));")
        output.append("    *data->duration = rtapi_get_time();")
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                varname = signal_config["varname"]
                var_prefix = signal_config["var_prefix"]
                boolean = signal_config.get("bool")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                vtype = self.typemap.get(hal_type, hal_type)
                signal_source = signal_config.get("source")
                mapping = {"output": "IN", "input": "OUT", "inout": "IO"}
                hal_direction = mapping[direction]
                virtual = signal_config.get("virtual")
                component = signal_config.get("component")
                if virtual and component:
                    # swap direction vor virt signals in component
                    if direction == "input":
                        direction = "output"
                    else:
                        direction = "input"
                    hal_direction = mapping[direction]
                elif virtual:
                    continue
                if not boolean:
                    if not signal_source and not signal_config.get("helper", False) and not virtual:
                        output.append(f"    data->{varname}_SCALE = (float*)malloc(sizeof(float));")
                        output.append(f"    *data->{varname}_SCALE = 1.0;")
                        output.append(f"    data->{varname}_OFFSET = (float*)malloc(sizeof(float));")
                        output.append(f"    *data->{varname}_OFFSET = 0.0;")
                    output.append(f"    data->{varname} = ({vtype}*)malloc(sizeof({vtype}));")
                    output.append(f"    *data->{varname} = 0;")
                    if direction == "input" and hal_type == "float" and not signal_source and not signal_config.get("helper", False):
                        output.append(f"    data->{varname}_ABS = (float*)malloc(sizeof(float));")
                        output.append(f"    *data->{varname}_ABS = 0.0;")
                        output.append(f"    data->{varname}_S32 = (int32_t*)malloc(sizeof(int32_t));")
                        output.append(f"    *data->{varname}_S32 = 0;")
                        output.append(f"    data->{varname}_U32_ABS = (uint32_t*)malloc(sizeof(uint32_t));")
                        output.append(f"    *data->{varname}_U32_ABS = 0;")
                else:
                    output.append(f"    data->{varname} = (uint8_t*)malloc(sizeof(uint8_t));")
                    output.append(f"    *data->{varname} = 0;")

                    if direction == "input":
                        output.append(f"    data->{varname}_not = (uint8_t*)malloc(sizeof(uint8_t));")
                        output.append(f"    *data->{varname}_not = 1;")

                    if signal_config.get("is_index_out"):
                        output.append(f"    data->{var_prefix}_INDEX_RESET = (uint8_t*)malloc(sizeof(uint8_t));")
                        output.append(f"    *data->{var_prefix}_INDEX_RESET = 0;")
                        output.append(f"    data->{var_prefix}_INDEX_WAIT = (uint8_t*)malloc(sizeof(uint8_t));")
                        output.append(f"    *data->{var_prefix}_INDEX_WAIT = 0;")

        output.append("}")
        output.append("")
        return output
