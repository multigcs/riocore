import importlib
import os
import shutil
import sys


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = self.config["output_path"]
        self.riocore_path = config["riocore_path"]
        self.toolchain_path = self.config.get("toolchains_json", {}).get("efinity", "")
        if self.toolchain_path and not self.toolchain_path.endswith("bin"):
            self.toolchain_path = os.path.join(self.toolchain_path, "bin")

    def info(cls):
        info = {
            "url": "https://www.efinixinc.com/",
            "info": "Efinix - Efinity",
            "description": "untested",
        }
        return info

    def pll(self, clock_in, clock_out):
        if clock_in != 33330000 or clock_out != 100000000:
            print(f"WARNING: can not generate pll for this platform: set speed to: {clock_in} Hz")
            self.config["speed"] = clock_in

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.peri")
        pins_generator.Pins(self.config).generate(path)
        if sys.platform == "linux":
            efinity_sh = shutil.which("efx_run")
            if efinity_sh is None:
                print("WARNING: can not found toolchain installation in PATH: efx_run")
                print("  example: export PATH=$PATH:/opt/efinity/2024.2/bin/")

        verilogs = " ".join(self.config["verilog_files"])
        family = self.config["family"]
        ftype = self.config["type"]
        timing_model = self.config["timing_model"]

        xml_data = []
        xml_data.append(
            '<efx:project xmlns:efx="http://www.efinixinc.com/enf_proj" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name="rio" description="" sw_version="2024.2.294" last_run_state="pass" last_run_flow="bitstream" config_result_in_sync="sync" design_ood="sync" place_ood="sync" route_ood="sync" xsi:schemaLocation="http://www.efinixinc.com/enf_proj enf_proj.xsd" last_change="1740155391">'
        )
        xml_data.append("    <efx:device_info>")
        xml_data.append(f'        <efx:family name="{family}" />')
        xml_data.append(f'        <efx:device name="{ftype}" />')
        xml_data.append(f'        <efx:timing_model name="{timing_model}" />')
        xml_data.append("    </efx:device_info>")
        xml_data.append("    <efx:design_info>")
        xml_data.append('        <efx:top_module name="rio" />')
        for verilog in self.config["verilog_files"]:
            xml_data.append(f'        <efx:design_file name="{verilog}" />')
        xml_data.append("    </efx:design_info>")
        xml_data.append("    <efx:constraint_info>")
        xml_data.append('        <efx:sdc_file name="rio.sdc" />')
        xml_data.append("    </efx:constraint_info>")
        xml_data.append("    <efx:sim_info />")
        xml_data.append("    <efx:misc_info />")
        xml_data.append('    <efx:synthesis tool_name="efx_map">')
        xml_data.append('        <efx:param name="work_dir" value="work_syn" value_type="e_string" />')
        xml_data.append('        <efx:param name="write_efx_verilog" value="on" value_type="e_bool" />')
        xml_data.append('        <efx:param name="opt_mode" value="speed" value_type="e_option" />')
        xml_data.append("    </efx:synthesis>")
        xml_data.append('    <efx:place_and_route tool_name="efx_pnr">')
        xml_data.append('        <efx:param name="work_dir" value="work_pnr" value_type="e_string" />')
        xml_data.append('        <efx:param name="verbose" value="off" value_type="e_bool" />')
        xml_data.append('        <efx:param name="load_delaym" value="on" value_type="e_bool" />')
        xml_data.append("    </efx:place_and_route>")
        xml_data.append('    <efx:bitstream_generation tool_name="efx_pgm">')
        xml_data.append('        <efx:param name="mode" value="active" value_type="e_string" />')
        xml_data.append('        <efx:param name="width" value="1" value_type="e_string" />')
        xml_data.append('        <efx:param name="cold_boot" value="off" value_type="e_bool" />')
        xml_data.append('        <efx:param name="cascade" value="off" value_type="e_option" />')
        xml_data.append('        <efx:param name="enable_roms" value="on" value_type="e_option" />')
        xml_data.append('        <efx:param name="spi_low_power_mode" value="on" value_type="e_bool" />')
        xml_data.append('        <efx:param name="io_weak_pullup" value="on" value_type="e_bool" />')
        xml_data.append('        <efx:param name="oscillator_clock_divider" value="DIV8" value_type="e_option" />')
        xml_data.append("    </efx:bitstream_generation>")
        xml_data.append("</efx:project>")
        open(os.path.join(path, "rio.xml"), "w").write("\n".join(xml_data))

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: efinity")
        makefile_data.append("")
        if self.toolchain_path:
            makefile_data.append(f"PATH         := {self.toolchain_path}:$(PATH)")
            makefile_data.append(f"EFINITY_HOME := {os.path.dirname(self.toolchain_path)}")
            makefile_data.append(f"EFXPT_HOME   := {os.path.dirname(self.toolchain_path)}/pt")
            makefile_data.append(f"PYTHON       := {self.toolchain_path}/python3")
            makefile_data.append("")
        makefile_data.append("PROJECT   := rio")
        makefile_data.append("TOP       := rio")
        makefile_data.append(f"PART      := {ftype}")
        makefile_data.append(f'FAMILY    := "{family}"')
        makefile_data.append(f'TMODEL    := "{timing_model}"')
        makefile_data.append(f"VERILOGS  := {verilogs}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append("")
        makefile_data.append("all: clean build load")
        makefile_data.append("")
        makefile_data.append("build: outflow/$(PROJECT).bit")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).peri.xml: pins.py")
        makefile_data.append("	EFXPT_HOME=$(EFXPT_HOME) EFINITY_HOME=$(EFINITY_HOME) $(PYTHON) pins.py")
        makefile_data.append("")
        makefile_data.append("outflow/$(PROJECT).bit: $(PROJECT).xml $(PROJECT).peri.xml")
        makefile_data.append("	efx_run --flow compile $(PROJECT).xml")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf work_pnr  work_syn outflow")
        makefile_data.append("")
        makefile_data.append("load: $(PROJECT).svf")
        makefile_data.append("	openFPGALoader outflow/$(PROJECT).bit -f")
        makefile_data.append("")
        makefile_data.append("sload: $(PROJECT).svf")
        makefile_data.append("	openFPGALoader outflow/$(PROJECT).bit")
        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))
