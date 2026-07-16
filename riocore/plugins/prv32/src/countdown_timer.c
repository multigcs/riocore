/* Copyright 2024 Grug Huhler
 *
 * License: SPDX BSD-2-Clause.
 */

#include "rio.h"

void cdt_wbyte0(const unsigned char value) {
  *CDT_COUNTER_B0 = value;
}

void cdt_wbyte1(const unsigned char value) {
  *CDT_COUNTER_B1 = value;
}

void cdt_wbyte2(const unsigned char value) {
  *CDT_COUNTER_B2 = value;
}

void cdt_wbyte3(const unsigned char value) {
  *CDT_COUNTER_B3 = value;
}

void cdt_whalf0(const unsigned short value) {
  *CDT_COUNTER_H0 = value;
}

void cdt_whalf2(const unsigned short value) {
  *CDT_COUNTER_H2 = value;
}

void cdt_write(const unsigned int value) {
  *CDT_COUNTER = value;
}

unsigned int cdt_read(void) {
  return *CDT_COUNTER;
}

void cdt_delay(const unsigned int value) {
  cdt_write(value);
  while (*CDT_COUNTER) {}
}
