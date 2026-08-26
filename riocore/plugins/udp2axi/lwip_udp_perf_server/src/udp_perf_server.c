#include "udp_perf_server.h"

extern struct netif server_netif;
static struct udp_pcb *pcb;

void print_app_header(void) {
    xil_printf("UDP server listening on port %d\r\n", UDP_CONN_PORT);
}

#define AXI_BASE 0x40000000
static void udp_recv_perf_traffic(void *arg, struct udp_pcb *tpcb, struct pbuf *p_rx, const ip_addr_t *addr, u16_t port) {
    u8_t n = 0;
    u8_t data[100];
    struct pbuf *p_tx;
    u8_t dlen = p_rx->len;
    u8_t *payload = (u8_t*)p_rx->payload;

    //xil_printf("RX: ");
    for (n = 0; n < dlen; n++) {
        //xil_printf("%i, ", payload[n]);
        *((volatile unsigned char *) AXI_BASE + n) = payload[n];
    }
    //xil_printf("\r\n");
    pbuf_free(p_rx);

    //xil_printf("TX: ");
    for (n = 0; n < dlen; n++) {
        //xil_printf("%i, ", data[n]);
        data[n] = *((volatile unsigned char *) AXI_BASE + n);
    }
    //xil_printf("\r\n");
    p_tx = pbuf_alloc(PBUF_TRANSPORT, dlen, PBUF_POOL);
    if (p_tx != NULL) {
        pbuf_take(p_tx, (char*)data, dlen);
        udp_sendto(tpcb, p_tx, addr, port);
        udp_disconnect(tpcb);
        pbuf_free(p_tx);
    }

    return;
}

void start_application(void) {
    err_t err;

    pcb = udp_new();
    if (!pcb) {
        xil_printf("UDP server: Error creating PCB. Out of Memory\r\n");
        return;
    }

    err = udp_bind(pcb, IP_ADDR_ANY, UDP_CONN_PORT);
    if (err != ERR_OK) {
        xil_printf("UDP server: Unable to bind to port");
        xil_printf(" %d: err = %d\r\n", UDP_CONN_PORT, err);
        udp_remove(pcb);
        return;
    }

    udp_recv(pcb, udp_recv_perf_traffic, NULL);

    return;
}
