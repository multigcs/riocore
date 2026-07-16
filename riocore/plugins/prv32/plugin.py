import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "prv32"
        self.INFO = "risc-v softcore"
        self.DESCRIPTION = "picorv32 risc-v cpu for testing"
        self.KEYWORDS = "risc-v softcore cpu"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["countdown_timer.v", "reset.v", "gowin_sp.v", "gpio.v", "uart_wrap.v", "simpleuart.v", "picorv32.v", "prv32.v"]
        self.SRCFILES = ["src/sram.v", "src/link_cmd.ld", "src/uart.h", "src/countdown_timer.h", "src/leds.c", "src/main.c", "src/startup.s", "src/uart.c", "src/leds.h", "src/conv_to_init.c", "src/countdown_timer.c"]
        self.OPTIONS = {
            "source": {
                "type": "multiline",
                "description": "source code (asm)",
                "default": "",
            },
        }
        self.PINDEFAULTS = {
            "uart_rx": {
                "direction": "input",
            },
            "uart_tx": {
                "direction": "output",
            },
        }
        for led in range(6):
            self.PINDEFAULTS[f"led{led}"] = {
                "direction": "output",
            }
        uid = self.plugin_setup["uid"]
        self.VERILOGS_GEN = [f"sram_{uid}.v"]
        self.OPTIONS["source"]["default"] = open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read()
        self.INTERFACE = {
            "val_in": {
                "size": 16,
                "direction": "input",
            },
            "val_out": {
                "size": 16,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "val_in": {
                "direction": "input",
            },
            "val_out": {
                "direction": "output",
            },
        }

    def gateware_instances(self):
        # uid = self.plugin_setup["uid"]
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_parameter["BARREL_SHIFTER"] = "0"
        instance_parameter["ENABLE_MUL"] = "0"
        instance_parameter["ENABLE_DIV"] = "0"
        instance_parameter["ENABLE_FAST_MUL"] = "0"
        instance_parameter["ENABLE_COMPRESSED"] = "0"
        instance_parameter["ENABLE_IRQ_QREGS"] = "0"
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
rm -rf conv_to_init
gcc -o conv_to_init conv_to_init.c

""")
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            # source = instance.plugin_setup.get("source", instance.OPTIONS["source"]["default"])
            # target = os.path.join(parent.gateware_path, f"main_{uid}.c")
            # open(target, "w").write(source)
            output.append(f"""

cp -a main.c main_{uid}.c

rm -f prog_{uid}.elf prog_{uid}.hex prog_{uid}.bin main_{uid}.o countdown_timer.o uart.o leds.o
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c countdown_timer.c
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c uart.c
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c leds.c

$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -c main_{uid}.c
$RISCV_BIN-gcc -mno-save-restore -march=rv32i2p0 -mabi=ilp32 -nostartfiles -nostdlib -static -O1 -Tlink_cmd.ld -o prog_{uid}.elf startup.s main_{uid}.o countdown_timer.o uart.o leds.o

$RISCV_BIN-objcopy prog_{uid}.elf -O binary prog_{uid}.bin
rm -f ../mem_init_{uid}.v
od -v -Ax -t x4 prog_{uid}.bin > prog_{uid}.hex

./conv_to_init prog_{uid}.bin > ../mem_init_{uid}.v

# sed "s|include .*|include \\"mem_init_{uid}.v\\"|g" sram.v | sed "s|module sram|module sram_{uid}|g" > ../sram_{uid}.v
sed "s|include .*|include \\"mem_init_{uid}.v\\"|g" sram.v > ../sram_{uid}.v

""")

        target = os.path.join(parent.gateware_path, "prepare.sh")
        open(target, "w").write("\n".join(output))
