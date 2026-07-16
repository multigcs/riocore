
#include "rio.h"

int main() {
  int i;
  unsigned char v, ch;

  set_leds(0);

  uart_set_div(2300); /* 27000000/9600 */

  uart_puts("hello world\r\n");

  i = 0;
  while (1) {
    uart_puts("Loop\r\n");
    v = get_leds();
    set_leds(v+1);

    *RIO_VIN = *RIO_VOUT + 20;

    cdt_delay(2700000);
    i += 1;
  }
  
  return 0;
}
