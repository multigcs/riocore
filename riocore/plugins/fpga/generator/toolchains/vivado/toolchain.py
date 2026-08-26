import importlib
import os
import shutil
import subprocess
import sys

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = self.config["output_path"]
        self.riocore_path = config["riocore_path"]
        self.toolchain_path = self.config.get("toolchains_json", {}).get("vivado", "")
        self.vitis_path = self.config.get("toolchains_json", {}).get("vitis", "")
        if self.toolchain_path and not self.toolchain_path.endswith("bin"):
            self.toolchain_path = os.path.join(self.toolchain_path, "bin")
        if not self.vitis_path and self.toolchain_path:
            self.vitis_path = self.toolchain_path.replace("Vivado", "Vitis")
        self.armcore = self.config.get("armcore", False)
        self.clock = int(self.config["speed"])

    @classmethod
    def info(cls):
        return {
            "url": "https://www.xilinx.com/products/design-tools/vivado.html",
            "info": "Xilinx/AMD Vivado",
            "description": "",
        }

    def pll(self, clock_in, clock_out):
        if self.config["family"] == "XC7":
            if float(clock_out) == 125000000.0 and float(clock_in) == 100000000.0:
                result = subprocess.check_output(
                    f"{self.riocore_path}/files/vivado-pll.sh \"{self.config['jdata']['family']}\" {float(clock_in) / 1000000} {float(clock_out) / 1000000} '{self.gateware_path}/pll.v'",
                    shell=True,
                )
                print(result.decode())
            else:
                print(f"WARNING: can not generate pll for this platform: set speed to: {clock_in} Hz")
                self.config["speed"] = clock_in
        else:
            print(f"WARNING: can not generate pll for this platform: set speed to: {clock_in} Hz")
            self.config["speed"] = clock_in

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.xdc")
        pins_generator.Pins(self.config).generate(path)

        if sys.platform == "linux":
            vivado = shutil.which("vivado")
            if vivado is None:
                print("WARNING: toolchain installation not found in PATH: vivado")
                print("  example: export PATH=$PATH:/opt/Xilinx/Vivado/2023.1/bin")

        verilogs = " ".join(self.config["verilog_files"])

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Vivado")
        makefile_data.append("")
        if self.vitis_path and self.toolchain_path:
            makefile_data.append(f"PATH     := {self.toolchain_path}:{self.vitis_path}:$(PATH)")
        elif self.toolchain_path:
            makefile_data.append(f"PATH     := {self.toolchain_path}:$(PATH)")
            makefile_data.append("")

        if self.armcore:
            for filename in ("ps7.xdc", "ps7.tcl"):
                source = os.path.join(self.config["json_path"], filename)
                if not os.path.exists(source):
                    source = os.path.join(os.path.dirname(__file__), filename)
                shutil.copy(source, os.path.join(path, filename))

            tcl_data = []
            tcl_data.append("")
            tcl_data.append('set projectname "rio-rtl"')
            tcl_data.append(f"set part {self.config['type']}")
            tcl_data.append('set outputdir "./$projectname"')
            tcl_data.append("")
            tcl_data.append("file mkdir $outputdir")
            tcl_data.append("create_project -part $part $projectname $outputdir")
            tcl_data.append("")
            tcl_data.append("read_xdc ps7.xdc")
            tcl_data.append("read_xdc pins.xdc")
            for verilog in self.config["verilog_files"]:
                if verilog == "globals.v":
                    continue
                tcl_data.append(f"add_files -norecurse {verilog}")
            tcl_data.append("")
            tcl_data.append("# block-design")
            tcl_data.append('create_bd_design "bd_rio"')
            tcl_data.append("")
            tcl_data.append("########### arm-core ###########")
            tcl_data.append("source ps7.tcl")
            tcl_data.append("################################")
            tcl_data.append("")
            tcl_data.append("# rio-module")
            tcl_data.append("set module_rio [create_bd_cell -type module -reference rio rio_0]")
            tcl_data.append("connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins rio_0/sysclk_in]")
            tcl_data.append("")
            for pname, pins in self.config["pinlists"].items():
                for pin, pin_config in pins.items():
                    if pin_config["varname"] == "sysclk_in":
                        continue
                    if pin_config.get("bus"):
                        continue
                    if pin_config["direction"] == "output":
                        dir_ch = "O"
                    elif pin_config["direction"] == "input":
                        dir_ch = "I"
                    else:
                        dir_ch = "IO"
                    tcl_data.append(f"create_bd_port -dir {dir_ch} {pin_config['varname']}")
                    tcl_data.append(f"connect_bd_net [get_bd_ports {pin_config['varname']}] [get_bd_pins rio_0/{pin_config['varname']}]")
            tcl_data.append("")

            tcl_data.append("# axi connect")
            tcl_data.append("apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/rio_0/S_AXI} ddr_seg {Auto} intc_ip {New AXI SmartConnect} master_apm {0}}  [get_bd_intf_pins rio_0/S_AXI]")
            tcl_data.append("set_property offset 0x40000000 [get_bd_addr_segs {processing_system7_0/Data/SEG_rio_0_reg0}]")
            tcl_data.append("")

            tcl_data.append("regenerate_bd_layout")
            tcl_data.append("save_bd_design")
            tcl_data.append("set bdpath [file dirname [get_files [get_property FILE_NAME [current_bd_design]]]]")
            tcl_data.append("")
            tcl_data.append("# top-wrapper")
            tcl_data.append("make_wrapper -files [get_files $bdpath/bd_rio.bd] -top")
            tcl_data.append("add_files -norecurse $bdpath/hdl/bd_rio_wrapper.v")
            tcl_data.append("")
            tcl_data.append("set obj [get_filesets sources_1]")
            tcl_data.append('set_property -name "top" -value "bd_rio_wrapper" -objects $obj')
            tcl_data.append('set_property -name "top_auto_set" -value "0" -objects $obj')
            tcl_data.append("")
            tcl_data.append("reset_run synth_1")
            tcl_data.append("launch_runs synth_1 -jobs 8")
            tcl_data.append("wait_on_run synth_1")
            tcl_data.append("launch_runs impl_1 -to_step write_bitstream -jobs 8")
            tcl_data.append("wait_on_run impl_1")
            tcl_data.append("")
            tcl_data.append("write_hw_platform -fixed -include_bit -force -file rio-rtl/bd_rio_wrapper.xsa")
            tcl_data.append("")
            tcl_data.append('puts "Implementation done!"')
            tcl_data.append("")
            open(os.path.join(path, "rio.tcl"), "w").write("\n".join(tcl_data))

            bitfileName = "rio-rtl/rio-rtl.runs/impl_1/bd_rio_wrapper.bit"
            makefile_data.append("")
            makefile_data.append("all: clean build load")
            makefile_data.append("")
            makefile_data.append("prepare:")
            makefile_data.append("	test -e prepare.sh || touch prepare.sh")
            makefile_data.append("	sh prepare.sh")
            makefile_data.append("")
            makefile_data.append("build: prepare clean rio-rtl/rio-rtl.runs/impl_1/bd_rio_wrapper.bit")
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append("	rm -rf rio-rtl")
            makefile_data.append("")
            makefile_data.append("rio-rtl/rio-rtl.runs/impl_1/bd_rio_wrapper.bit: rio.tcl")
            makefile_data.append("	rm -rf rio-rtl")
            makefile_data.append("	sed -i 's| clog2(| $$clog2(|g' *.v")
            makefile_data.append("	vivado -mode batch -source rio.tcl")
            makefile_data.append("")

            if self.config["family"] == "XC7":
                makefile_data.append("app_create: rio-rtl/bd_rio_wrapper.xsa")
                makefile_data.append("	rm -rf _vitis/")
                makefile_data.append("	echo 'setw _vitis' > app_create.tcl")
                makefile_data.append("	echo 'app create -name riolwip -hw {rio-rtl/bd_rio_wrapper.xsa} -proc ps7_cortexa9_0 -os standalone -template \"lwIP UDP Perf Server\"' >> app_create.tcl")
                makefile_data.append("	xsct app_create.tcl")
                makefile_data.append("")
                makefile_data.append("app_build: _vitis/riolwip_system")
                makefile_data.append("	echo 'setw _vitis' > app_build.tcl")
                makefile_data.append("	echo 'sysproj build -name riolwip_system' >> app_build.tcl")
                makefile_data.append("	echo '#bootgen -image riolwip_system.bif -arch zynq -o _vitis/riolwip_system/_ide/bootimage/BOOT.bin' >> app_build.tcl")
                makefile_data.append("	xsct app_build.tcl")
                makefile_data.append("	realpath _vitis/riolwip_system/Debug/sd_card/BOOT.BIN")
                makefile_data.append("")
                makefile_data.append("app:")
                makefile_data.append("	rm -rf _vitis/")
                makefile_data.append("	echo 'setw _vitis' > app.tcl")
                # makefile_data.append("	echo 'repo -set {repo}' >> app.tcl")
                # makefile_data.append("	echo 'repo -apps' >> app.tcl")
                makefile_data.append("	echo 'app create -name riolwip -hw {rio-rtl/bd_rio_wrapper.xsa} -proc ps7_cortexa9_0 -os standalone -template \"lwIP UDP Perf Server\"' >> app.tcl")
                # makefile_data.append("	echo 'app create -name riolwip -hw {rio-rtl/bd_rio_wrapper.xsa} -proc ps7_cortexa9_0 -os standalone -template \"RIO UDP Server\"' >> app.tcl")
                makefile_data.append("	echo 'sysproj build -name riolwip_system' >> app.tcl")
                makefile_data.append("	xsct app.tcl")
                makefile_data.append("	realpath _vitis/riolwip_system/Debug/sd_card/BOOT.BIN")
                makefile_data.append("")
                makefile_data.append("app_py:")
                makefile_data.append("	echo '' > app.py")
                makefile_data.append("	echo 'import hsi' >> app.py")
                makefile_data.append("	echo 'import vitis' >> app.py")
                makefile_data.append("	echo '' >> app.py")
                makefile_data.append("	echo 'xsa = \"rio-rtl/bd_rio_wrapper.xsa\"' >> app.py")
                makefile_data.append("	echo '' >> app.py")
                makefile_data.append("	echo 'HwDesign = hsi.HwManager.open_hw_design(xsa)' >> app.py")
                makefile_data.append("	echo 'HwDesign.report_property()' >> app.py")
                makefile_data.append("	echo 'cells = HwDesign.get_cells(filter='IP_TYPE==PROCESSOR')' >> app.py")
                makefile_data.append("	echo 'cpu_name = cells[0].NAME' >> app.py")
                makefile_data.append("	echo '' >> app.py")
                makefile_data.append("	echo 'client = vitis.create_client()' >> app.py")
                makefile_data.append("	echo 'client.set_workspace(\"_vitis\")' >> app.py")
                makefile_data.append("	echo '' >> app.py")
                makefile_data.append("	echo 'platform_name = \"rio_platform\"' >> app.py")
                makefile_data.append("	echo 'platform = client.create_platform_component(name=platform_name, hw_design=xsa, os=\"standalone\", cpu=cpu_name)' >> app.py")
                makefile_data.append("	echo 'platform.build()' >> app.py")
                makefile_data.append("	echo '' >> app.py")
                makefile_data.append("	echo 'app = client.create_app_component('fsbl', platform) ' >> app.py")
                makefile_data.append("	echo 'app.build()' >> app.py")
                makefile_data.append("	echo '' >> app.py")
                makefile_data.append("	vitis -s app.py")
                makefile_data.append("	realpath _vitis/riolwip_system/Debug/sd_card/BOOT.BIN")
                makefile_data.append("")

        else:
            bitfileName = "build/$(PROJECT).bit"
            makefile_data.append("PROJECT  := rio")
            makefile_data.append("TOP      := rio")
            makefile_data.append(f"PART     := {self.config['type']}")
            makefile_data.append(f"VERILOGS := {verilogs}")
            makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
            makefile_data.append("")
            makefile_data.append("all: clean build load")
            makefile_data.append("")
            makefile_data.append("prepare:")
            makefile_data.append("	test -e prepare.sh || touch prepare.sh")
            makefile_data.append("	sh prepare.sh")
            makefile_data.append("")
            makefile_data.append("build: prepare build/$(PROJECT).bit")
            makefile_data.append("")
            makefile_data.append("$(PROJECT).tcl: pins.xdc $(VERILOGS)")
            makefile_data.append('	@echo "set outputDir ./build" > $(PROJECT).tcl')
            makefile_data.append(r'	@echo "file mkdir \$$outputDir" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "" >> $(PROJECT).tcl')
            makefile_data.append(r'	@for VAR in $?; do echo $$VAR | grep -s -q "\.v$$" && echo "read_verilog $$VAR" >> $(PROJECT).tcl; done')
            makefile_data.append('	@echo "read_xdc pins.xdc" >> $(PROJECT).tcl')
            makefile_data.append("	@echo  >> $(PROJECT).tcl")
            makefile_data.append('	@echo "synth_design -top $(TOP) -part $(PART)" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "write_checkpoint -force \$$outputDir/post_synth.dcp" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_timing_summary -file \$$outputDir/post_synth_timing_summary.rpt" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_utilization -file \$$outputDir/post_synth_util.rpt" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "opt_design" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "place_design" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_clock_utilization -file \$$outputDir/clock_util.rpt" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "write_checkpoint -force \$$outputDir/post_place.dcp" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_utilization -file \$$outputDir/post_place_util.rpt" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_timing_summary -file \$$outputDir/post_place_timing_summary.rpt" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "route_design" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "write_checkpoint -force \$$outputDir/post_route.dcp" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_route_status -file \$$outputDir/post_route_status.rpt" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_timing_summary -file \$$outputDir/post_route_timing_summary.rpt" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_power -file \$$outputDir/post_route_power.rpt" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "report_drc -file \$$outputDir/post_imp_drc.rpt" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "write_verilog -force \$$outputDir/impl_netlist.v -mode timesim -sdf_anno true" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "" >> $(PROJECT).tcl')
            makefile_data.append(r'	@echo "write_bitstream -force \$$outputDir/$(PROJECT).bit" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "" >> $(PROJECT).tcl')
            makefile_data.append('	@echo "exit" >> $(PROJECT).tcl')
            makefile_data.append("")
            makefile_data.append("build/$(PROJECT).bit: $(PROJECT).tcl")
            makefile_data.append("	vivado -mode batch -source $(PROJECT).tcl")
            makefile_data.append("	cp -v hash_new.txt hash_compiled.txt")
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append("	rm -rf build $(PROJECT).tcl *.jou *.log .Xil")
            makefile_data.append("")

        flashcmd = self.config.get("flashcmd")
        if flashcmd:
            makefile_data.append("load:")
            makefile_data.append(f"	{flashcmd}")
            makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
            makefile_data.append("")
            flashcmd_ram = self.config.get("flashcmd_ram")
            if flashcmd_ram:
                makefile_data.append("sload:")
                makefile_data.append(f"	{flashcmd_ram}")
                makefile_data.append("")
        else:
            makefile_data.append("xc3sprog:")
            makefile_data.append(f"	xc3sprog -c nexys4 {bitfileName}")
            makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
            makefile_data.append("")
            makefile_data.append("load:")
            makefile_data.append(f"	openFPGALoader -b arty -f {bitfileName}")
            makefile_data.append("")
            makefile_data.append("sload:")
            makefile_data.append(f"	openFPGALoader -b arty {bitfileName}")
            makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
            makefile_data.append("")

        if self.toolchain_path:
            makefile_data.append("hw_server:")
            makefile_data.append(f"	sudo {self.toolchain_path}/vivado -mode batch -source flash.tcl")
            makefile_data.append("")

            makefile_data.append("ssh:")
            makefile_data.append("	scp -oHostKeyAlgorithms=+ssh-rsa rio-rtl/rio-rtl.runs/impl_1/bd_rio_wrapper.bit root@192.168.10.205:/tmp/rio.bit")
            makefile_data.append('	ssh -oHostKeyAlgorithms=+ssh-rsa root@192.168.10.205 "cat /tmp/rio.bit > /dev/xdevcfg"')
            makefile_data.append("")

        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))

        flash = []
        flash.append("open_hw_manager")
        flash.append("connect_hw_server -allow_non_jtag")
        flash.append("open_hw_target")
        flash.append("current_hw_device [get_hw_devices xc7z010_1]")
        flash.append("refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xc7z010_1] 0]")
        flash.append("set_property PROBES.FILE {} [get_hw_devices xc7z010_1]")
        flash.append("set_property FULL_PROBES.FILE {} [get_hw_devices xc7z010_1]")
        flash.append("set_property PROGRAM.FILE {rio-rtl/rio-rtl.runs/impl_1/bd_rio_wrapper.bit} [get_hw_devices xc7z010_1]")
        flash.append("program_hw_devices [get_hw_devices xc7z010_1]")
        flash.append("refresh_hw_device [lindex [get_hw_devices xc7z010_1] 0]")
        flash.append("")
        open(os.path.join(path, "flash.tcl"), "w").write("\n".join(flash))
