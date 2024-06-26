import importlib
import shutil


class Toolchain:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.generator.pins.xdc")
        pins_generator.Pins(self.config).generate(path)

        vivado = shutil.which("vivado")
        if vivado is None:
            print("WARNING: can not found toolchain installation in PATH: vivado")

        verilogs = " ".join(self.config["verilog_files"])
        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Vivado")
        makefile_data.append("")
        makefile_data.append("PROJECT  := rio")
        makefile_data.append("TOP      := rio")
        makefile_data.append(f"PART     := {self.config['type']}")
        makefile_data.append(f"VERILOGS := {verilogs}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append("")
        makefile_data.append("all: build/$(PROJECT).bit")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).tcl: pins.xdc $(VERILOGS)")
        makefile_data.append('	@echo "set outputDir ./build" > $(PROJECT).tcl')
        makefile_data.append('	@echo "file mkdir \$$outputDir" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "" >> $(PROJECT).tcl')
        makefile_data.append('	@for VAR in $?; do echo $$VAR | grep -s -q "\.v$$" && echo "read_verilog $$VAR" >> $(PROJECT).tcl; done')
        makefile_data.append('	@echo "read_xdc pins.xdc" >> $(PROJECT).tcl')
        makefile_data.append("	@echo " " >> $(PROJECT).tcl")
        makefile_data.append('	@echo "synth_design -top $(TOP) -part $(PART)" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "write_checkpoint -force \$$outputDir/post_synth.dcp" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_timing_summary -file \$$outputDir/post_synth_timing_summary.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_utilization -file \$$outputDir/post_synth_util.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "opt_design" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "place_design" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_clock_utilization -file \$$outputDir/clock_util.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "write_checkpoint -force \$$outputDir/post_place.dcp" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_utilization -file \$$outputDir/post_place_util.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_timing_summary -file \$$outputDir/post_place_timing_summary.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "route_design" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "write_checkpoint -force \$$outputDir/post_route.dcp" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_route_status -file \$$outputDir/post_route_status.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_timing_summary -file \$$outputDir/post_route_timing_summary.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_power -file \$$outputDir/post_route_power.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "report_drc -file \$$outputDir/post_imp_drc.rpt" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "write_verilog -force \$$outputDir/impl_netlist.v -mode timesim -sdf_anno true" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "write_bitstream -force \$$outputDir/$(PROJECT).bit" >> $(PROJECT).tcl')
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
        makefile_data.append("xc3sprog: build/$(PROJECT).bit")
        makefile_data.append("	xc3sprog -c nexys4 build/$(PROJECT).bit")
        makefile_data.append("")
        makefile_data.append("load: build/$(PROJECT).bit")
        makefile_data.append("	openFPGALoader -b arty -f build/$(PROJECT).bit")
        makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))
