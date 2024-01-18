import importlib
import os


class Toolchain:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        pins_generator = importlib.import_module(f".pins", f"riocore.generator.pins.cst")
        pins_generator.Pins(self.config).generate(path)

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
        makefile_data.append(f"VERILOGS := {verilogs}")
        makefile_data.append("")
        makefile_data.append("all: $(PROJECT).fs")
        makefile_data.append("")
        makefile_data.append(f"$(PROJECT).json: $(VERILOGS)")
        makefile_data.append("	yosys -q -l yosys.log -p 'synth_gowin -noalu -nowidelut -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        makefile_data.append("")
        makefile_data.append("$(PROJECT)_pnr.json: $(PROJECT).json pins.cst")
        makefile_data.append(
            f"	nextpnr-gowin --seed 0 --json $(PROJECT).json --write $(PROJECT)_pnr.json --freq {float(self.config['speed']) / 1000000} --enable-globals --enable-auto-longwires --device $(DEVICE) --cst pins.cst"
        )
        makefile_data.append("")
        makefile_data.append("$(PROJECT).fs: $(PROJECT)_pnr.json")
        makefile_data.append("	gowin_pack -d ${FAMILY} -o $(PROJECT).fs $(PROJECT)_pnr.json")
        makefile_data.append("")
        makefile_data.append("load: $(PROJECT).fs")
        print("####board", board)
        makefile_data.append(f"	openFPGALoader -b {board.lower()} $(PROJECT).fs -f")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf $(PROJECT).fs $(PROJECT).json $(PROJECT)_pnr.json $(PROJECT).tcl abc.history impl yosys.log")
        makefile_data.append("")
        makefile_data.append("gowin_build: impl/pnr/project.fs")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).tcl: pins.cst $(VERILOGS)")
        makefile_data.append('	@echo "set_device -name $(FAMILY_GOWIN) $(DEVICE)" > $(PROJECT).tcl')
        makefile_data.append('	@for VAR in $?; do echo $$VAR | grep -s -q "\.v$$" && echo "add_file $$VAR" >> $(PROJECT).tcl; done')
        makefile_data.append('	@echo "add_file pins.cst" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "set_option -top_module $(TOP)" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "set_option -verilog_std v2001" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "set_option -vhdl_std vhd2008" >> $(PROJECT).tcl')
        set_options = self.config.get(
            "set_options",
            (
                "use_sspi_as_gpio",
                "use_mspi_as_gpio",
                "use_done_as_gpio",
                "use_ready_as_gpio",
                "use_reconfign_as_gpio",
                "use_i2c_as_gpio",
            ),
        )
        for set_option in set_options:
            makefile_data.append(f'	@echo "set_option -{set_option} 1" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "run all" >> $(PROJECT).tcl')
        makefile_data.append("")
        makefile_data.append("impl/pnr/project.fs: $(PROJECT).tcl")
        makefile_data.append("	gw_sh $(PROJECT).tcl")
        makefile_data.append("")
        makefile_data.append("gowin_load: impl/pnr/project.fs")
        makefile_data.append(f"	openFPGALoader -b {board.lower()} impl/pnr/project.fs -f")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))

        # generating project file for the gowin toolchain
        prj_data = []
        prj_data.append('<?xml version="1" encoding="UTF-8"?>')
        prj_data.append("<!DOCTYPE gowin-fpga-project>")
        prj_data.append("<Project>")
        prj_data.append("    <Template>FPGA</Template>")
        prj_data.append("    <Version>5</Version>")
        if family == "GW1N-9C":
            prj_data.append(f'    <Device name="{family_gowin}" pn="{ftype}">gw1nr9c-004</Device>')
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

        os.system(f"mkdir -p {path}/impl")
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
