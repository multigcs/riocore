import importlib
import re
import shutil
import subprocess


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = f"{self.config['output_path']}/Gateware"
        self.riocore_path = config["riocore_path"]

    def info(cls):
        info = {
            "url": "https://github.com/YosysHQ/oss-cad-suite-build",
            "info": "Icestorm (yosys/nextpnr)",
            "description": "",
            "install": """### on Intel/AMD systems
```
mkdir -p /opt
cd /opt
wget "https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-09-10/oss-cad-suite-linux-x64-20240910.tgz"
tar xzvpf oss-cad-suite-linux-x64-20240910.tgz
rm -rf oss-cad-suite-linux-x64-20240910.tgz
```

### on Raspberry-PI 4 systems
```
mkdir -p /opt
cd /opt
wget "https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-09-10/oss-cad-suite-linux-arm64-20240910.tgz"
tar xzvpf oss-cad-suite-linux-arm64-20240910.tgz
rm -rf oss-cad-suite-linux-arm64-20240910.tgz
```
""",
        }
        return info

    def pll(self, clock_in, clock_out):
        if self.config["jdata"]["family"] == "ecp5":
            result = subprocess.check_output(f"ecppll -f '{self.gateware_path}/pll.v' -i {float(clock_in) / 1000000} -o {float(clock_out) / 1000000}", shell=True)
        elif self.config["jdata"]["type"] == "up5k":
            result = subprocess.check_output(f"icepll -p -m -f '{self.gateware_path}/pll.v' -i {float(clock_in) / 1000000} -o {float(clock_out) / 1000000}", shell=True)
            achieved = re.findall(r"F_PLLOUT:\s*(\d*\.\d*)\s*MHz \(achieved\)", result.decode())
            if achieved:
                new_speed = int(float(achieved[0]) * 1000000)
                if new_speed != self.config["speed"]:
                    print(f"WARNING: achieved PLL frequency is: {new_speed}")
                    self.config["speed"] = new_speed
        else:
            result = subprocess.check_output(f"icepll -q -m -f '{self.gateware_path}/pll.v' -i {float(clock_in) / 1000000} -o {float(clock_out) / 1000000}", shell=True)
            # print(result.decode())

    def generate(self, path):
        verilogs = " ".join(self.config["verilog_files"])
        family = self.config["family"]
        device_family = None
        board = self.config.get("board")
        if family.startswith("GW"):
            device_family = family
            if shutil.which("nextpnr-himbaechel") is not None:
                family = "himbaechel"
            else:
                family = "gowin"

        nextpnr = shutil.which(f"nextpnr-{family}")
        if nextpnr is None:
            print(f"WARNING: can not found toolchain installation in PATH: nextpnr (nextpnr-{family})")
            print("  example: export PATH=$PATH:/opt/oss-cad-suite/bin")

        if family == "ecp5":
            pins_generator = importlib.import_module(".pins", "riocore.generator.pins.lpf")
            bitfileName = "$(PROJECT).bit"
        elif family == "gatemate":
            pins_generator = importlib.import_module(".pins", "riocore.generator.pins.ccf")
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
            prepack_data.append(f'ctx.addClock("{key}", {int(value)/1000000})')

        for key, value in self.config["timing_constraints_instance"].items():
            prepack_data.append(f'ctx.addClock("{key}", {int(value)/1000000})')

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
        if self.config["type"] == "up5k":
            makefile_data.append("$(PROJECT).json: $(VERILOGS)")
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_$(FAMILY) -dsp -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        elif self.config["type"] == "gatemate":
            makefile_data.append("net/$(PROJECT).v: $(VERILOGS)")
            makefile_data.append("	mkdir -p net/")
            makefile_data.append("	yosys -q -l yosys.log -p 'read_verilog $(VERILOGS) ; synth_$(FAMILY) -top $(TOP) -nomx8 -json $(PROJECT).json -vlog net/$(PROJECT).v'")
        elif family in {"gowin", "himbaechel"}:
            makefile_data.append("$(PROJECT).json: $(VERILOGS)")
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_gowin -noalu -nowidelut -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        else:
            makefile_data.append("$(PROJECT).json: $(VERILOGS)")
            makefile_data.append("	yosys -q -l yosys.log -p 'synth_$(FAMILY) -top $(TOP) -json $(PROJECT).json' $(VERILOGS)")
        makefile_data.append("")
        if family == "ecp5":
            makefile_data.append("$(PROJECT).config: $(PROJECT).json pins.lpf")
            makefile_data.append(
                "	nextpnr-$(FAMILY) -q -l nextpnr.log --timing-allow-fail --pre-pack prepack.py --$(TYPE) --package $(PACKAGE) --json $(PROJECT).json --freq $(CLK_SPEED) --lpf pins.lpf --textcfg $(PROJECT).config"
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
        elif family == "gatemate":
            makefile_data.append("$(PROJECT).bit: net/$(PROJECT).v pins.ccf")
            makefile_data.append("	p_r -i net/$(PROJECT).v -o $(PROJECT) -ccf pins.ccf -cCP")
            makefile_data.append('	@echo ""')
            makefile_data.append('	@grep -B 1 "%$$" nextpnr.log')
            makefile_data.append('	@echo ""')
            makefile_data.append("")
            makefile_data.append("clean:")
            makefile_data.append(f"	rm -rf {bitfileName} net/ $(PROJECT).config $(PROJECT).json yosys.log nextpnr.log")
            makefile_data.append("")
        elif family in {"gowin", "himbaechel"}:
            makefile_data.append("$(PROJECT)_pnr.json: $(PROJECT).json pins.cst")
            if family == "himbaechel":
                makefile_data.append(
                    "	nextpnr-himbaechel -q -l nextpnr.log --timing-allow-fail --json $(PROJECT).json --write $(PROJECT)_pnr.json --freq $(CLK_SPEED) --device $(TYPE) --vopt cst=pins.cst --vopt family=${DEVICE_FAMILY}"
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
                "	nextpnr-$(FAMILY) -q -l nextpnr.log --timing-allow-fail --pre-pack prepack.py --$(TYPE) --package $(PACKAGE) --json $(PROJECT).json --freq $(CLK_SPEED) --pcf pins.pcf --asc $(PROJECT).asc"
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
            elif board and board == "Tangoboard":
                makefile_data.append("load: $(PROJECT).fs")
                makefile_data.append("	openFPGALoader -b tangnano9k $(PROJECT).fs -f")
            else:
                makefile_data.append(f"load: {bitfileName}")
                makefile_data.append(f"	 openFPGALoader -b ice40_generic {bitfileName}")

        makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))
