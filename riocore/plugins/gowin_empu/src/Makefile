# Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause.

COMMONFLAGS = -mthumb -mcpu=cortex-m3
CFLAGS = $(COMMONFLAGS) -nostartfiles -nostdlib -static -O1
CPPFLAGS = 
ASFLAGS = $(COMMONFLAGS)
LIBS = -lgcc

CC = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
OBJDUMP = arm-none-eabi-objdump
AS = arm-none-eabi-as

ALL_CSRCS = cont_startup.c main.c uart.c gpio.c

%.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@

%.d: %.c
	$(CC) -MM $(CPPFLAGS) $< > $@.$$$$; \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	rm -f $@.$$$$

default: prog.bin

include $(ALL_CSRCS:.c=.d)

startup.o: startup.S
	$(CC) $(CFLAGS) -c startup.S

prog.elf: startup.o $(ALL_CSRCS:.c=.o) 
	$(CC) $(CFLAGS) -Tlink_cmd.ld -o prog.elf startup.o \
              $(ALL_CSRCS:.c=.o) $(LIBS)

prog.bin: prog.elf
	$(OBJCOPY) -O binary prog.elf prog.bin

clean:
	rm -f prog.elf prog.bin prog.srec startup.o $(ALL_CSRCS:.c=.d) $(ALL_CSRCS:.c=.o)
