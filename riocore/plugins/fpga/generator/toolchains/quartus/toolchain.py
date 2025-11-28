import importlib
import os
import re
import shutil
import subprocess
import sys


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = self.config["output_path"]
        self.riocore_path = config["riocore_path"]
        self.toolchain_path = self.config.get("toolchains_json", {}).get("quartus", "")
        if self.toolchain_path and not self.toolchain_path.endswith("bin"):
            self.toolchain_path = os.path.join(self.toolchain_path, "bin")

    def info(cls):
        info = {
            "url": "https://www.intel.de/content/www/de/de/products/details/fpga/development-tools/quartus-prime.html",
            "info": "Intel Quartus",
            "description": """## add device support
```
select version -> individual Files -> Devices -> .qdz
```
bin/quartus

* Tools -> Install Device...

* Next -> Select Download-Folder -> Selct Device .... -> Exit

## I/O standards Definition (.qdf)
https://www.intel.com/content/www/us/en/programmable/quartushelp/17.0/reference/glossary/def_iostandard-1.htm

""",
        }
        return info

    def pll(self, clock_in, clock_out):
        if self.config["family"] in {"MAX 10", "Cyclone 10 LP", "Cyclone IV E"}:
            pll_cmd = f"{self.riocore_path}/files/quartus-pll.sh \"{self.config['family']}\" {float(clock_in) / 1000000} {float(clock_out) / 1000000} '{self.gateware_path}/pll.v'"
            if self.toolchain_path:
                pll_cmd += f" '{self.toolchain_path}'"
            result = subprocess.check_output(pll_cmd, shell=True)
            achieved = re.findall(r"OUTPUT FREQ:\s*(\d*\.\d*)", result.decode())
            if achieved:
                new_speed = int(achieved[0].replace(".", ""))
                if new_speed != self.config["speed"]:
                    print(f"WARNING: achieved PLL frequency is: {new_speed}")
                    self.config["speed"] = new_speed
        else:
            print(f"WARNING: can not generate pll for this platform: set speed to: {clock_in} Hz")
            self.config["speed"] = clock_in

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.qdf")
        pins_generator.Pins(self.config).generate(path)
        if sys.platform == "linux" and not self.toolchain_path:
            quartus_sh = shutil.which("quartus_sh")
            if quartus_sh is None:
                print("WARNING: can not found toolchain installation in PATH: quartus")
                print("  example: export PATH=$PATH:/opt/intelFPGA_lite/22.1std/quartus/bin/")

        verilogs = " ".join(self.config["verilog_files"])
        family = self.config["family"]
        ftype = self.config["type"]

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Quartus")
        makefile_data.append("")
        if self.toolchain_path:
            makefile_data.append(f"PATH            := {self.toolchain_path}:$(PATH)")
            makefile_data.append(f"LD_LIBRARY_PATH := {self.toolchain_path}:$(LD_LIBRARY_PATH)")
            makefile_data.append("")
        makefile_data.append("PROJECT   := rio")
        makefile_data.append("TOP       := rio")
        # makefile_data.append("NUM_CPUS  := $(shell nproc)")
        makefile_data.append("NUM_CPUS  := $(shell grep 'cpu cores' /proc/cpuinfo | tail -n 1 | cut -d':' -f2)")
        makefile_data.append(f"PART      := {ftype}")
        makefile_data.append(f'FAMILY    := "{family}"')
        makefile_data.append(f"VERILOGS  := {verilogs}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append("")
        makefile_data.append("QC   = quartus_sh")
        makefile_data.append("QP   = quartus_pgm")
        makefile_data.append("QM   = quartus_map")
        makefile_data.append("QF   = quartus_fit")
        makefile_data.append("QA   = quartus_asm")
        makefile_data.append("QS   = quartus_sta")
        makefile_data.append("ECHO = echo")
        makefile_data.append("Q   ?= @")
        makefile_data.append("")
        makefile_data.append("STAMP = echo done >")
        makefile_data.append("")
        makefile_data.append("QCFLAGS = --flow compile")
        makefile_data.append("QPFLAGS =")
        makefile_data.append("QMFLAGS = --read_settings_files=on $(addprefix --source=,$(VERILOGS))")
        makefile_data.append("QFFLAGS = --part=$(PART) --read_settings_files=on")
        makefile_data.append("")
        makefile_data.append("ASIGN = $(PROJECT).qsf $(PROJECT).qpf")
        makefile_data.append("")
        makefile_data.append("all: build")
        makefile_data.append("build: $(PROJECT)")
        makefile_data.append("")
        makefile_data.append("map: smart.log $(PROJECT).map.rpt")
        makefile_data.append("fit: smart.log $(PROJECT).fit.rpt")
        makefile_data.append("asm: smart.log $(PROJECT).asm.rpt")
        makefile_data.append("sta: smart.log $(PROJECT).sta.rpt")
        makefile_data.append("smart: smart.log")
        makefile_data.append("")
        makefile_data.append("$(ASIGN):")
        makefile_data.append('	$(Q)$(ECHO) "Generating asignment files."')
        makefile_data.append("	$(QC) --prepare -f $(FAMILY) -t $(TOP) $(PROJECT)")
        makefile_data.append("	echo >> $(PROJECT).qsf")
        makefile_data.append('	echo "set_global_assignment -name NUM_PARALLEL_PROCESSORS $(NUM_CPUS)" >> $(PROJECT).qsf')
        makefile_data.append('	echo "set_global_assignment -name VERILOG_INPUT_VERSION SYSTEMVERILOG_2005" >> $(PROJECT).qsf')
        makefile_data.append('	echo "set_global_assignment -name ON_CHIP_BITSTREAM_DECOMPRESSION OFF" >> $(PROJECT).qsf')
        makefile_data.append('	echo "set_global_assignment -name GENERATE_RBF_FILE ON" >> $(PROJECT).qsf')
        makefile_data.append('	echo "set_global_assignment -name GENERATE_SVF_FILE ON" >> $(PROJECT).qsf')
        makefile_data.append('	echo "set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION \\"USE AS REGULAR IO\\"" >> $(PROJECT).qsf')
        makefile_data.append("	echo >> $(PROJECT).qsf")
        makefile_data.append("	cat pins.qdf >> $(PROJECT).qsf")
        makefile_data.append("")
        makefile_data.append("smart.log: $(ASIGN)")
        makefile_data.append('	$(Q)$(ECHO) "Generating smart.log."')
        makefile_data.append("	$(QC) --determine_smart_action $(PROJECT) > smart.log")
        makefile_data.append("")
        makefile_data.append("$(PROJECT): smart.log $(PROJECT).asm.rpt $(PROJECT).sta.rpt")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).map.rpt: map.chg $(VERILOGS)")
        makefile_data.append("	$(QM) $(QMFLAGS) $(PROJECT)")
        makefile_data.append("	$(STAMP) fit.chg")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).fit.rpt: fit.chg $(PROJECT).map.rpt")
        makefile_data.append("	$(QF) $(QFFLAGS) $(PROJECT)")
        makefile_data.append("	$(STAMP) asm.chg")
        makefile_data.append("	$(STAMP) sta.chg")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).asm.rpt: asm.chg $(PROJECT).fit.rpt")
        makefile_data.append("	$(QA) $(PROJECT)")
        makefile_data.append("")
        makefile_data.append("$(PROJECT).sta.rpt: sta.chg $(PROJECT).fit.rpt")
        makefile_data.append("	$(QS) $(PROJECT)")
        makefile_data.append("	cp -v hash_new.txt hash_compiled.txt")
        makefile_data.append("")
        makefile_data.append("map.chg:")
        makefile_data.append("	$(STAMP) map.chg")
        makefile_data.append("fit.chg:")
        makefile_data.append("	$(STAMP) fit.chg")
        makefile_data.append("sta.chg:")
        makefile_data.append("	$(STAMP) sta.chg")
        makefile_data.append("asm.chg:")
        makefile_data.append("	$(STAMP) asm.chg")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append('	$(Q)$(ECHO) "Cleaning."')
        makefile_data.append("	rm -rf db incremental_db")
        makefile_data.append("	rm -f smart.log *.rpt *.sof *.chg *.qsf *.qpf *.summary *.smsg *.pin *.jdi")
        makefile_data.append("")
        flashcmd = self.config.get("flashcmd")
        if flashcmd:
            makefile_data.append("load:")
            makefile_data.append(f"	{flashcmd}")
        else:
            makefile_data.append("load:")
            makefile_data.append("	# openFPGALoader -v -c usb-blaster -m $(PROJECT).svf -f")
            makefile_data.append("	openFPGALoader -v -c usb-blaster -m $(PROJECT).rbf -f")
        makefile_data.append("")
        makefile_data.append("sload:")
        makefile_data.append("	openFPGALoader -v -c usb-blaster -m $(PROJECT).rbf")
        makefile_data.append("")
        makefile_data.append("qpload:")
        makefile_data.append("prog: $(PROJECT).sof")
        makefile_data.append('	$(Q)$(ECHO) "Programming."')
        makefile_data.append('	$(QP) --no_banner --mode=jtag -o "P;$(PROJECT).sof"')
        makefile_data.append("	cp -v hash_new.txt hash_flashed.txt")
        makefile_data.append("")
        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))

        clock_speed = self.config["clock"]["speed"]
        osc_speed = self.config["clock"].get("osc", clock_speed)
        osc_name = "sysclk_in"

        sdc_data = []
        sdc_data.append("")
        sdc_data.append(f'create_clock -name {osc_name} -period "{float(osc_speed) / 1000000} MHz" [get_ports {osc_name}]')
        sdc_data.append("derive_pll_clocks")
        sdc_data.append("derive_clock_uncertainty")
        sdc_data.append("")
        open(os.path.join(path, "rio.sdc"), "w").write("\n".join(sdc_data))
