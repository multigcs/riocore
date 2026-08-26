#include <stdio.h>
#include "xparameters.h"
#include "netif/xadapter.h"
#include "platform.h"
#include "platform_config.h"
#include "lwipopts.h"
#include "xil_printf.h"
#include "sleep.h"
#include "lwip/priv/tcp_priv.h"
#include "lwip/init.h"
#include "lwip/inet.h"
#include "xil_cache.h"

extern volatile int TcpFastTmrFlag;
extern volatile int TcpSlowTmrFlag;

#define DEFAULT_IP_ADDRESS "192.168.10.119"
#define DEFAULT_IP_MASK    "255.255.255.0"
#define DEFAULT_GW_ADDRESS "192.168.10.1"

void start_application(void);
void print_app_header(void);

#if defined (__arm__) && !defined (ARMR5)
#if XPAR_GIGE_PCS_PMA_SGMII_CORE_PRESENT == 1 || XPAR_GIGE_PCS_PMA_1000BASEX_CORE_PRESENT == 1
int ProgramSi5324(void);
int ProgramSfpPhy(void);
#endif
#endif

struct netif server_netif;

static void print_ip(char *msg, ip_addr_t *ip) {
    print(msg);
    xil_printf("%d.%d.%d.%d\r\n", ip4_addr1(ip), ip4_addr2(ip), ip4_addr3(ip), ip4_addr4(ip));
}

static void print_ip_settings(ip_addr_t *ip, ip_addr_t *mask, ip_addr_t *gw) {
    print_ip("Board IP:       ", ip);
    print_ip("Netmask :       ", mask);
    print_ip("Gateway :       ", gw);
}


int main(void) {
    int err;
    struct netif *netif;
    unsigned char mac_ethernet_address[] = {0x00, 0x0a, 0x35, 0x00, 0x01, 0x02};

    netif = &server_netif;
#if defined (__arm__) && !defined (ARMR5)
#if XPAR_GIGE_PCS_PMA_SGMII_CORE_PRESENT == 1 || XPAR_GIGE_PCS_PMA_1000BASEX_CORE_PRESENT == 1
    ProgramSi5324();
    ProgramSfpPhy();
#endif
#endif

    init_platform();

    xil_printf("\r\n\r\n");
    xil_printf("-----lwIP RIOCORE UDP Server-----\r\n");

    lwip_init();

    if (!xemac_add(netif, NULL, NULL, NULL, mac_ethernet_address, PLATFORM_EMAC_BASEADDR)) {
        xil_printf("Error adding N/W interface\r\n");
        return -1;
    }
    netif_set_default(netif);

    init_timer();

    netif_set_up(netif);

    xil_printf("Configuring default IP %s \r\n", DEFAULT_IP_ADDRESS);
    err = inet_aton(DEFAULT_IP_ADDRESS, ip);
    if (!err) {
        xil_printf("Invalid default IP address: %d\r\n", err);
	}
    err = inet_aton(DEFAULT_IP_MASK, mask);
    if (!err) {
        xil_printf("Invalid default IP MASK: %d\r\n", err);
	}
    err = inet_aton(DEFAULT_GW_ADDRESS, gw);
    if (!err) {
        xil_printf("Invalid default gateway address: %d\r\n", err);
	}

    print_ip_settings(&(netif->ip_addr), &(netif->netmask), &(netif->gw));
    xil_printf("\r\n");

    print_app_header();

    start_application();
    xil_printf("\r\n");

    while (1) {
        if (TcpFastTmrFlag) {
            tcp_fasttmr();
            TcpFastTmrFlag = 0;
        }
        if (TcpSlowTmrFlag) {
            tcp_slowtmr();
            TcpSlowTmrFlag = 0;
        }
        xemacif_input(netif);
    }
    cleanup_platform();
    return 0;
}
