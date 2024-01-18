import importlib


class Toolchain:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        verilogs = " ".join(self.config["verilog_files"])

        if self.config["family"] == "ecp5":
            pins_generator = importlib.import_module(f".pins", f"riocore.generator.pins.lpf")
            bitfileName = "$(PROJECT).bit"
        else:
            pins_generator = importlib.import_module(f".pins", f"riocore.generator.pins.pcf")
            bitfileName = "$(PROJECT).bin"

        pins_generator.Pins(self.config).generate(path)

        verilogs = " ".join(self.config["verilog_files"])
        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Icestorm")
        makefile_data.append("")
        makefile_data.append("PROJECT  := rio")
        makefile_data.append("TOP      := rio")
        makefile_data.append(f"FAMILY   := {self.config['family']}")
        makefile_data.append(f"TYPE     := {self.config['type']}")
        makefile_data.append(f"PACKAGE  := {self.config['package']}")
        makefile_data.append(f"VERILOGS := {verilogs}")
        makefile_data.append("")
        makefile_data.append(f"all: {bitfileName}")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).json: $(VERILOGS)")
        if self.config["type"] == "up5k":
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_$(FAMILY) -dsp -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        else:
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_$(FAMILY) -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        makefile_data.append("")
        if self.config["family"] == "ecp5":
            makefile_data.append("$(PROJECT).config: $(PROJECT).json pins.lpf")
            makefile_data.append("	nextpnr-${FAMILY} -q -l nextpnr.log --${TYPE} --package ${PACKAGE} --json $(PROJECT).json --lpf pins.lpf --textcfg $(PROJECT).config")
            makefile_data.append('	@echo ""')
            makefile_data.append('	@grep -B 1 "%$$" nextpnr.log')
            makefile_data.append('	@echo ""')
            makefile_data.append("")
            makefile_data.append(f"{bitfileName}: $(PROJECT).config")
            makefile_data.append(f"	ecppack --svf $(PROJECT).svf $(PROJECT).config {bitfileName}")
            makefile_data.append("")
            makefile_data.append(f"$(PROJECT).svf: {bitfileName}")
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append(f"	rm -rf {bitfileName} $(PROJECT).svf $(PROJECT).config $(PROJECT).json yosys.log nextpnr.log")
            makefile_data.append("")
        else:
            makefile_data.append("$(PROJECT).asc: $(PROJECT).json pins.pcf")
            makefile_data.append("	nextpnr-${FAMILY} -q -l nextpnr.log --${TYPE} --package ${PACKAGE} --json $(PROJECT).json --pcf pins.pcf --asc $(PROJECT).asc")
            makefile_data.append('	@echo ""')
            makefile_data.append('	@grep -B 1 "%$$" nextpnr.log')
            makefile_data.append('	@echo ""')
            makefile_data.append("")
            makefile_data.append(f"{bitfileName}: $(PROJECT).asc")
            makefile_data.append(f"	icepack $(PROJECT).asc {bitfileName}")
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append(f"	rm -rf {bitfileName} $(PROJECT).asc $(PROJECT).json yosys.log nextpnr.log")
            makefile_data.append("")
        makefile_data.append("check:")
        makefile_data.append("	verilator --top-module $(PROJECT) --lint-only -Wall *.v")
        makefile_data.append("")
        makefile_data.append(f"sim: $(VERILOGS)")
        makefile_data.append(f"	verilator --cc --exe --build -j 0 -Wall --top-module $(PROJECT) sim_main.cpp $(VERILOGS)")
        makefile_data.append("")
        makefile_data.append(f"tinyprog: {bitfileName}")
        makefile_data.append(f"	tinyprog -p {bitfileName}")
        makefile_data.append("")
        flashcmd = self.config.get("flashcmd")
        if flashcmd:
            makefile_data.append(f"load: {bitfileName}")
            makefile_data.append(f"	{flashcmd}")
        else:
            makefile_data.append(f"load: {bitfileName}")
            makefile_data.append(f"	 openFPGALoader -b ice40_generic {bitfileName}")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))
