import importlib


class Toolchain:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        pins_generator = importlib.import_module(f".pins", f"riocore.generator.pins.lpf")
        pins_generator.Pins(self.config).generate(path)

        verilogs = " ".join(self.config["verilog_files"])

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Diamond")
        makefile_data.append("")
        makefile_data.append("PROJECT  := rio")
        makefile_data.append("TOP      := rio")
        makefile_data.append(f"PART     := {self.config['type']}")
        makefile_data.append(f"VERILOGS := {verilogs}")
        makefile_data.append("")
        makefile_data.append("all: build/$(PROJECT)_build.bit")
        makefile_data.append("")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).tcl: $(VERILOGS)")
        makefile_data.append('	@echo "prj_project new -name $(PROJECT) -impl build -dev $(PART) -lpf pins.lpf" > $(PROJECT).tcl')
        makefile_data.append('	@for VAR in $?; do echo $$VAR | grep -s -q "\.v$$" && echo "prj_src add $$VAR" >> $(PROJECT).tcl; done')
        makefile_data.append('	@echo "prj_impl option top $(TOP)" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "prj_project save" >> $(PROJECT).tcl')
        makefile_data.append('	@echo "prj_project close" >> $(PROJECT).tcl')
        makefile_data.append("")
        makefile_data.append("syn.tcl: $(PROJECT).tcl")
        makefile_data.append('	@echo "prj_project open $(PROJECT).ldf" >> syn.tcl')
        makefile_data.append('	@echo "prj_run Synthesis -impl build" >> syn.tcl')
        makefile_data.append('	@echo "prj_run Translate -impl build" >> syn.tcl')
        makefile_data.append('	@echo "prj_run Map -impl build" >> syn.tcl')
        makefile_data.append('	@echo "prj_run PAR -impl build" >> syn.tcl')
        makefile_data.append('	@echo "prj_run PAR -impl build -task PARTrace" >> syn.tcl')
        makefile_data.append('	@echo "prj_run Export -impl build -task Bitgen" >> syn.tcl')
        makefile_data.append('	@echo "prj_run Export -impl build -task Jedecgen" >> syn.tcl')
        makefile_data.append('	@echo "prj_project close" >> syn.tcl')
        makefile_data.append("")
        makefile_data.append("$(PROJECT).ldf: syn.tcl")
        makefile_data.append("	diamondc $(PROJECT).tcl")
        makefile_data.append("")
        makefile_data.append("build/$(PROJECT)_build.bit: $(PROJECT).ldf")
        makefile_data.append("	diamondc syn.tcl")
        makefile_data.append("")
        makefile_data.append("load:")
        makefile_data.append("	openFPGALoader -c usb-blaster build/$(PROJECT)_build.bit")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf build $(PROJECT).ldf $(PROJECT).tcl syn.tcl")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))
