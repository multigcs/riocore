import importlib


class Toolchain:
    def __init__(self, config):
        self.config = config

    def generate(self, path):
        pins_generator = importlib.import_module(f".pins", f"riocore.generator.pins.qdf")
        pins_generator.Pins(self.config).generate(path)

        verilogs = " ".join(self.config["verilog_files"])

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("PROJECT   := rio")
        makefile_data.append("TOP       := rio")
        makefile_data.append(f"VERILOGS  := {verilogs}")
        makefile_data.append("")
        makefile_data.append("all: obj_dir/V$(TOP)")
        makefile_data.append("")
        makefile_data.append("obj_dir/V$(TOP): $(VERILOGS)")
        makefile_data.append("	verilator --cc --exe --build -j 0 -Wall main.cpp $(TOP).v")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	rm -rf obj_dir")
        makefile_data.append("")
        makefile_data.append("")
        open(f"{path}/Makefile", "w").write("\n".join(makefile_data))

        top_arguments = []
        for pname in sorted(list(self.config["pinlists"])):
            pins = self.config["pinlists"][pname]
            for pin in pins:
                if pin[1].startswith("EXPANSION"):
                    continue
                if pin[1] == "USRMCLK":
                    continue

                top_arguments.append(
                    {
                        "dir": pin[2].lower(),
                        "name": pin[0],
                    }
                )

        main_cpp = []
        main_cpp.append(
            """
#include "Vrio.h"
#include "verilated.h"

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#define BUFFER_BIT 40
#define BUFFER_BYTES (BUFFER_BIT / 8)

int main(int argc, char** argv) {

    uint8_t spi_tx[BUFFER_BYTES] = {0x74, 0x69, 0x72, 0x77};
    uint8_t spi_rx[BUFFER_BYTES];
    int spi_rx_num = 0;
    int spi_rx_bit = 0;
    int spi_rx_cs = 1;

    VerilatedContext* contextp = new VerilatedContext;
    contextp->commandArgs(argc, argv);
    Vrio* rio = new Vrio{contextp};
    rio->BLINK_LED = 0;
    rio->DIN0 = 0;
    rio->DOUT0 = 0;
    rio->DOUT1 = 0;
    rio->INTERFACE_SPI_MOSI = 0;
    rio->INTERFACE_SPI_MISO = 0;
    rio->INTERFACE_SPI_SCK = 0;
    rio->INTERFACE_SPI_SSEL = 0;
    rio->sysclk = 0;
    rio->eval();

    int counter = 0;
    int last = 0;
    while (!contextp->gotFinish()) {
        rio->sysclk = 1 - rio->sysclk;
        rio->eval();
        rio->sysclk = 1 - rio->sysclk;
        rio->eval();

        if (rio->BLINK_LED != last) {
            fprintf(stdout, "BLINK_LED=%i ", rio->BLINK_LED);
            fprintf(stdout, "DOUT0=%i ", rio->DOUT0);
            fprintf(stdout, "DOUT1=%i ", rio->DOUT1);
            fprintf(stdout, "INTERFACE_SPI_MISO=%i ", rio->INTERFACE_SPI_MISO);
            fprintf(stdout, "\\n");
        }
        last = rio->BLINK_LED;

        if (counter++ > 100000) {
            counter = 0;
            if (rio->INTERFACE_SPI_SSEL == 0) {
                if (rio->INTERFACE_SPI_SCK == 0) {
                    if (spi_rx_bit < 8) {
                        if ((spi_tx[spi_rx_num] & (1<<(7-spi_rx_bit))) > 0) {
                            rio->INTERFACE_SPI_MOSI = 1;
                        } else {
                            rio->INTERFACE_SPI_MOSI = 0;
                        }
                    }
                    rio->INTERFACE_SPI_SCK = 1;
                } else if (spi_rx_num < BUFFER_BYTES) {
                    if (spi_rx_bit < 8) {
                        if (rio->INTERFACE_SPI_MISO == 1) {
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
                            } else {
                                spi_rx[spi_rx_num] = 0;
                            }
                        }
                    }
                    if (spi_rx_num < BUFFER_BYTES) {
                        rio->INTERFACE_SPI_SCK = 0;
                    }
                } else {
                    rio->INTERFACE_SPI_SSEL = 1;
                    spi_rx_bit = 0;
                    spi_rx_num = 0;
                }
            } else if (rio->INTERFACE_SPI_SSEL == 1) {
                int fd_tx = open("/dev/shm/verilog.tx", O_RDONLY);
                read(fd_tx, spi_tx, BUFFER_BYTES);
                close(fd_tx);
                spi_rx_bit = 0;
                spi_rx_num = 0;
                spi_rx[spi_rx_num] = 0;
                rio->INTERFACE_SPI_SSEL = 0;
                rio->INTERFACE_SPI_SCK = 0;
            }
        }
    }
    delete rio;
    delete contextp;
    return 0;
}

        """
        )

        open(f"{path}/main.cpp", "w").write("\n".join(main_cpp))
