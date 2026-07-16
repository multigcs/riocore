/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause.
*/

#include "uart.h"

#define UART_DIV ((volatile unsigned char *) 0x80000008)
#define UART_DATA ((volatile unsigned char *) 0x8000000c)

void uart_set_div(unsigned int div)
{
  volatile int delay;

  *UART_DIV = div;

  /* Need to delay a little */
  for (delay = 0; delay < 200; delay++) {}
}

void uart_print_hex(unsigned int val)
{
  char ch;
  int i;

  for (i = 0; i < 8; i++) {
    ch = (val & 0xf0000000) >> 28;
    *UART_DATA = "0123456789abcdef"[ch];
    val = val << 4;
  }
}

char uart_getchar(void)
{
  unsigned char ch;

  /* UART gives 0xff when empty */
  while ((ch = *UART_DATA) == 0xff) {}

  return(ch);
}

void uart_putchar(char ch)
{
  *UART_DATA = ch;
}
  
void uart_puts(char *s)
{
  while (*s != 0) *UART_DATA = *s++;
}
