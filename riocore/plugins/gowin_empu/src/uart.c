/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause. */

#include "uart.h"

#define UART_BASE 0x40004000

#define UART_DATA(N) (*((volatile unsigned int *) (UART_BASE + 0x00 + N)))
#define UART_STATE(N) (*((volatile unsigned int *) (UART_BASE + 0x04 + N)))
#define UART_CTRL(N) (*((volatile unsigned int *) (UART_BASE + 0x08 + N)))
#define UART_INT(N) (*((volatile unsigned int *) (UART_BASE + 0x0c + N)))
#define UART_BAUDDIV(N) (*((volatile unsigned int *) (UART_BASE + 0x10 + N)))

/* min bauddiv is 16 */

void uart_init(const unsigned short uart, const int bauddiv)
{
  UART_BAUDDIV(uart) = bauddiv;
  /* enable RX and TX */
  UART_CTRL(uart) = 3;
}

void uart_putchar(const unsigned short uart, const char c)
{
  UART_DATA(uart) = c;
  /* await char being sent */
  while (UART_STATE(uart) & 1) {}
}

void uart_puts(const unsigned short uart, const char *str)
{
  char c;

  while ((c = *str++) != 0) uart_putchar(uart, c);
}

char uart_getchar(const unsigned short uart)
{
  /* await presence of character */
  while ((UART_STATE(uart) & 2) == 0) {}

  return UART_DATA(uart);
}

void uart_print_hex(const unsigned short uart, unsigned int val)
{
  char ch;
  int i;

  for (i = 0; i < 8; i++) {
    ch = (val & 0xf0000000) >> 28;
    uart_putchar(uart, "0123456789abcdef"[ch]);
    val = val << 4;
  }
}
