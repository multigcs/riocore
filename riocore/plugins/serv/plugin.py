import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "serv"
        self.INFO = "minimal risc-v softcore"
        self.DESCRIPTION = "minimal risc-v cpu for testing"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["serv.v", "ram32.v", "ser_add.v", "ser_lt.v", "ser_shift.v", "serv_alu.v", "serv_bufreg.v", "serv_csr.v", "serv_ctrl.v", "serv_decode.v", "serv_mem_if.v", "serv_rf_if.v", "serv_rf_ram_if.v", "serv_rf_ram.v", "serv_rf_top.v", "serv_state.v", "serv_top.v", "shift_reg.v"]
        self.SRCFILES = ["src/makehex.py", "src/link.ld", "src/serv_params.vh", "src/main.c"]
        self.PLUGIN_CONFIGS = {"Source-Editor": "config.py"}
        self.OPTIONS = {
            "ramsize": {
                "default": 256,
                "type": int,
                "min": 64,
                "max": 2048,
                "unit": "byte",
                "description": "memory size",
            },
        }
        self.PINDEFAULTS = {
            "gpio0": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "gpio1": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "gpio2": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.source = self.plugin_setup.get("source", open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read())

    def gateware_instances(self, gateware=None):
        uid = self.plugin_setup["uid"]
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        ramsize = int(self.plugin_setup.get("ramsize", self.OPTIONS["ramsize"]["default"]))
        instance_parameter["RAM_SIZE"] = ramsize
        instance_parameter["INITIAL_FILE"] = f'"src/prog_{uid}.hex"'
        return instances

    @classmethod
    def extra_files(cls, parent, instances):

        output = []
        output.append("""#!/bin/sh
#
# https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v15.2.0-1
#
set -x

RISCV_BIN="riscv64-unknown-elf"
RISCV_BIN="riscv-none-elf"

cd src/

""")
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            ramsize = int(instance.plugin_setup.get("ramsize", instance.OPTIONS["ramsize"]["default"]))

            startup = []
            startup.append("")
            startup.append(".text")
            startup.append(".global _start")
            startup.append("_start:")
            startup.append(f"	li x2, {ramsize}")
            startup.append("	call main")
            startup.append("")
            target = os.path.join(parent.gateware_path, "src", f"startup_{uid}.s")
            open(target, "w").write("\n".join(startup))

            target = os.path.join(parent.gateware_path, "src", f"main_{uid}.c")
            open(target, "w").write(instance.source)

            instance.march = "rv32i"
            instance.mabi = "ilp32"
            instance.gcc_options = ""

            output.append(f"""
echo "compile prog_{uid}.hex"
rm -f prog_{uid}.elf prog_{uid}.bin prog_{uid}.hex

FLAGS="-nostartfiles -nostdlib -static -Os"

#$RISCV_BIN-gcc -nostdlib -nostartfiles -march=rv32i -mabi=ilp32 -Tlink.ld -oprog_{uid}.elf prog_{uid}.S

$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} $FLAGS -c main_{uid}.c
$RISCV_BIN-gcc -mno-save-restore -march={instance.march} -mabi={instance.mabi} {instance.gcc_options} $FLAGS -Tlink.ld -o prog_{uid}.elf startup_{uid}.s main_{uid}.o
$RISCV_BIN-size -G -d prog_{uid}.elf

$RISCV_BIN-objcopy -O binary prog_{uid}.elf prog_{uid}.bin
python3 makehex.py prog_{uid}.bin {ramsize // 4} > prog_{uid}.hex
#rm -rf prog_{uid}.bin prog_{uid}.elf
    """)

        target = os.path.join(parent.gateware_path, "prepare.sh")
        open(target, "w").write("\n".join(output))
