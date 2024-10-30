import importlib
import re
import os
import shutil
import subprocess


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = f"{self.config['output_path']}/Gateware"
        self.riocore_path = config["riocore_path"]

    def info(cls):
        info = {
            "url": "https://www.gowinsemi.com/en/support/home/",
            "info": "Gowin EDA",
            "description": "",
            "install": """```### on Intel/AMD systems
mkdir -p /opt/gowin
cd /opt/gowin
wget "https://cdn.gowinsemi.com.cn/Gowin_V1.9.9.03_Education_linux.tar.gz"
tar xzvpf Gowin_V1.9.9.03_Education_linux.tar.gz
rm -rf Gowin_V1.9.9.03_Education_linux.tar.gz
```
""",
        }
        return info

    def pll(self, clock_in, clock_out):
        if self.config["jdata"]["family"] == "GW1N-9C":
            result = subprocess.check_output(
                f"python3 {self.riocore_path}/files/gowin-pll.py -d 'GW1NR-9 C6/I5' -f '{self.gateware_path}/pll.v' -i {float(clock_in) / 1000000} -o {float(clock_out) / 1000000}", shell=True
            )
            achieved = re.findall(r"Achieved output frequency:\s*(\d*\.\d*)\s*MHz", result.decode())
            if achieved:
                new_speed = int(float(achieved[0]) * 1000000)
                if new_speed != self.config["speed"]:
                    print(f"WARNING: achieved PLL frequency is: {new_speed}")
                    self.config["speed"] = new_speed
        else:
            print(f"WARNING: can not generate pll for this platform: set speed to: {clock_in} Hz")
            self.config["speed"] = clock_in

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.generator.pins.cst")
        pins_generator.Pins(self.config).generate(path)

        gw_sh = shutil.which("gw_sh")
        if gw_sh is None:
            print("WARNING: can not found toolchain installation in PATH: gowin (gw_sh)")
            print("  example: export PATH=$PATH:/opt/gowin/IDE/bin")

        verilogs = " ".join(self.config["verilog_files"])

        board = self.config.get("board")
        family = self.config["family"]
        ftype = self.config["type"]
        if family == "GW1N-9C":
            family_gowin = "GW1NR-9C"
        else:
            family_gowin = family

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Gowin and Icestorm")
        makefile_data.append("")
        makefile_data.append("PROJECT  := rio")
        makefile_data.append("TOP      := rio")
        makefile_data.append(f"FAMILY   := {family}")
        makefile_data.append(f"FAMILY_GOWIN := {family_gowin}")
        makefile_data.append(f"DEVICE   := {ftype}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append(f"VERILOGS := {verilogs}")
        makefile_data.append("")
        makefile_data.append("all: impl/pnr/project.fs")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf $(PROJECT).fs $(PROJECT).json $(PROJECT)_pnr.json $(PROJECT).tcl abc.history impl")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).tcl: pins.cst $(VERILOGS)")
        makefile_data.append('	@echo "set_device -name $(FAMILY_GOWIN) $(DEVICE)" > $(PROJECT).tcl')
        makefile_data.append(r'	@for VAR in $?; do echo $$VAR | grep -s -q "\.v$$" && echo "add_file $$VAR" >> $(PROJECT).tcl; done')
        makefile_data.append('	@echo "add_file rio.sdc" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "add_file pins.cst" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "set_option -top_module $(TOP)" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "set_option -verilog_std v2001" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "set_option -vhdl_std vhd2008" >> $(PROJECT).tcl')
        set_options = self.config.get(
            "set_options",
            [
                "use_sspi_as_gpio",
                "use_mspi_as_gpio",
                "use_done_as_gpio",
                "use_ready_as_gpio",
                "use_reconfign_as_gpio",
                "use_i2c_as_gpio",
            ],
        )
        if family in {"GW5A-25A", "GW5A-25B"}:
            set_options.append("use_cpu_as_gpio")

        for set_option in set_options:
            makefile_data.append(f'	@echo "set_option -{set_option} 1" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "run all" >> $(PROJECT).tcl')
        makefile_data.append("")
        makefile_data.append("impl/pnr/project.fs: $(PROJECT).tcl")
        makefile_data.append("	gw_sh $(PROJECT).tcl")
        makefile_data.append("	cp -v hash_new.txt hash_compiled.txt")
        makefile_data.append('	@grep -A 34 "3. Resource Usage Summary" impl/pnr/project.rpt.txt')
        makefile_data.append("")
        makefile_data.append("load: impl/pnr/project.fs")

        board_id = board.lower()
        if board_id == "tangoboard":
            board_id = "tangnano9k"
        makefile_data.append(f"	openFPGALoader -b {board_id} impl/pnr/project.fs -f")
        makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))

        # generating timing constraints (.sdc)
        speed_ns = 1000000000 / self.config["speed"]
        sdc_data = [f"create_clock -period {speed_ns:0.3f} -waveform {{0.000 {speed_ns / 2:0.2f}}} -name sysclk_in [get_ports {{sysclk_in}}]"]
        sdc_data.append("")
        for key, value in self.config["timing_constraints"].items():
            speed_ns = 1000000000 / int(value)
            sdc_data.append(f"create_clock -period {speed_ns:0.3f} -waveform {{0.000 {speed_ns / 2:0.2f}}} -name {key} [get_ports {{{key}}}]")
        sdc_data.append("")
        open(f"{path}/rio.sdc", "w").write("\n".join(sdc_data))

        # generating project file for the gowin toolchain
        prj_data = []
        prj_data.append('<?xml version="1" encoding="UTF-8"?>')
        prj_data.append("<!DOCTYPE gowin-fpga-project>")
        prj_data.append("<Project>")
        prj_data.append("    <Template>FPGA</Template>")
        prj_data.append("    <Version>5</Version>")
        if family == "GW1N-9C":
            prj_data.append(f'    <Device name="{family_gowin}" pn="{ftype}">gw1nr9c-004</Device>')
        elif family == "GW1N-9C7":
            prj_data.append(f'    <Device name="{family_gowin}" pn="{ftype}">gw1nr9c-017</Device>')
        elif family in {"GW5A-25A", "GW5A-25B"}:
            prj_data.append(f'    <Device name="{family_gowin}" pn="{ftype}">gw5a25b-003</Device>')
        elif family == "GW2AR-18":
            prj_data.append('    <Device name="" pn="">gw2ar18c-000</Device>')
        elif family == "GW2A-18C":
            prj_data.append('    <Device name="" pn="">gw2a18c-011</Device>')
        else:
            prj_data.append(f'    <Device name="{family_gowin}" pn="{ftype}">gw2ar-18-004</Device>')
        prj_data.append("    <FileList>")
        for verilog in verilogs.split():
            prj_data.append(f'        <File path="{verilog}" type="file.verilog" enable="1"/>')
        prj_data.append('    <File path="pins.cst" type="file.cst" enable="1"/>')
        prj_data.append("    </FileList>")
        prj_data.append("</Project>")
        open(f"{path}/rio.gprj", "w").write("\n".join(prj_data))

        os.makedirs(f"{path}/impl", exist_ok=True)
        pps_data = """{
 "Allow_Duplicate_Modules" : false,
 "Annotated_Properties_for_Analyst" : true,
 "BACKGROUND_PROGRAMMING" : "",
 "COMPRESS" : false,
 "CRC_CHECK" : true,
 "Clock_Conversion" : true,
 "Clock_Route_Order" : 0,
 "Correct_Hold_Violation" : true,
 "DONE" : false,
 "DOWNLOAD_SPEED" : "",
 "Default_Enum_Encoding" : "default",
 "Disable_Insert_Pad" : false,
 "ENCRYPTION_KEY" : false,
 "ENCRYPTION_KEY_TEXT" : "00000000000000000000000000000000",
 "FORMAT" : "txt",
 "FSM Compiler" : true,
 "Fanout_Guide" : 10000,
 "Frequency" : "Auto",
 "Generate_Constraint_File_of_Ports" : false,
 "Generate_IBIS_File" : false,
 "Generate_Plain_Text_Timing_Report" : false,
 "Generate_Post_PNR_Simulation_Model_File" : false,
 "Generate_Post_Place_File" : false,
 "Generate_SDF_File" : false,
 "Generate_VHDL_Post_PNR_Simulation_Model_File" : false,
 "GwSyn_Loop_Limit" : 2000,
 "HOTBOOT" : false,
 "I2C" : false,
 "I2C_SLAVE_ADDR" : "",
 "Implicit_Initial_Value_Support" : false,
 "IncludePath" : [],
 "Incremental_Compile" : "",
 "Initialize_Primitives" : false,
 "JTAG" : false,
 "MODE_IO" : false,
 "MSPI" : false,
 "Multiple_File_Compilation_Unit" : true,
 "Number_of_Critical_Paths" : "",
 "Number_of_Start/End_Points" : "",
 "OUTPUT_BASE_NAME" : "rio",
 "POWER_ON_RESET_MONITOR" : false,
 "PRINT_BSRAM_VALUE" : true,
 "PROGRAM_DONE_BYPASS" : false,
 "Pipelining" : true,
 "PlaceInRegToIob" : true,
 "PlaceIoRegToIob" : true,
 "PlaceOutRegToIob" : true,
 "Place_Option" : "0",
 "Process_Configuration_Verion" : "1.0",
 "Promote_Physical_Constraint_Warning_to_Error" : true,
 "Push_Tristates" : true,
 "READY" : false,
 "RECONFIG_N" : false,
 "Ram_RW_Check" : true,
 "Report_Auto-Placed_Io_Information" : false,
 "Resolve_Mixed_Drivers" : false,
 "Resource_Sharing" : true,
 "Retiming" : false,
 "Route_Maxfan" : 23,
 "Route_Option" : "0",
 "Run_Timing_Driven" : true,
 "SECURE_MODE" : false,
 "SECURITY_BIT" : true,
 "SPI_FLASH_ADDR" : "",
 "SSPI" : true,
 "Show_All_Warnings" : false,
 "Synthesis On/Off Implemented as Translate On/Off" : false,
 "Synthesize_tool" : "GowinSyn",
 "TclPre" : "",
 "TopModule" : "",
 "USERCODE" : "default",
 "Unused_Pin" : "As_input_tri_stated_with_pull_up",
 "Update_Compile_Point_Timing_Data" : false,
 "Use_Clock_Period_for_Unconstrainted IO" : false,
 "VCCAUX" : 3.3,
 "VHDL_Standard" : "VHDL_Std_1993",
 "Verilog_Standard" : "Vlg_Std_2001",
 "WAKE_UP" : "0",
 "Write_Vendor_Constraint_File" : true,
 "dsp_balance" : false,
 "show_all_warnings" : false,
 "turn_off_bg" : false
}"""
        open(f"{path}/impl/project_process_config.json", "w").write("\n".join(pps_data))
