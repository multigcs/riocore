import importlib
import os
import shutil
import sys


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = self.config["output_path"]
        self.riocore_path = config["riocore_path"]
        self.toolchain_path = self.config.get("toolchains_json", {}).get("verilator", "")
        if self.toolchain_path and not self.toolchain_path.endswith("bin"):
            self.toolchain_path = os.path.join(self.toolchain_path, "bin")

    def info(cls):
        info = {
            "url": "https://www.veripool.org/verilator/",
            "info": "verilog simulation",
            "description": "",
        }
        return info

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.qdf")
        pins_generator.Pins(self.config).generate(path)
        if sys.platform == "linux":
            verilator = shutil.which("verilator")
            if verilator is None:
                print("WARNING: can not found toolchain installation in PATH: verilator")

        verilogs = " ".join(self.config["verilog_files"])

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Verilator")
        makefile_data.append("")
        if self.toolchain_path:
            makefile_data.append(f"PATH     := {self.toolchain_path}:$(PATH)")
            makefile_data.append("")
        makefile_data.append("PROJECT   := rio")
        makefile_data.append("TOP       := rio")
        makefile_data.append(f"VERILOGS  := {verilogs}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append("")
        makefile_data.append("all: build")
        makefile_data.append("build: obj_dir/V$(TOP)")
        makefile_data.append("")
        makefile_data.append("obj_dir/V$(TOP): $(VERILOGS)")
        makefile_data.append("	verilator --cc --exe --build -j 0 -Wall main.cpp $(TOP).v")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf obj_dir")
        makefile_data.append("")
        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))
