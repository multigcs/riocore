/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause.
*/

#include "rio.h"

#ifdef UART0_DIV

void uart_set_div(unsigned int uart, unsigned int div) {
  volatile int delay;

  *UART0_DIV = div;

  /* Need to delay a little */
//  for (delay = 0; delay < 200; delay++) {}
}

#ifdef ENABLE_MUL
#ifdef ENABLE_DIV
void uart_set_baud(unsigned int uart, unsigned int baud) {
    uart_set_div(uart, F_CPU / baud);
}
#endif
#endif

void uart_print_hex(unsigned int uart, unsigned int val) {
  char ch;
  int i;

  for (i = 0; i < 8; i++) {
    ch = (val & 0xf0000000) >> 28;
    *UART0_DATA = "0123456789abcdef"[ch];
    val = val << 4;
  }
}

#ifdef ENABLE_MUL
#ifdef ENABLE_DIV
void uart_print_dec(unsigned int uart, unsigned int val) {
	char buffer[10];
	char *p = buffer;
	while (val || p == buffer) {
		*(p++) = val % 10;
		val = val / 10;
	}
	while (p != buffer) {
		*((volatile uint32_t*)UART0_DATA) = '0' + *(--p);
	}
}
#endif
#endif

char uart_getchar(unsigned int uart) {
    return *UART0_DATA;
}

char uart_available(unsigned int uart) {
    return (*UART0_DATA)>>8;
}

void uart_putc(unsigned int uart, char ch) {
    *UART0_DATA = ch;
}
  
void uart_puts(unsigned int uart, char *s) {
    while (*s != 0) *UART0_DATA = *s++;
}

#endif
