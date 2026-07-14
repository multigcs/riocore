import importlib
import os
import shutil
import sys


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = self.config["output_path"]
        self.riocore_path = config["riocore_path"]
        self.toolchain_path = self.config.get("toolchains_json", {}).get("verilator", "")
        if self.toolchain_path and not self.toolchain_path.endswith("bin"):
            self.toolchain_path = os.path.join(self.toolchain_path, "bin")

    @classmethod
    def info(cls):
        return {
            "url": "https://www.veripool.org/verilator/",
            "info": "verilog simulation",
            "description": "",
        }

    def generate(self, path):
        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.qdf")
        pins_generator.Pins(self.config).generate(path)
        if sys.platform == "linux":
            verilator = shutil.which("verilator")
            if verilator is None:
                print("WARNING: can not found toolchain installation in PATH: verilator")

        verilogs = " ".join(self.config["verilog_files"])

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("# Toolchain: Verilator")
        makefile_data.append("")
        if self.toolchain_path:
            makefile_data.append(f"PATH     := {self.toolchain_path}:$(PATH)")
            makefile_data.append("")
        makefile_data.append("PROJECT   := rio")
        makefile_data.append("TOP       := rio")
        makefile_data.append(f"VERILOGS  := {verilogs}")
        makefile_data.append(f"CLK_SPEED := {float(self.config['speed']) / 1000000}")
        makefile_data.append("")
        makefile_data.append("all: clean build load")
        makefile_data.append("")
        makefile_data.append("build: obj_dir/V$(TOP)")
        makefile_data.append("")
        makefile_data.append("obj_dir/V$(TOP): $(VERILOGS)")
        makefile_data.append("	verilator --cc --exe --build -j 0 -Wall main.cpp $(TOP).v")
        makefile_data.append("")
        makefile_data.append("load:")
        makefile_data.append("	obj_dir/Vrio")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf obj_dir")
        makefile_data.append("")
        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))

        buffersize = 0
        pinlist = []
        riov_data = open(os.path.join(path, "rio.v"), "r").read()
        for _line in riov_data.split("\n"):
            line = _line.strip()
            if line.startswith("PIN") and (" <- " in line or " -> " in line):
                pinlist.append(line.split()[0])
            elif line.startswith("localparam BUFFER_SIZE_"):
                buffersize = max(buffersize, int(line.split()[5]))

        main_cpp = []
        main_cpp.append("""
#include "Vrio.h"
#include "verilated.h"

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
""")

        main_cpp.append(f"#define BUFFER_BIT {buffersize * 8}")
        main_cpp.append(f"#define BUFFER_BYTES {buffersize}")

        main_cpp.append("""
int main(int argc, char** argv) {

    uint8_t spi_tx[BUFFER_BYTES] = {0x74, 0x69, 0x72, 0x77};
    uint8_t spi_rx[BUFFER_BYTES];
    int spi_rx_num = 0;
    int spi_rx_bit = 0;
    int spi_rx_cs = 1;

    VerilatedContext* contextp = new VerilatedContext;
    contextp->commandArgs(argc, argv);
    Vrio* rio = new Vrio{contextp};
""")

        for pin in pinlist:
            main_cpp.append(f"    rio->{pin} = 0;")

        main_cpp.append("""
    rio->PININ_SPI0_MOSI = 0;
    rio->PINOUT_SPI0_MISO = 0;
    rio->PININ_SPI0_SCLK = 0;
    rio->PININ_SPI0_SEL = 0;
    rio->sysclk_in = 0;
    rio->eval();

    int print_counter = 0;
    int spi_counter = 0;
    while (!contextp->gotFinish()) {
        rio->sysclk_in = 1 - rio->sysclk_in;
        rio->eval();
        rio->sysclk_in = 1 - rio->sysclk_in;
        rio->eval();

        if (print_counter++ > 1000000) {
            print_counter = 0;

""")

        for pin in pinlist:
            if pin.startswith("PINOUT_") and "SPI" not in pin:
                main_cpp.append(f'            fprintf(stdout, "{pin}=%i ", rio->{pin});')

        main_cpp.append("""
            fprintf(stdout, "\\n");
        }
        if (spi_counter++ > 1000) {
            spi_counter = 0;
            if (rio->PININ_SPI0_SEL == 0) {
                if (rio->PININ_SPI0_SCLK == 0) {
                    if (spi_rx_bit < 8) {
                        if ((spi_tx[spi_rx_num] & (1<<(7-spi_rx_bit))) > 0) {
                            rio->PININ_SPI0_MOSI = 1;
                        } else {
                            rio->PININ_SPI0_MOSI = 0;
                        }
                    }
                    rio->PININ_SPI0_SCLK = 1;
                } else if (spi_rx_num < BUFFER_BYTES) {
                    if (spi_rx_bit < 8) {
                        if (rio->PINOUT_SPI0_MISO == 1) {
                            spi_rx[spi_rx_num] |= (1<<(7-spi_rx_bit));
                        }
                        spi_rx_bit++;
                        if (spi_rx_bit == 8) {
                            spi_rx_bit = 0;
                            spi_rx_num++;
                            if (spi_rx_num == BUFFER_BYTES) {
                                int fd_rx = open("/dev/shm/verilog.rx", O_WRONLY);
                                write(fd_rx, spi_rx, BUFFER_BYTES);
                                close(fd_rx);

                                /*
                                int i = 0;
                                printf("data2(%i): ", BUFFER_BYTES);
                                for (i = 0; i < BUFFER_BYTES; i++) {
                                    printf("%d ", spi_rx[i]);
                                }
                                printf("\\n");
                                */

                            } else {
                                spi_rx[spi_rx_num] = 0;
                            }
                        }
                    }
                    if (spi_rx_num < BUFFER_BYTES) {
                        rio->PININ_SPI0_SCLK = 0;
                    }
                } else {
                    rio->PININ_SPI0_SEL = 1;
                    spi_rx_bit = 0;
                    spi_rx_num = 0;
                }
            } else if (rio->PININ_SPI0_SEL == 1) {
                int fd_tx = open("/dev/shm/verilog.tx", O_RDONLY);
                read(fd_tx, spi_tx, BUFFER_BYTES);
                close(fd_tx);

                spi_rx_bit = 0;
                spi_rx_num = 0;
                spi_rx[spi_rx_num] = 0;
                rio->PININ_SPI0_SEL = 0;
                rio->PININ_SPI0_SCLK = 0;
            }
        }
    }
    delete rio;
    delete contextp;
    return 0;
}

""")
        open(os.path.join(path, "main.cpp"), "w").write("\n".join(main_cpp))
