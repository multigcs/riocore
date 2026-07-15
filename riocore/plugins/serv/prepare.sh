#!/bin/sh
#
#

echo "compile prog.hex"
rm -f *.elf *.bin *.hex
riscv64-unknown-elf-gcc -nostdlib -nostartfiles -march=rv32i -mabi=ilp32 -Tlink.ld -oprog.elf prog.S
riscv64-unknown-elf-objcopy -O binary prog.elf prog.bin
python3 makehex.py prog.bin 2048 > prog.hex
rm prog.bin prog.elf
