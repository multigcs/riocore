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
        self.SRCFILES = ["makehex.py", "link.ld", "serv_params.vh"]
        self.OPTIONS = {
            "ramsize": {
                "default": 64,
                "type": int,
                "min": 64,
                "max": 2048,
                "unit": "byte",
                "description": "memory size",
            },
            "source": {
                "type": "multiline",
                "description": "source code (asm)",
                "default": """/*
* LED Blinker
* Assuming that GPIO_BASE is mapped to a GPIO core, which in turn is
* connected to LEDs, this will light the LEDs one at a time.
* Useful as smoke test to see that serv is running correctly
*/
#ifndef GPIO_BASE
#define GPIO_BASE 0x100
#endif

#ifndef DELAY
#define DELAY 0x20000 /* Loop 100000 times before inverting the LED */
#endif

	/*
	a0 = GPIO Base address
	t0 = Value
	t1 = Timer max value
	t2 = Current timer value

	*/

.globl _start
_start:
	/* Load GPIO base address to a0 */
	lui a0, %hi(GPIO_BASE)
	addi a0, a0, %lo(GPIO_BASE)

	/* Set timer value to control blink speed */
	li t1, DELAY

bl1:
	/* Write to LEDs */
	sb t0, 0(a0)

	/* invert LED */
	xori t0, t0, 1

	/* Reset timer */
	and t2, zero, zero

	/* Delay loop */
time1:
	addi t2, t2, 1
	bne t1, t2, time1
	j bl1
""",
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

    def gateware_instances(self, gateware=None):
        uid = self.plugin_setup["uid"]
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        ramsize = int(self.plugin_setup.get("ramsize", self.OPTIONS["ramsize"]["default"]))
        instance_parameter["RAM_SIZE"] = ramsize
        instance_parameter["INITIAL_FILE"] = f'"prog_{uid}.hex"'
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

""")
        for instance in instances:
            uid = instance.plugin_setup["uid"]
            ramsize = int(instance.plugin_setup.get("ramsize", instance.OPTIONS["ramsize"]["default"]))
            source = instance.plugin_setup.get("source", instance.OPTIONS["source"]["default"])
            target = os.path.join(parent.gateware_path, f"prog_{uid}.S")
            open(target, "w").write(source)

            output.append(f"""
echo "compile prog_{uid}.hex"
rm -f prog_{uid}.elf prog_{uid}.bin prog_{uid}.hex
$RISCV_BIN-gcc -nostdlib -nostartfiles -march=rv32i -mabi=ilp32 -Tlink.ld -oprog_{uid}.elf prog_{uid}.S
$RISCV_BIN-objcopy -O binary prog_{uid}.elf prog_{uid}.bin
python3 makehex.py prog_{uid}.bin {ramsize // 4} > prog_{uid}.hex
#rm -rf prog_{uid}.bin prog_{uid}.elf
    """)

        target = os.path.join(parent.gateware_path, "prepare.sh")
        open(target, "w").write("\n".join(output))
