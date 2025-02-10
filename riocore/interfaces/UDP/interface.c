
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#define SEND_TIMEOUT_US 10
#define RECV_TIMEOUT_US 10
#define READ_PCK_DELAY_NS 1000
#define READ_PCK_TIMEOUT_MS 2

static int udpSocket;
static int errCount;
struct sockaddr_in dstAddr, srcAddr;
struct hostent *server;

int udp_init(const char *dstAddress, int dstPort, int srcPort) {
    int ret;

    // Create a UDP socket
    udpSocket = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpSocket < 0) {
        rtapi_print("ERROR: can't open socket: %s\n", strerror(errno));
        return -errno;
    }

    bzero((char*) &dstAddr, sizeof(dstAddr));
    dstAddr.sin_family = AF_INET;
    dstAddr.sin_addr.s_addr = inet_addr(dstAddress);
    dstAddr.sin_port = htons(dstPort);

    bzero((char*) &srcAddr, sizeof(srcAddr));
    srcAddr.sin_family = AF_INET;
    srcAddr.sin_addr.s_addr = htonl(INADDR_ANY);
    srcAddr.sin_port = htons(srcPort);

    rtapi_print("INFO: listening on udp port: %s:%i\n", "0.0.0.0", srcPort);

    // bind the local socket to SCR_PORT
    ret = bind(udpSocket, (struct sockaddr *) &srcAddr, sizeof(srcAddr));
    if (ret < 0) {
        rtapi_print("ERROR: can't bind: %s\n", strerror(errno));
        return -errno;
    }

    // Connect to send and receive only to the server_addr
    ret = connect(udpSocket, (struct sockaddr*) &dstAddr, sizeof(struct sockaddr_in));
    if (ret < 0) {
        rtapi_print("ERROR: can't connect: %s\n", strerror(errno));
        return -errno;
    }

    struct timeval timeout;
    timeout.tv_sec = 0;
    timeout.tv_usec = RECV_TIMEOUT_US;

    ret = setsockopt(udpSocket, SOL_SOCKET, SO_RCVTIMEO, (char*) &timeout, sizeof(timeout));
    if (ret < 0) {
        rtapi_print("ERROR: can't set receive timeout socket option: %s\n", strerror(errno));
        return -errno;
    }

    timeout.tv_usec = SEND_TIMEOUT_US;
    ret = setsockopt(udpSocket, SOL_SOCKET, SO_SNDTIMEO, (char*) &timeout,
                     sizeof(timeout));
    if (ret < 0) {
        rtapi_print("ERROR: can't set send timeout socket option: %s\n", strerror(errno));
        return -errno;
    }

    return 0;
}

void udp_tx(uint8_t *txBuffer, uint16_t size) {
    // Send datagram
    send(udpSocket, txBuffer, size, 0);
}

int udp_rx(uint8_t *rxBuffer, uint16_t size) {
    int i;
    int ret;
    long t1;
    long t2;
    uint8_t rxBufferTmp[1024];

    for (i = 0; i < 1024; i++) {
        rxBufferTmp[i] = 0;
    }

    // Receive incoming datagram
    t1 = rtapi_get_time();
    do {
        ret = recv(udpSocket, rxBufferTmp, size * 2, 0);
        if (ret < 0) {
            rtapi_delay(READ_PCK_DELAY_NS);
        }
        t2 = rtapi_get_time();
    }
    while ((ret < 0) && ((t2 - t1) < READ_PCK_TIMEOUT_MS * 1000 * 1000));

    if (ret > 0) {
        errCount = 0;
        if (ret == size) {
            memcpy(rxBuffer, rxBufferTmp, size);
        } else {
            rtapi_print("wrong size = %d\n", ret);
            for (i = 0; i < ret; i++) {
                rtapi_print("%d ", rxBufferTmp[i]);
            }
            rtapi_print("\n");
        }
        /*
        printf("rx:");
        for (i = 0; i < ret; i++) {
            printf(" %d,", rxBuffer[i]);
        }
        printf("\n");
        */
    } else {
        errCount++;
        // rtapi_print("Ethernet TIMEOUT: N = %d (ret: %d)\n", errCount, ret);
    }

    return ret;
}

void udp_exit(void) {
}
