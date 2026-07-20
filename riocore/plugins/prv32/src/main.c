
#include <rio.h>

int main() {


    pinMode(GPIO_LED0, OUTPUT);
    digitalWrite(GPIO_LED0, HIGH);

    RIO_BITIN = 0;

    while (1) {


        RIO_BITIN = 1 - RIO_BITIN;

        RIO_UINT8IN = 123;
        RIO_UINT16IN = 12346;
        RIO_UINT32IN = 12345678;

        RIO_INT8IN = -123;
        RIO_INT16IN = -12346;
        RIO_INT32IN = -12345678;


        digitalWrite(GPIO_LED0, TOGGLE);
        delay(100);


    }
    return 0;
}
