
# Toolchain: Gowin

PROJECT  := rio
TOP      := rio
FAMILY   := GW1N-9C
FAMILY_GOWIN := GW1NR-9C
DEVICE   := GW1NR-LV9QN88PC6/I5
CLK_SPEED := 27.0
VERILOGS := globals.v modbus.v uart_baud.v uart_rx.v uart_tx.v blink.v i2c_master.v i2cbus_i2cbus0.v stepdir.v w5500.v ws2812.v wled.v debouncer.v toggle.v pwmmod.v oneshot.v delay.v rio.v

all: build
build: impl/pnr/project.fs

clean:
	rm -rf $(PROJECT).fs $(PROJECT).json $(PROJECT)_pnr.json $(PROJECT).tcl abc.history impl

$(PROJECT).tcl: pins.cst $(VERILOGS)
	@echo "set_device -name $(FAMILY_GOWIN) $(DEVICE)" > $(PROJECT).tcl
	@for VAR in $?; do echo $$VAR | grep -s -q "\.v$$" && echo "add_file $$VAR" >> $(PROJECT).tcl; done
	@echo "add_file rio.sdc" >> $(PROJECT).tcl
	@echo "add_file pins.cst" >> $(PROJECT).tcl
	@echo "set_option -top_module $(TOP)" >> $(PROJECT).tcl
	@echo "set_option -verilog_std v2001" >> $(PROJECT).tcl
	@echo "set_option -vhdl_std vhd2008" >> $(PROJECT).tcl
	@echo "set_option -use_sspi_as_gpio 1" >> $(PROJECT).tcl
	@echo "set_option -use_mspi_as_gpio 1" >> $(PROJECT).tcl
	@echo "set_option -use_done_as_gpio 1" >> $(PROJECT).tcl
	@echo "set_option -use_ready_as_gpio 1" >> $(PROJECT).tcl
	@echo "set_option -use_reconfign_as_gpio 1" >> $(PROJECT).tcl
	@echo "set_option -use_i2c_as_gpio 1" >> $(PROJECT).tcl
	@echo "run all" >> $(PROJECT).tcl

impl/pnr/project.fs: $(PROJECT).tcl
	gw_sh $(PROJECT).tcl
	cp -v hash_new.txt hash_compiled.txt
	@grep -A 34 "3. Resource Usage Summary" impl/pnr/project.rpt.txt

load:
	openFPGALoader -b tangnano9k impl/pnr/project.fs -f
	cp -v hash_new.txt hash_flashed.txt

sload:
	openFPGALoader -b tangnano9k impl/pnr/project.fs
	cp -v hash_new.txt hash_flashed.txt

