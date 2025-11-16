
# Toolchain: Quartus

PATH            := /opt/intelFPGA_lite/20.1/quartus/bin:$(PATH)
LD_LIBRARY_PATH := /opt/intelFPGA_lite/20.1/quartus/bin:$(LD_LIBRARY_PATH)

PROJECT   := rio
TOP       := rio
NUM_CPUS  := $(shell grep 'cpu cores' /proc/cpuinfo | tail -n 1 | cut -d':' -f2)
PART      := 10CL025YU256C8G
FAMILY    := "Cyclone 10 LP"
VERILOGS  := globals.v pll.v blink.v pwmout.v w5500.v stepdir.v debouncer.v toggle.v pwmmod.v oneshot.v delay.v rio.v
CLK_SPEED := 48.0

QC   = quartus_sh
QP   = quartus_pgm
QM   = quartus_map
QF   = quartus_fit
QA   = quartus_asm
QS   = quartus_sta
ECHO = echo
Q   ?= @

STAMP = echo done >

QCFLAGS = --flow compile
QPFLAGS =
QMFLAGS = --read_settings_files=on $(addprefix --source=,$(VERILOGS))
QFFLAGS = --part=$(PART) --read_settings_files=on

ASIGN = $(PROJECT).qsf $(PROJECT).qpf

all: build
build: $(PROJECT)

map: smart.log $(PROJECT).map.rpt
fit: smart.log $(PROJECT).fit.rpt
asm: smart.log $(PROJECT).asm.rpt
sta: smart.log $(PROJECT).sta.rpt
smart: smart.log

$(ASIGN):
	$(Q)$(ECHO) "Generating asignment files."
	$(QC) --prepare -f $(FAMILY) -t $(TOP) $(PROJECT)
	echo >> $(PROJECT).qsf
	echo "set_global_assignment -name NUM_PARALLEL_PROCESSORS $(NUM_CPUS)" >> $(PROJECT).qsf
	echo "set_global_assignment -name VERILOG_INPUT_VERSION SYSTEMVERILOG_2005" >> $(PROJECT).qsf
	echo "set_global_assignment -name ON_CHIP_BITSTREAM_DECOMPRESSION OFF" >> $(PROJECT).qsf
	echo "set_global_assignment -name GENERATE_RBF_FILE ON" >> $(PROJECT).qsf
	echo "set_global_assignment -name GENERATE_SVF_FILE ON" >> $(PROJECT).qsf
	echo "set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION \"USE AS REGULAR IO\"" >> $(PROJECT).qsf
	echo >> $(PROJECT).qsf
	cat pins.qdf >> $(PROJECT).qsf

smart.log: $(ASIGN)
	$(Q)$(ECHO) "Generating smart.log."
	$(QC) --determine_smart_action $(PROJECT) > smart.log

$(PROJECT): smart.log $(PROJECT).asm.rpt $(PROJECT).sta.rpt

$(PROJECT).map.rpt: map.chg $(VERILOGS)
	$(QM) $(QMFLAGS) $(PROJECT)
	$(STAMP) fit.chg

$(PROJECT).fit.rpt: fit.chg $(PROJECT).map.rpt
	$(QF) $(QFFLAGS) $(PROJECT)
	$(STAMP) asm.chg
	$(STAMP) sta.chg

$(PROJECT).asm.rpt: asm.chg $(PROJECT).fit.rpt
	$(QA) $(PROJECT)

$(PROJECT).sta.rpt: sta.chg $(PROJECT).fit.rpt
	$(QS) $(PROJECT)
	cp -v hash_new.txt hash_compiled.txt

map.chg:
	$(STAMP) map.chg
fit.chg:
	$(STAMP) fit.chg
sta.chg:
	$(STAMP) sta.chg
asm.chg:
	$(STAMP) asm.chg

clean:
	$(Q)$(ECHO) "Cleaning."
	rm -rf db incremental_db
	rm -f smart.log *.rpt *.sof *.chg *.qsf *.qpf *.summary *.smsg *.pin *.jdi

load:
	openFPGALoader -v -b cyc1000 -m rio.rbf -f

sload:
	openFPGALoader -v -c usb-blaster -m $(PROJECT).rbf

qpload:
prog: $(PROJECT).sof
	$(Q)$(ECHO) "Programming."
	$(QP) --no_banner --mode=jtag -o "P;$(PROJECT).sof"
	cp -v hash_new.txt hash_flashed.txt

