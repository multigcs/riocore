
#include <rio.h>

int main() {
    int i;
    unsigned char v, ch;

    uart_set_div(2300); /* 27000000/9600 */
    uart_puts("hello world\r\n");

    gpio_dir(0, GPIO_OUT);
    gpio_dir(1, GPIO_OUT);
    gpio_dir(2, GPIO_OUT);
    gpio_dir(3, GPIO_OUT);
    gpio_dir(4, GPIO_OUT);
    gpio_dir(5, GPIO_OUT);

    gpio_set(0, GPIO_HI);
    gpio_set(1, GPIO_HI);
    gpio_set(2, GPIO_HI);
    gpio_set(3, GPIO_HI);
    gpio_set(4, GPIO_HI);
    gpio_set(5, GPIO_HI);

    gpio_dir(6, GPIO_IN);
    gpio_dir(7, GPIO_IN);

    i = 0;
    while (1) {
    uart_puts("Loop\r\n");

        *RIO_VIN = *RIO_VOUT + 20;

        gpio_toggle(0);
        gpio_set(4, gpio_get(6));
        gpio_set(5, gpio_get(7));

        cdt_delay(2700000);
        i += 1;
    }

    return 0;
}
