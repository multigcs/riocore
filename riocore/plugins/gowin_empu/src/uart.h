/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause. */

#ifndef _UART_H
#define _UART_H

#define UART0 (0)
#define UART1 (0x1000)

extern void uart_init(const unsigned short uart, const int bauddiv);
extern void uart_putchar(const unsigned short uart, const char c);
extern void uart_puts(const unsigned short uart, const char *str);
extern char uart_getchar(const unsigned short uart);
extern void uart_print_hex(const unsigned short uart, unsigned int val);

#endif

    
