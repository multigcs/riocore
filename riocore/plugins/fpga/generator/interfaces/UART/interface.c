
int uart_serial_fd = -1;

int uart_set_interface_attribs (int fd, int speed) {
    struct termios tty;
    if (tcgetattr (fd, &tty) != 0) {
        rtapi_print("ERROR: can't setup serial: %s\n", strerror(errno));
        return errno;
    }
    cfsetospeed (&tty, speed);
    cfsetispeed (&tty, speed);
    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8 | CLOCAL | CREAD;
    tty.c_iflag = 0;         // disable input processing
    tty.c_lflag = 0;         // no signaling chars, no echo,
    tty.c_oflag = 0;         // no output processing
    tty.c_cc[VMIN]  = 0;     // read doesn't block
    tty.c_cc[VTIME] = 0;     // 0.x seconds read timeout

    if (tcsetattr (fd, TCSANOW, &tty) != 0) {
        rtapi_print("ERROR: can't setup serial: %s\n", strerror(errno));
        return errno;
    }
    return 0;
}

int uart_init(char *serialPort) {
    rtapi_print("Info: Initialize serial connection: %s\n", serialPort);
    uart_serial_fd = open (serialPort, O_RDWR | O_NOCTTY | O_SYNC | O_NDELAY);
    if (uart_serial_fd < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR,"usb setup error\n");
        return errno;
    }
    uart_set_interface_attribs(uart_serial_fd, SERIAL_BAUD);
    return 0;
}

void uart_tx(uint8_t *txBuffer, uint16_t size) {
#ifdef SERIAL_CSUM
    uint8_t n = 0;
    uint8_t csum = 0;
    for (n = 0; n < size; n++) {
        csum += txBuffer[n];
    }
    txBuffer[size] = csum;
    write(uart_serial_fd, txBuffer, size + 1);
#else
    write(uart_serial_fd, txBuffer, size);
#endif
}

int uart_rx(uint8_t *rxBuffer, uint16_t size, uint8_t uart_async) {
    int rec = 0;
    int cnt = 0;
#ifdef SERIAL_CSUM
    int n = 0;
    // clear buffer
    memset(rxBuffer, 0, size + 1);
    if (uart_async == 1) {
        rec = read(uart_serial_fd, rxBuffer, size * 2);
    } else {
        while((rec = read(uart_serial_fd, rxBuffer, size * 2)) < size + 1 && cnt++ < 250) {
            usleep(1000);
        }
    }
    if (rec == size + 1) {
        uint8_t csum = 0;
        for (n = 0; n < size; n++) {
            csum += rxBuffer[n];
        }
        if (csum == rxBuffer[size]) {
            rec -= 1;
        } else {
            printf("CSUM_ERROR: %i != %i\n", csum, rxBuffer[size]);
            rec = -1;
        }
    }
#else
    while((rec = read(uart_serial_fd, rxBuffer, size * 2)) < size && cnt++ < 250) {
        usleep(1000);
    }
#endif
    return rec;
}

void uart_exit(void) {
}
