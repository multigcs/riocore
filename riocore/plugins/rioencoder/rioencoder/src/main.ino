
#include <HardwareSerial.h>
#include <Wire.h>
#include "AS5600.h"

AS5600 as5600;
uint16_t angle_last = 0;
int16_t angle_diff = 0;
uint16_t i = 0;

struct s_package_t {
    int32_t revs;
    uint16_t angle;
    uint16_t csum;
};
const int package_t_size = sizeof(s_package_t);

union package_t{
    s_package_t values;
    byte data[package_t_size];
};
volatile package_t package;



void setup() {
    // init serial 2Mbit
    Serial.begin(2000000);
    while (!Serial);

    // init i2c 1Mhz
    Wire.begin(8, 9);
    Wire.setClock(1000000UL);

    // init values
    package.values.revs = 0;
    package.values.angle = 0;
    package.values.csum = 0;
    angle_last = as5600.readAngle();
}

void loop() {
    // get angle from sensor
    package.values.angle = as5600.readAngle();

    // count revolutions
    angle_diff = package.values.angle - angle_last;
    if (angle_diff < -2048) {{
        package.values.revs++;
    }} else if (angle_diff > 2048) {{
        package.values.revs--;
    }}
    angle_last = package.values.angle;

    // calc checksum
    package.values.csum = 0;
    for (i = 0; i < 6; i++) {
        package.values.csum ^= package.data[i];
    }

    // send package
    Serial.write((byte *)package.data, package_t_size);
}

