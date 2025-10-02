import os
import stat
from riocore.generator.cbase import cbase

riocore_path = os.path.dirname(os.path.dirname(__file__))


class rosbridge(cbase):
    filename_functions = "ros_functions.c"
    rtapi_mode = False
    typemap = {
        "float": "float",
        "bool": "bool",
        "s32": "int32_t",
        "u32": "uint32_t",
    }
    printf = "printf"
    prefix = "/rio"
    header_list = [
        "ros/ros.h",
        "std_msgs/String.h",
        "std_msgs/Float32.h",
        "std_msgs/Bool.h",
        "time.h",
        "sstream",
        "unistd.h",
        "stdlib.h",
        "stdbool.h",
        "stdio.h",
        "string.h",
        "math.h",
        "sys/mman.h",
        "errno.h",
    ]
    module_info = {
        "AUTHOR": "Oliver Dippel",
        "DESCRIPTION": "Driver for RIO FPGA boards",
        "LICENSE": "GPL v2",
    }

    def __init__(self, project):
        self.project = project
        self.ros_path = os.path.join(self.project.config["output_path"], "ROS")
        self.base_path = os.path.join(self.ros_path, "src", "rosbridge")

        self.rosbridge_path = os.path.join(self.base_path, "src")
        os.makedirs(self.rosbridge_path, exist_ok=True)

        self.ros_cmake()
        self.ros_package()

        output = self.mainc(project)
        output += self.ros_functions()

        open(os.path.join(self.rosbridge_path, "rosbridge.cpp"), "w").write("\n".join(output))

    def ros_cmake(self):
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

    def ros_package(self):
        output = ['<?xml version="1.0"?>']
        output.append('<package format="2">')
        output.append("  <name>riobridge</name>")
        output.append("  <version>0.0.0</version>")
        output.append(f"  <description>{self.module_info['DESCRIPTION']}</description>")
        output.append(f'  <maintainer email="odippel@gmx.de">{self.module_info["AUTHOR"]}</maintainer>')
        output.append(f"  <license>{self.module_info['LICENSE']}</license>")
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

    def ros_functions(self):
        output = []
        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if not boolean:
                    rtype = "Float32"
                else:
                    rtype = "Bool"
                if direction == "output":
                    output.append(f"void cb_{varname}(const std_msgs::{rtype}::ConstPtr& msg) {{")
                    output.append(f"    *data->{varname} = msg->data;")
                    output.append("}")
                    output.append("")

        output.append("")

        output.append("int main(int argc, char **argv) {")
        output.append("")
        output.append('    ros::init(argc, argv, "riobridge");')
        output.append("")
        output.append("    data = (data_t*)malloc(sizeof(data_t));")
        output.append("    register_signals();")
        output.append("    interface_init();")
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if not boolean:
                    rtype = "Float32"
                else:
                    rtype = "Bool"
                output.append(f"    ros::NodeHandle n{varname};")
                if direction == "input":
                    output.append(f"    std_msgs::{rtype} msg_{varname};")
                    output.append(f'    ros::Publisher pub_{varname} = n{varname}.advertise<std_msgs::{rtype}>("{self.rosname(halname)}", 1000);')
                else:
                    output.append(f'    ros::Subscriber sub_{varname} = n{varname}.subscribe("{self.rosname(halname)}", 1000, cb_{varname});')

        output.append("")
        output.append("")
        output.append("    ros::Rate loop_rate(10);")
        output.append("")
        output.append("    while (ros::ok()) {")
        output.append("        rio_readwrite(NULL, 0);")
        output.append("")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                varname = signal_config["varname"]
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if not boolean:
                    rtype = "Float32"
                else:
                    rtype = "Bool"
                if direction == "input":
                    output.append(f"        msg_{varname}.data = *data->{varname};")
                    output.append(f"        pub_{varname}.publish(msg_{varname});")
                    output.append("")

        output.append("")
        output.append("        ros::spinOnce();")
        output.append("        loop_rate.sleep();")
        output.append("    }")
        output.append("")
        output.append("    return 0;")
        output.append("}")
        output.append("")
        return output

    def rosbridge_startscript(self):
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

    def rosname(self, halname):
        rosname = halname.replace(".", "/").replace("-", "_")
        return f"{self.prefix}/{rosname}"

    def vinit(self, vname, vtype, halstr=None, vdir="input"):
        vtype = self.typemap.get(vtype, vtype)
        return f"    data->{vname} = ({vtype}*)malloc(sizeof({vtype}));"
