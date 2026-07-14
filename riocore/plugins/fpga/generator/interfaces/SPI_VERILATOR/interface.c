#include "rtapi.h"			/* RTAPI realtime OS API */
#include "rtapi_app.h"		/* RTAPI realtime module decls */

#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <fcntl.h>
#include <time.h>
#include <sys/ioctl.h>
#include <linux/ioctl.h>
#include <sys/stat.h>
#include <linux/types.h>

int spi_init(char *spi_device) {
    rtapi_print("Info: Initialize SHM connection\n");
    return 0;
}

void spi_exit(void) {
}

int spi_trx(uint8_t *txBuffer, uint8_t *rxBuffer, uint16_t size) {
    int fd_tx = open("/dev/shm/verilog.tx", O_WRONLY);
    write(fd_tx, txBuffer, size);
    close(fd_tx);
    int fd_rx = open("/dev/shm/verilog.rx", O_RDONLY);
    read(fd_rx, rxBuffer, size);
    close(fd_rx);
    return size;;
}

