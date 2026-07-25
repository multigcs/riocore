/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause.
 *
 * Don't trust this to be complete.  For example, only the main
 * stack gets set. 
 */
        .cpu cortex-m3
        .eabi_attribute 20, 1
        .eabi_attribute 21, 1
        .eabi_attribute 23, 3
        .eabi_attribute 24, 1
        .eabi_attribute 25, 1
        .eabi_attribute 26, 1
        .eabi_attribute 30, 1
        .eabi_attribute 34, 1
        .eabi_attribute 18, 4
        .arch armv7-m
        .syntax unified
        .thumb

	.text
	/* Interrupt vector table: Gowin doc IPUG922-1.1E */
	.word 0x20004000  /* main stack ptr at end of 16384 bytes of SRAM */
	.word _start+1    /*  1: reset, +1 sets bit for thumb mode */
	.word 0           /*  2: NMI */
	.word 0           /*  3: hard fault */
	.word 0           /*  4: mem manage */
	.word 0           /*  5: bus fault */
	.word 0           /*  6: usage fault */
	.word 0           /*  7: res */
	.word 0           /*  8: res */
	.word 0           /*  9: res */
	.word 0           /* 10: res */
	.word 0           /* 11: svcall */
	.word 0           /* 12: debug mon */
	.word 0           /* 13: res */
	.word 0           /* 14: pend SV */
	.word 0           /* 15: sys tick */
	.word 0           /* 16: UART0 RX and TX */
	.word 0           /* 17: UART1 RX and TX */
	.word 0           /* 18: timer 0 */
	.word 0           /* 19: timer 1 */
	.word 0           /* 20: GPIO port 0 combined */
	.word 0           /* 21: UART0,1 overflow */
	.word 0           /* 22: RTC */
	.word 0           /* 23: I2C */
	.word 0           /* 24: int 8 */
	.word 0           /* 25: ETH */
	.word 0           /* 26: int 10 */
	.word 0           /* 27: int 11 */
	.word 0           /* 28: int 12 */
	.word 0           /* 29: int 13 */
	.word 0           /* 30: int 14 */
	.word 0           /* 31: int 15 */
	.word 0           /* 32: GPIO0_0 */
	.word 0           /* 33: GPIO0_1 */
	.word 0           /* 34: GPIO0_2 */
	.word 0           /* 35: GPIO0_3 */
	.word 0           /* 36: GPIO0_4 */
	.word 0           /* 37: GPIO0_5 */
	.word 0           /* 38: GPIO0_6 */
	.word 0           /* 39: GPIO0_7 */
	.word 0           /* 40: GPIO0_8 */
	.word 0           /* 41: GPIO0_9 */
	.word 0           /* 42: GPIO0_10 */
	.word 0           /* 43: GPIO0_11 */
	.word 0           /* 44: GPIO0_12 */
	.word 0           /* 45: GPIO0_13 */
	.word 0           /* 46: GPIO0_14 */
	.word 0           /* 47: GPIO0_15 */
	.word 0           /* 48: User int 0 */
	.word 0           /* 49: User int 1 */
	.word 0           /* 50: User int 2 */
	.word 0           /* 51: User int 3 */
	.word 0           /* 52: User int 4 */
	.word 0           /* 53: User int 5 */
	.word 0           /* 54: User int 6 */
	.word 0           /* 55: User int 7 */
	.word 0           /* 56: User int 8 */
	.word 0           /* 57: User int 9 */
	.word 0           /* 58: User int 10 */
	.word 0           /* 59: User int 11 */
	.word 0           /* 60: User int 12 */
	.word 0           /* 61: User int 13 */
	.word 0           /* 62: User int 14 */
	.word 0           /* 63: User int 15 */

/* start of normal execution, calls main */

	.global _start
_start:
	bl cont_startup
stuck:  b stuck
