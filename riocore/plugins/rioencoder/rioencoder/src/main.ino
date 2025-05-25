
#include <HardwareSerial.h>
#include <Wire.h>
#include "AS5600.h"

AS5600 as5600;

void setup() {
    Serial.begin(2000000);
    while (!Serial);

    Wire.begin(21, 22);
    Wire.setClock(1000000UL);
}

void loop() {
    uint16_t angle = as5600.readAngle();
    byte MSB = (angle >> 8) & 0xFF;
    byte LSB = angle & 0xFF;
    byte CSUM = (MSB | LSB);
    byte msg[3];

    msg[0] = MSB;
    msg[1] = LSB;
    msg[2] = CSUM;

    Serial.write(msg, 3);
}

