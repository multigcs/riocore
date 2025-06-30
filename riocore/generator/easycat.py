import os
import stat
from riocore.generator.cbase import cbase

riocore_path = os.path.dirname(os.path.dirname(__file__))


class easycat(cbase):
    filename_functions = None
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
        "time.h",
        "unistd.h",
        "stdint.h",
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

    def variables_init(self):
        output = []

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

        # output.append(self.vinit("sys_status", "bool", "sys-status", "input"))
        # output.append(self.vinit("sys_enable", "bool", "sys-enable", "output"))
        # output.append(self.vinit("sys_enable_request", "bool", "sys-enable-request", "output"))
        output.append(self.vinit("sys_simulation", "bool", "sys-simulation", "output", True))
        output.append("*data->sys_simulation = 1;")
        output.append(self.vinit("duration", "float", "duration", "input", True))
        output.append("    *data->duration = 0;")

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                halname = signal_config["halname"]
                direction = signal_config["direction"]
                varname = signal_config["varname"]
                var_prefix = signal_config["var_prefix"]
                boolean = signal_config.get("bool")
                hal_type = signal_config.get("userconfig", {}).get("hal_type", signal_config.get("hal_type", "float"))
                signal_source = signal_config.get("source")
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                if not boolean:
                    if not signal_source and not signal_config.get("helper", False) and not virtual:
                        output.append(self.vinit(f"{varname}_SCALE", "float", f"{halname}-scale", "output"))
                        output.append(f"    *data->{varname}_SCALE = 1.0;")
                        output.append(self.vinit(f"{varname}_OFFSET", "float", f"{halname}-offset", "output"))
                        output.append(f"    *data->{varname}_OFFSET = 0.0;")
                    output.append(self.vinit(varname, "float", halname, direction))
                    output.append(f"    *data->{varname} = 0;")
                    if direction == "input" and hal_type == "float" and not signal_source and not signal_config.get("helper", False):
                        output.append(self.vinit(f"{varname}_ABS", "float", f"{halname}-abs", direction))
                        output.append(f"    *data->{varname}_ABS = 0;")
                        output.append(self.vinit(f"{varname}_S32", "s32", f"{halname}-s32", direction))
                        output.append(f"    *data->{varname}_S32 = 0;")
                        output.append(self.vinit(f"{varname}_U32_ABS", "u32", f"{halname}-u32-abs", direction))
                        output.append(f"    *data->{varname}_U32_ABS = 0;")
                else:
                    output.append(self.vinit(varname, "bool", halname, direction))
                    output.append(f"    *data->{varname} = 0;")
                    if direction == "input":
                        output.append(self.vinit(f"{varname}_not", "bool", f"{halname}-not", direction))
                        output.append(f"    *data->{varname}_not = 1 - *data->{varname};")
                    if signal_config.get("is_index_out"):
                        output.append(self.vinit(f"{varname}_INDEX_RESET", "bool", f"{halname}-reset", direction))
                        output.append(f"    *data->{var_prefix}_INDEX_RESET = 0;")
                        output.append(self.vinit(f"{varname}_INDEX_WAIT", "bool", f"{halname}-wait", direction))
                        output.append(f"    *data->{var_prefix}_INDEX_WAIT = 0;")

        output.append("}")
        output.append("")
        return output

    def __init__(self, project):
        self.project = project
        self.easycat_path = os.path.join(self.project.config["output_path"], "EASYCAT")
        self.easycat_src_path = os.path.join(self.easycat_path, "src")
        self.easycat_lib_path = os.path.join(self.easycat_path, "lib")
        self.linuxcnc_path = os.path.join(self.project.config["output_path"], "LinuxCNC")
        os.makedirs(self.easycat_path, exist_ok=True)
        os.makedirs(self.easycat_src_path, exist_ok=True)
        os.makedirs(self.easycat_lib_path, exist_ok=True)
        os.makedirs(self.linuxcnc_path, exist_ok=True)

        self.easycat_makefile()
        self.easycat_esi()
        self.easycat_conf()
        self.platformio_ini()

        # output = self.mainc(project)

        output = [""]
        output += self.easycat_functions()
        output += self.variables()
        output += self.variables_init()

        output += self.c_signal_converter()
        output += self.c_buffer_converter()
        output += self.c_buffer()
        output += [
            """
unsigned long Millis = 0;
unsigned long PreviousMillis = 0;

void setup() {
    Serial.begin(9600);
    delay(1000);
    Serial.println("EasyCAT - Generic EtherCAT slave");

    data = (data_t*)malloc(sizeof(data_t));
    register_signals();

    if (EASYCAT.Init() == true) {
        Serial.print ("initialized");
    } else {
        Serial.print ("initialization failed");
    } 
    PreviousMillis = millis();
}

void loop() {
    EASYCAT.MainTask();
    Millis = millis();
    if (Millis - PreviousMillis >= 2) {
        PreviousMillis = Millis;
        convert_outputs();
        convert_inputs();
    }   
}

"""
        ]

        open(os.path.join(self.easycat_src_path, "main.ino"), "w").write("\n".join(output))

    def platformio_ini(self):
        output = [""]
        output.append("[env:genericSTM32F446RE]")
        output.append("framework = arduino")
        output.append("platform = ststm32")
        output.append("board = nucleo_f446re")
        output.append("upload_protocol = mbed")
        output.append("")
        open(os.path.join(self.easycat_path, "platformio.ini"), "w").write("\n".join(output))

    def easycat_conf(self):
        output = [
            """<masters>
 <master idx="0" appTimePeriod="1000000" refClockSyncCycles="1">
   <slave idx="0" type="generic" vid="0000079a" pid="defede16" configPdos="true" name="rio">
"""
        ]

        floats = {
            "input": [],
            "output": [],
        }
        bits = {
            "input": [],
            "output": [],
        }

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                halname = signal_config["halname"]
                if not boolean:
                    floats[direction].append(halname)
                    floats["output"].append(f"{halname}-scale")
                else:
                    bits[direction].append(halname)

        output.append("""
    <syncManager idx="1" dir="in">
     <pdo idx="0x1a00">
        """)
        subidx = 0
        for subidx, halname in enumerate(floats["input"], 1):
            output.append(f"""      <pdoEntry idx="0005" subIdx="{subidx}" bitLen="32" halPin="{halname}" halType="float-ieee"/>""")
        for subidx, halname in enumerate(bits["input"], subidx):
            output.append(f"""      <pdoEntry idx="0005" subIdx="{subidx}" bitLen="1" halPin="{halname}" halType="bit"/>""")
        output.append("     </pdo>")
        output.append("    </syncManager>")

        output.append("""
    <syncManager idx="0" dir="out">
     <pdo idx="0x1600">
        """)
        for subidx, halname in enumerate(floats["output"], 1):
            output.append(f"""     <pdoEntry idx="0006" subIdx="{subidx}" bitLen="32" halPin="{halname}" halType="float-ieee"/>""")
        for subidx, halname in enumerate(bits["output"], subidx):
            output.append(f"""     <pdoEntry idx="0006" subIdx="{subidx}" bitLen="1" halPin="{halname}" halType="bit"/>""")
        output.append("     </pdo>")
        output.append("    </syncManager>")

        output.append("""
   </slave>
 </master>
</masters>""")

        open(os.path.join(self.linuxcnc_path, "ethercat-conf.xml"), "w").write("\n".join(output))

    def easycat_esi(self):
        output = [
            """<?xml version="1.0"?>
<EtherCATInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="EtherCATInfo.xsd" Version="1.6">
  <Vendor>
    <Id>#x0000079A</Id>
    <Name>RIO</Name>
  </Vendor> 
  <Descriptions>
    <Groups>
      <Group SortOrder="0">
        <Type>SSC_Device</Type>
        <Name LcId="1033">RIO</Name>
      </Group>
    </Groups>
    <Devices>
      <Device Physics="YY">
        <Type ProductCode="#xDEFEDE16" RevisionNo="#x00005A01">RIO-Ethercat</Type>
        <Name LcId="1033">RIO</Name>
        <GroupType>SSC_Device</GroupType>
        <Fmmu>Outputs</Fmmu>
        <Fmmu>Inputs</Fmmu>
        <Sm StartAddress="#x1000" ControlByte="#x64" Enable="1">Outputs</Sm>
        <Sm StartAddress="#x1200" ControlByte="#x20" Enable="1">Inputs</Sm>
"""
        ]

        floats = {
            "input": [],
            "output": [],
        }
        bits = {
            "input": [],
            "output": [],
        }

        for plugin_instance in self.project.plugin_instances:
            for signal_name, signal_config in plugin_instance.signals().items():
                virtual = signal_config.get("virtual")
                if virtual:
                    continue
                direction = signal_config["direction"]
                boolean = signal_config.get("bool")
                halname = signal_config["halname"]
                if not boolean:
                    floats[direction].append(halname)
                else:
                    bits[direction].append(halname)

        output.append("""
            <TxPdo Fixed="1" Mandatory="1" Sm="1">
              <Index>#x1A00</Index>
              <Name>Inputs</Name>""")
        subidx = 0
        for subidx, halname in enumerate(floats["input"], 1):
            output.append(f"""
              <Entry>
                <Index>#x0005</Index>
                <SubIndex>{subidx}</SubIndex>
                <BitLen>32</BitLen>
                <Name>{halname}</Name>
                <DataType>UNDEF</DataType>
              </Entry>""")
        for subidx, halname in enumerate(bits["input"], subidx):
            output.append(f"""
              <Entry>
                <Index>#x0005</Index>
                <SubIndex>{subidx}</SubIndex>
                <BitLen>1</BitLen>
                <Name>{halname}</Name>
                <DataType>BOOL</DataType>
              </Entry>""")
        output.append("            </TxPdo>")

        output.append("""
            <RxPdo Fixed="1" Mandatory="1" Sm="0">
              <Index>#x1600</Index>
              <Name>Outputs</Name>""")
        for subidx, halname in enumerate(floats["output"], 1):
            output.append(f"""
              <Entry>
                <Index>#x0006</Index>
                <SubIndex>{subidx}</SubIndex>
                <BitLen>32</BitLen>
                <Name>{halname}</Name>
                <DataType>UNDEF</DataType>
              </Entry>""")
        for subidx, halname in enumerate(bits["output"], subidx):
            output.append(f"""
              <Entry>
                <Index>#x0006</Index>
                <SubIndex>{subidx}</SubIndex>
                <BitLen>1</BitLen>
                <Name>{halname}</Name>
                <DataType>BOOL</DataType>
              </Entry>""")
        output.append("            </RxPdo>")

        output.append("""
        <Dc>
            <OpMode>                                          
                <Name>SM_Sync or Async</Name>
                <Desc>SM_Sync or Async</Desc>            
                <AssignActivate>#x0000</AssignActivate>
            </OpMode>
            <OpMode>
                <Name>DC_Sync</Name>
                <Desc>DC_Sync</Desc>               
                <AssignActivate>#x300</AssignActivate>
                <CycleTimeSync0 Factor="1">0</CycleTimeSync0>
                <ShiftTimeSync0>2000200000</ShiftTimeSync0>
            </OpMode>
        </Dc>       
        <Eeprom>
          <ByteSize>4096</ByteSize>                  
          <ConfigData>8003006EFF00FF000000</ConfigData> 
        </Eeprom>
     </Device>              
    </Devices>
  </Descriptions>
</EtherCATInfo>""")

        open(os.path.join(self.easycat_path, "easycat.xml"), "w").write("\n".join(output))

    def easycat_makefile(self):
        output = []
        output.append("")
        output.append("all: load")
        output.append("")
        output.append("easycat:")
        output.append("	pio run")
        output.append("")
        output.append("load:")
        output.append("	pio run --target=upload")
        output.append("")
        open(os.path.join(self.easycat_path, "Makefile"), "w").write("\n".join(output))

    def easycat_functions(self):
        output = []
        output.append("")
        output.append("#include <SPI.h>")
        output.append("")
        output.append("#define CUSTOM 1")
        output.append("#define CUST_BYTE_NUM_IN 32")
        output.append("#define CUST_BYTE_NUM_OUT 32")
        output.append("")
        output.append("typedef struct {")

        out_size = 0
        for is_bool in (False, True):
            for plugin_instance in self.project.plugin_instances:
                for signal_name, signal_config in plugin_instance.signals().items():
                    varname = signal_config["varname"]
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    virtual = signal_config.get("virtual")
                    if virtual:
                        continue
                    if bool(boolean) != is_bool:
                        continue
                    if direction == "output":
                        if boolean:
                            output.append(f"    bool {varname};")
                            out_size += 1
                        else:
                            output.append(f"    float {varname};")
                            out_size += 32
                            output.append(f"    float {varname}_SCALE;")
                            out_size += 32
                    # output.append(f"    float {varname}_OFFSET;")
                    # out_size += 32;
                    elif direction == "input":
                        if not boolean:
                            output.append(f"    float {varname}_SCALE;")
                            out_size += 32
        # output.append(f"    float {varname}_OFFSET;")
        # out_size += 32;

        output.append("    uint8_t Fill[32];")
        output.append(f"    // size: {out_size} / {out_size / 8}")
        output.append("} PROCBUFFER_OUT;")
        output.append("")
        output.append("typedef struct {")
        in_size = 0
        for is_bool in (False, True):
            for plugin_instance in self.project.plugin_instances:
                for signal_name, signal_config in plugin_instance.signals().items():
                    varname = signal_config["varname"]
                    direction = signal_config["direction"]
                    boolean = signal_config.get("bool")
                    virtual = signal_config.get("virtual")
                    if virtual:
                        continue
                    if bool(boolean) != is_bool:
                        continue
                    if direction == "input":
                        if boolean:
                            output.append(f"    bool {varname};")
                            in_size += 1
                        else:
                            output.append(f"    float {varname};")
                            in_size += 32
        output.append("    uint8_t Fill[32];")
        output.append(f"    // size: {in_size} / {in_size / 8}")
        output.append("} PROCBUFFER_IN;")
        output.append("")
        output.append('#include "EasyCAT.h"')
        output.append("EasyCAT EASYCAT(10);")
        output.append("")

        defines = {
            "MODNAME": '"rio"',
            "PREFIX": '"rio"',
            "JOINTS": "3",
            "BUFFER_SIZE": self.project.buffer_bytes,
            "OSC_CLOCK": self.project.config["speed"],
        }
        for key, value in defines.items():
            output.append(f"#define {key} {value}")
        output.append("")
        output.append("""
long stamp_last = 0;
float fpga_stamp_last = 0;
uint32_t fpga_timestamp = 0;
""")

        output.append("")
        return output

    def easycat_startscript(self):
        output = ["#!/bin/sh"]
        output.append("")
        output.append("set -e")
        output.append("set -x")
        output.append("")
        output.append('DIRNAME=`dirname "$0"`')
        output.append("")
        output.append('echo "compile package:"')
        output.append('(cd "$DIRNAME" && make clean all)')
        output.append("")
        output.append('echo "running easycat:"')
        output.append("$DIRNAME/easycat")
        output.append("")
        output.append("")
        os.makedirs(self.easycat_path, exist_ok=True)
        target = os.path.join(self.easycat_path, "start.sh")
        open(target, "w").write("\n".join(output))
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def vinit(self, vname, vtype, halstr=None, vdir="input", force_mem=False):
        vtype = self.typemap.get(vtype, vtype)
        # if force_mem or vname.endswith("_SCALE") or vname.endswith("_OFFSET") or vname.endswith("_S32") or vname.endswith("_ABS"):
        if force_mem or vname.endswith("_OFFSET") or vname.endswith("_S32") or vname.endswith("_ABS"):
            return f"    data->{vname} = ({vtype}*)malloc(sizeof({vtype}));"
        else:
            if vname.endswith("_SCALE") or vname.endswith("_OFFSET"):
                bdir = "Out"
            else:
                bdir = vdir.title().replace("put", "")
            return f"    data->{vname} = &EASYCAT.Buffer{bdir}.{vname};"
