# prv32
**risc-v softcore**

risc-v cpu for testing

* Keywords: risc-v softcore cpu
* NEEDS: fpga

## Pins:
*FPGA-pins*
### uart_rx:

 * direction: input

### uart_tx:

 * direction: output

### led0:

 * direction: output

### led1:

 * direction: output

### led2:

 * direction: output

### led3:

 * direction: output

### led4:

 * direction: output

### led5:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### image:
hardware type

 * type: imgselect
 * default: generic

### source:
source code (asm)

 * type: multiline
 * default: 
#include "leds.h"
#include "uart.h"
#include "countdown_timer.h"


int main() {
  int i;
  unsigned char v, ch;

  set_leds(0);

  //uart_set_div(234); /* 27000000/115200 */
  uart_set_div(2812); /* 27000000/9600 */

  uart_puts("hello world\r\n");

  i = 0;
  while (1) {
    uart_puts("Loop\r\n");
    v = get_leds();
    set_leds(v+1);

    uart_set_div(2000 + i);

    cdt_delay(2700000);
    i += 1;
  }
  
  return 0;
}



## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Verilogs:
 * [countdown_timer.v](countdown_timer.v)
 * [reset.v](reset.v)
 * [tang_nano_9k_leds.v](tang_nano_9k_leds.v)
 * [gowin_sp.v](gowin_sp.v)
 * [uart_wrap.v](uart_wrap.v)
 * [simpleuart.v](simpleuart.v)
 * [picorv32.v](picorv32.v)
 * [prv32.v](prv32.v)
