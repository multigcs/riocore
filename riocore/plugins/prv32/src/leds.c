/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause.
*/

#include "leds.h"

#define LEDS ((volatile unsigned char *) 0x80000000)

void set_leds(unsigned char val)
{
  *LEDS = val;
}

unsigned char get_leds(void)
{
  return *LEDS;
}
