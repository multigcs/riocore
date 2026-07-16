import os
import sys

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

    def gateware_instances(self):
        uid = self.plugin_setup["uid"]
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_predefines = instance["predefines"]
        ramsize = int(self.plugin_setup.get("ramsize", self.OPTIONS["ramsize"]["default"]))
        instance_parameter["RAM_SIZE"] = ramsize
        instance_parameter["INITIAL_FILE"] = f"\"prog_{uid}.hex\""
        return instances

    @classmethod
    def extra_files(cls, parent, instances):
        output = []
        output.append("""#!/bin/sh
#
# https://release-assets.githubusercontent.com/github-production-release-asset/486846742/0e1b7552-e5a3-4626-b978-a5f174501c53?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-07-16T05%3A54%3A58Z&rscd=attachment%3B+filename%3Dxpack-riscv-none-elf-gcc-15.2.0-1-linux-x64.tar.gz&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-07-16T04%3A54%3A12Z&ske=2026-07-16T05%3A54%3A58Z&sks=b&skv=2018-11-09&sig=qIFf8KXwgQzFX9b%2Fq9ELeuCuBWBjaBLQEV%2B1qADFWlY%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc4NDE4MjEzMCwibmJmIjoxNzg0MTc4NTMwLCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.8CxYWTzLp8kYHpJ539upf5RdL9BtC_yoygJCBY3hvPE&response-content-disposition=attachment%3B%20filename%3Dxpack-riscv-none-elf-gcc-15.2.0-1-linux-x64.tar.gz&response-content-type=application%2Foctet-stream
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



