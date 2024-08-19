import importlib
import shutil


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = f"{self.config['output_path']}/Gateware"
        self.riocore_path = config["riocore_path"]

    def info(cls):
        info = {
            "url": "https://www.xilinx.com/products/design-tools/ise-design-suite/ise-webpack.html",
            "info": "Xilinx/AMD ISE WebPACK",
            "description": "",
        }
        return info

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.generator.pins.ucf")
        pins_generator.Pins(self.config).generate(path)

        ngdbuild = shutil.which("ngdbuild")
        if ngdbuild is None:
            print("WARNING: can not found toolchain installation in PATH: ise (ngdbuild)")
            print("  example: export PATH=$PATH:/opt/Xilinx/14.7/ISE_DS/ISE/bin/lin64/")

        verilogs = " ".join(self.config["verilog_files"])

        # CClk | jtagclk
        startupClk = self.config["jdata"]["clock"].get("startup", "jtagclk")

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: ISE/Webpack")
        makefile_data.append("")
        makefile_data.append("PROJECT  := rio")
        makefile_data.append("TOP      := rio")
        makefile_data.append(f"PART     := {self.config['type']}")
        makefile_data.append(f"VERILOGS := {verilogs}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append(f"STARTUP_CLK := {startupClk}")
        makefile_data.append("")
        makefile_data.append("all: $(PROJECT).bit")
        makefile_data.append("")
        makefile_data.append("$(PROJECT)-modules.v: $(VERILOGS)")
        makefile_data.append("	cat $(VERILOGS) > $(PROJECT)-modules.v")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).ngc: $(PROJECT)-modules.v")
        makefile_data.append("	echo 'run -ifn $(PROJECT)-modules.v -ifmt Verilog -ofn $(PROJECT).ngc -top $(TOP) -p $(PART) -opt_mode Speed -opt_level 1' | xst")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).ngd: $(PROJECT).ngc pins.ucf")
        makefile_data.append("	ngdbuild -p $(PART) -uc pins.ucf $(PROJECT).ngc")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).ncd: $(PROJECT).ngd")
        makefile_data.append("	map -detail -pr b $(PROJECT).ngd")
        makefile_data.append("")
        makefile_data.append("parout.ncd: $(PROJECT).ncd $(PROJECT).pcf")
        makefile_data.append("	par -w $(PROJECT).ncd parout.ncd $(PROJECT).pcf")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).bit: parout.ncd $(PROJECT).pcf")
        makefile_data.append("	bitgen -w -g StartUpClk:$(STARTUP_CLK) -g CRC:Enable parout.ncd $(PROJECT).bit $(PROJECT).pcf")
        makefile_data.append("	cp -v hash_new.txt hash_compiled.txt")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf $(PROJECT).ngc $(PROJECT).ngd $(PROJECT).ncd parout.ncd $(PROJECT).bit")
        makefile_data.append("")
        makefile_data.append("load: $(PROJECT).bit")
        flashcmd = self.config.get("flashcmd")
        if flashcmd:
            makefile_data.append(f"	{flashcmd}")
        else:
            makefile_data.append("	openFPGALoader -v -c usb-blaster $(PROJECT).bit -f")
        makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))
