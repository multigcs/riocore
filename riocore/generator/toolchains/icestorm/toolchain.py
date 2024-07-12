import importlib
import shutil


class Toolchain:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        verilogs = " ".join(self.config["verilog_files"])
        family = self.config["family"]
        device_family = None
        board = self.config.get("board")
        if family.startswith("GW"):
            device_family = family
            if shutil.which(f"nextpnr-himbaechel") is not None:
                family = "himbaechel"
            else:
                family = "gowin"

        nextpnr = shutil.which(f"nextpnr-{family}")
        if nextpnr is None:
            print(f"WARNING: can not found toolchain installation in PATH: nextpnr (nextpnr-{family})")

        if family == "ecp5":
            pins_generator = importlib.import_module(".pins", "riocore.generator.pins.lpf")
            bitfileName = "$(PROJECT).bit"
        elif family in {"gowin", "himbaechel"}:
            pins_generator = importlib.import_module(".pins", "riocore.generator.pins.cst")
            bitfileName = "$(PROJECT).fs"
        else:
            pins_generator = importlib.import_module(".pins", "riocore.generator.pins.pcf")
            bitfileName = "$(PROJECT).bin"

        pins_generator.Pins(self.config).generate(path)

        prepack_data = []
        for key, value in self.config["timing_constraints"].items():
            prepack_data.append(f'ctx.addClock("{key}", {int(value)})')

        prepack_data.append("")
        open(f"{path}/prepack.py", "w").write("\n".join(prepack_data))

        verilogs = " ".join(self.config["verilog_files"])
        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Icestorm")
        makefile_data.append("")
        makefile_data.append("PROJECT   := rio")
        makefile_data.append("TOP       := rio")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append(f"FAMILY    := {family}")
        if device_family:
            makefile_data.append(f"DEVICE_FAMILY   := {device_family}")
        makefile_data.append(f"TYPE      := {self.config['type']}")
        makefile_data.append(f"PACKAGE   := {self.config['package']}")
        makefile_data.append(f"VERILOGS  := {verilogs}")
        makefile_data.append("")
        makefile_data.append(f"all: {bitfileName}")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).json: $(VERILOGS)")
        if self.config["type"] == "up5k":
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_$(FAMILY) -dsp -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        elif family in {"gowin", "himbaechel"}:
            OPTIONS: -noalu - nowidelut
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_gowin -noalu -nowidelut -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        else:
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_$(FAMILY) -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        makefile_data.append("")
        if family == "ecp5":
            makefile_data.append("$(PROJECT).config: $(PROJECT).json pins.lpf")
            makefile_data.append(
                "	nextpnr-$(FAMILY) -q -l nextpnr.log --pre-pack prepack.py --$(TYPE) --package $(PACKAGE) --json $(PROJECT).json --freq $(CLK_SPEED) --lpf pins.lpf --textcfg $(PROJECT).config"
            )
            makefile_data.append('	@echo ""')
            makefile_data.append('	@grep -B 1 "%$$" nextpnr.log')
            makefile_data.append('	@echo ""')
            makefile_data.append("")
            makefile_data.append(f"{bitfileName}: $(PROJECT).config")
            makefile_data.append(f"	ecppack --svf $(PROJECT).svf $(PROJECT).config {bitfileName}")
            makefile_data.append("	cp -v hash_new.txt hash_compiled.txt")
            makefile_data.append("")
            makefile_data.append(f"$(PROJECT).svf: {bitfileName}")
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append(f"	rm -rf {bitfileName} $(PROJECT).svf $(PROJECT).config $(PROJECT).json yosys.log nextpnr.log")
            makefile_data.append("")
        elif family in {"gowin", "himbaechel"}:
            makefile_data.append("$(PROJECT)_pnr.json: $(PROJECT).json pins.cst")
            if family == "himbaechel":
                makefile_data.append(
                    "	nextpnr-himbaechel -q -l nextpnr.log --json $(PROJECT).json --write $(PROJECT)_pnr.json --freq $(CLK_SPEED) --device $(TYPE) --vopt cst=pins.cst --vopt family=${DEVICE_FAMILY}"
                )
            else:
                makefile_data.append(
                    "	nextpnr-gowin -q -l nextpnr.log --seed 0 --json $(PROJECT).json --write $(PROJECT)_pnr.json --freq $(CLK_SPEED) --enable-globals --enable-auto-longwires --device $(TYPE) --cst pins.cst"
                )
            makefile_data.append('	@echo ""')
            makefile_data.append('	@grep -B 1 "%$$" nextpnr.log')
            makefile_data.append('	@echo ""')
            makefile_data.append("")
            makefile_data.append("$(PROJECT).fs: $(PROJECT)_pnr.json")
            makefile_data.append("	gowin_pack -d ${DEVICE_FAMILY} -o $(PROJECT).fs $(PROJECT)_pnr.json")
            makefile_data.append("	cp -v hash_new.txt hash_compiled.txt")
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append("	rm -rf $(PROJECT).fs $(PROJECT).json $(PROJECT)_pnr.json $(PROJECT).tcl abc.history impl yosys.log nextpnr.log")
            makefile_data.append("")
        else:
            makefile_data.append("$(PROJECT).asc: $(PROJECT).json pins.pcf")
            makefile_data.append(
                "	nextpnr-$(FAMILY) -q -l nextpnr.log --pre-pack prepack.py --$(TYPE) --package $(PACKAGE) --json $(PROJECT).json --freq $(CLK_SPEED) --pcf pins.pcf --asc $(PROJECT).asc"
            )
            makefile_data.append('	@echo ""')
            makefile_data.append('	@grep -B 1 "%$$" nextpnr.log')
            makefile_data.append('	@echo ""')
            makefile_data.append("")
            makefile_data.append(f"{bitfileName}: $(PROJECT).asc")
            makefile_data.append(f"	icepack $(PROJECT).asc {bitfileName}")
            makefile_data.append("	cp -v hash_new.txt hash_compiled.txt")
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append(f"	rm -rf {bitfileName} $(PROJECT).asc $(PROJECT).json yosys.log nextpnr.log")
            makefile_data.append("")
        makefile_data.append("check:")
        makefile_data.append("	verilator --top-module $(PROJECT) --lint-only -Wall *.v")
        makefile_data.append("")
        makefile_data.append("sim: $(VERILOGS)")
        makefile_data.append("	verilator --cc --exe --build -j 0 -Wall --top-module $(PROJECT) sim_main.cpp $(VERILOGS)")
        makefile_data.append("")
        makefile_data.append(f"tinyprog: {bitfileName}")
        makefile_data.append(f"	tinyprog -p {bitfileName}")
        makefile_data.append("")
        flashcmd = self.config.get("flashcmd")
        if flashcmd:
            makefile_data.append(f"load: {bitfileName}")
            makefile_data.append(f"	{flashcmd}")
        else:
            if board and board.startswith("TangNano"):
                makefile_data.append("load: $(PROJECT).fs")
                makefile_data.append(f"	openFPGALoader -b {board.lower()} $(PROJECT).fs -f")
            else:
                makefile_data.append(f"load: {bitfileName}")
                makefile_data.append(f"	 openFPGALoader -b ice40_generic {bitfileName}")

        makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))
