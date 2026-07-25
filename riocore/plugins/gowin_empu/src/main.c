
#include "gpio.h"

int main() {
  unsigned char val = 1;
  
  gpio_init();
  gpio_set_dir(0, GPIO_OUT);
  gpio_out_set_val(0, val);

  while (1) {
    val = 1 - val;
    gpio_out_set_val(0, val);

    for (int i = 0; i < 100000; i++) {
        asm("nop");
    }

  }
  
  return 0;
}
