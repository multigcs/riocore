
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <simulator.h>
#include <riocore.h>

#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>


#ifdef MODBUS_SERIAL_PORT
int MODBUS_SERIAL_PORT = -1;
#endif

void modbus_init() {
#ifdef MODBUS_SERIAL_PORT
    struct termios tty;
    MODBUS_SERIAL_PORT = open(MODBUS_SERIAL_PORT, O_RDWR);
    if (MODBUS_SERIAL_PORT < 0) {
        printf("Error %i from open: %s\n", errno, strerror(errno));
    }
    if(tcgetattr(MODBUS_SERIAL_PORT, &tty) != 0) {
        printf("Error %i from tcgetattr: %s\n", errno, strerror(errno));
    }
    tty.c_cflag &= ~PARENB; // Clear parity bit, disabling parity (most common)
    tty.c_cflag &= ~CSTOPB; // Clear stop field, only one stop bit used in communication (most common)
    tty.c_cflag &= ~CSIZE; // Clear all bits that set the data size
    tty.c_cflag |= CS8; // 8 bits per byte (most common)
    tty.c_cflag &= ~CRTSCTS; // Disable RTS/CTS hardware flow control (most common)
    tty.c_cflag |= CREAD | CLOCAL; // Turn on READ & ignore ctrl lines (CLOCAL = 1)
    tty.c_lflag &= ~ICANON;
    tty.c_lflag &= ~ECHO; // Disable echo
    tty.c_lflag &= ~ECHOE; // Disable erasure
    tty.c_lflag &= ~ECHONL; // Disable new-line echo
    tty.c_lflag &= ~ISIG; // Disable interpretation of INTR, QUIT and SUSP
    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // Turn off s/w flow ctrl
    tty.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL); // Disable any special handling of received bytes
    tty.c_oflag &= ~OPOST; // Prevent special interpretation of output bytes (e.g. newline chars)
    tty.c_oflag &= ~ONLCR; // Prevent conversion of newline to carriage return/line feed
    tty.c_cc[VTIME] = 10;    // Wait for up to 1s (10 deciseconds), returning as soon as any data is received.
    tty.c_cc[VMIN] = 0;
    cfsetispeed(&tty, B9600);
    cfsetospeed(&tty, B9600);
    if (tcsetattr(MODBUS_SERIAL_PORT, TCSANOW, &tty) != 0) {
        printf("Error %i from tcsetattr: %s\n", errno, strerror(errno));
    }
#endif
}

uint16_t crc16_update(uint16_t crc, uint8_t a) {
	int i;
	crc ^= (uint16_t)a;
	for (i = 0; i < 8; ++i) {
		if (crc & 1)
			crc = (crc >> 1) ^ 0xA001;
		else
			crc = (crc >> 1);
	}
	return crc;
}

int modbus_sim(uint8_t channel, uint8_t *frame, uint8_t len, uint8_t *ret_frame) {
    uint8_t addr = frame[0];
    if (addr == 11) {
        uint8_t fcode = frame[1];
        if (fcode == 15) { // Force Multiple Coils (Function Code=15)
            uint16_t daddr = (frame[2]<<8) | frame[3];
            uint16_t ncoils = (frame[4]<<8) | frame[5];
            uint8_t nbytes = frame[6];
            printf("modbus set coils: %i %i %i %i: ", addr, fcode, daddr, ncoils);
            for (uint8_t byte = 0; byte < nbytes; byte++) {
                for (uint8_t bit = 0; bit < 8; bit++) {
                    if ((frame[7 + byte] & (1<<bit)) != 0) {
                        printf("1 ");
                    } else {
                        printf("0 ");
                    }
                }
            }
            printf("\n");
            return -1;
        } else if (fcode == 2) { // Read Input Status (Function Code=02)
            uint16_t crc = 0xFFFF;
            uint16_t frame_len = 4;
            uint16_t daddr = (frame[2]<<8) | frame[3];
            ret_frame[0] = 11;
            ret_frame[1] = 2;
            ret_frame[2] = 1;
            ret_frame[3]++;
            for (uint8_t i = 0; i < frame_len; i++) {
                crc = crc16_update(crc, ret_frame[i]);
            }
            ret_frame[frame_len] = crc & 0xFF;
            ret_frame[frame_len + 1] = crc>>8 & 0xFF;
            // printf("---ret_frame: ");
            // for (int i = 0; i < frame_len + 2; i++) {
            //     printf("%i ", ret_frame[i]);
            // }
            // printf("\n");
            return frame_len;
        }
    }
}

int modbus(uint8_t channel, uint8_t *frame, uint8_t len, uint8_t *ret_frame) {
#ifdef MODBUS_SERIAL_PORT
    if (channel == 0) {
        write(MODBUS_SERIAL_PORT, frame, len);
    }
#endif
    return modbus_sim(channel, frame, len, ret_frame);
}


