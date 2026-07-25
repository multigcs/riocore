/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause. */

#ifndef _GPIO_H
#define _GPIO_H

#define GPIO_IN 0
#define GPIO_OUT 1

extern void gpio_init(void);
extern void gpio_set_dir(unsigned char gpio, unsigned char direction);
extern void gpio_out_set_val(unsigned char gpio, unsigned char val);
extern unsigned char gpio_in_get_val(unsigned char gpio);

#endif
