
#define GPIO_BASE ((volatile unsigned int *) 0x100)
#define DELAY 0x20000

int main() {

    *GPIO_BASE = 1;

    while (1) {

        *GPIO_BASE = 0;
        for (int i = 0; i < DELAY; i++) {
            asm("nop");
        }

        *GPIO_BASE = 1;
        for (int i = 0; i < DELAY; i++) {
            asm("nop");
        }

    }
    return 0;
}
