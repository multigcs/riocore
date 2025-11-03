

TOOLCHAIN_PATH := /usr/src/MXM/riocore/riocore/toolchains
PICO_SDK_PATH := $(TOOLCHAIN_PATH)/pico-sdk
NINJA_SRC_PATH := $(TOOLCHAIN_PATH)/stepper-ninja

all: clean prepare build install

clean:
	rm -rf build

$(PICO_SDK_PATH):
	mkdir -p $(TOOLCHAIN_PATH)
	cd $(TOOLCHAIN_PATH) && git clone https://github.com/raspberrypi/pico-sdk
	cd $(TOOLCHAIN_PATH)/pico-sdk && git submodule update --init

$(NINJA_SRC_PATH):
	mkdir -p $(TOOLCHAIN_PATH)
	cd $(TOOLCHAIN_PATH) && git clone https://github.com/atrex66/stepper-ninja
	sed -i "s|.*PICO_SDK_PATH.*||g" $(NINJA_SRC_PATH)/firmware/CMakeLists.txt

prepare: $(NINJA_SRC_PATH) $(PICO_SDK_PATH) ninja-config.h
	cp -a ninja-config.h $(NINJA_SRC_PATH)/firmware/inc/config.h
	mkdir -p build

build: prepare ninja-config.h
	rm -rf build/stepper-ninja-*.uf2
	cd build && PICO_SDK_PATH=$(PICO_SDK_PATH) cmake -DBOARD=pico -DWIZCHIP_TYPE=W5500 $(NINJA_SRC_PATH)/firmware
	cd build && make clean
	cd build && make all
	ls build/stepper-ninja-*.uf2

/dev/disk/by-label/RPI-RP2:
	@echo "##### set rpi to bootmode #####"
	@exit 1

halcompile:
	sudo halcompile --install $(NINJA_SRC_PATH)/hal-driver/stepgen-ninja.c

install: halcompile /dev/disk/by-label/RPI-RP2
	mkdir -p fs_pico
	sudo umount fs_pico || true
	sudo mount /dev/disk/by-label/RPI-RP2 fs_pico
	sudo cp build/stepper-ninja-*.uf2 fs_pico || true
	sudo umount fs_pico
	rmdir fs_pico
