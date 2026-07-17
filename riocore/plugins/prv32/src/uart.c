/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause.
*/

#include "rio.h"

void uart_set_div(unsigned int uart, unsigned int div) {
  volatile int delay;

  *UART0_DIV = div;

  /* Need to delay a little */
  for (delay = 0; delay < 200; delay++) {}
}

void uart_print_hex(unsigned int uart, unsigned int val) {
  char ch;
  int i;

  for (i = 0; i < 8; i++) {
    ch = (val & 0xf0000000) >> 28;
    *UART0_DATA = "0123456789abcdef"[ch];
    val = val << 4;
  }
}

char uart_getchar(unsigned int uart) {
  unsigned char ch;

  /* UART gives 0xff when empty */
  while ((ch = *UART0_DATA) == 0xff) {}

  return(ch);
}

void uart_putchar(unsigned int uart, char ch) {
  *UART0_DATA = ch;
}
  
void uart_puts(unsigned int uart, char *s) {
  while (*s != 0) *UART0_DATA = *s++;
}
