
int uart_serial_fd = -1;

int uart_set_interface_attribs (int fd, int speed, int parity) {
    struct termios tty;
    if (tcgetattr (fd, &tty) != 0) {
        rtapi_print("ERROR: can't setup usb: %s\n", strerror(errno));
        return errno;
    }
    cfsetospeed (&tty, speed);
    cfsetispeed (&tty, speed);
    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
    tty.c_iflag &= ~IGNBRK;         // disable break processing
    tty.c_lflag = 0;                // no signaling chars, no echo,
    tty.c_oflag = 0;                // no remapping, no delays
    tty.c_cc[VMIN]  = 0;            // read doesn't block
    tty.c_cc[VTIME] = 0;            // 0.5 seconds read timeout
    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl
    tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls, enable reading
    tty.c_cflag &= ~(PARENB | PARODD);      // shut off parity
    tty.c_cflag |= parity;
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CRTSCTS;

    if (tcsetattr (fd, TCSANOW, &tty) != 0) {
        rtapi_print("ERROR: can't setup usb: %s\n", strerror(errno));
        return errno;
    }
    return 0;
}

int uart_init(void) {
    rtapi_print("Info: Initialize serial connection: %s\n", SERIAL_PORT);
    uart_serial_fd = open (SERIAL_PORT, O_RDWR | O_NOCTTY | O_SYNC);
    if (uart_serial_fd < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR,"usb setup error\n");
        return errno;
    }
    uart_set_interface_attribs(uart_serial_fd, SERIAL_BAUD, 0);
}

int uart_trx(uint8_t *txBuffer, uint8_t *rxBuffer, uint16_t size) {
    int n = 0;
    int cnt = 0;
    int rec = 0;
    
    printf("tx:");
    for (n = 0; n < size; n++) {
        printf(" %d,", txBuffer[n]);
    }
    printf("\n");

    int ret = write(uart_serial_fd, txBuffer, BUFFER_SIZE);
    tcdrain(uart_serial_fd);
    tcflush(uart_serial_fd, TCIFLUSH);


    while((rec = read(uart_serial_fd, rxBuffer, size)) < size && cnt++ < 250) {
        usleep(1000);
    }

    printf("########################\n");
    printf("rec %d %d \n", rec, cnt);

    printf("rx:");
    for (n = 0; n < rec; n++) {
        printf(" %d,", rxBuffer[n]);
    }
    printf("\n");


    return 1;
}

