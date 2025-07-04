
#include <esp_wifi.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include <AS5600.h>
#include <driver/adc.h>

#define VREF 4424 // ADC-Calibration

AS5600 as5600;
uint16_t angle_last = 0;
int16_t angle_diff = 0;
uint16_t i = 0;

struct s_package_t {
    int32_t revs;
    uint16_t angle;
    uint16_t temperature;
    uint16_t csum;
};
const int package_t_size = sizeof(s_package_t);

union package_t{
    s_package_t values;
    byte data[package_t_size];
};
volatile package_t package;


void setup() {
    // set CPU Clock
    // setCpuFrequencyMhz(160);

    // force disable wifi
    esp_err_t results = esp_wifi_stop();

    // init serial 2Mbit
    Serial.begin(2000000);
    while (!Serial);

    // init i2c 1Mhz
    Wire.begin(8, 9);
    Wire.setClock(1000000UL);

    // rw pin
    pinMode(10, OUTPUT);
    digitalWrite(10, HIGH);

    // init values
    package.values.revs = 0;
    package.values.angle = 0;
    package.values.temperature = 0;
    package.values.csum = 0;
    angle_last = as5600.readAngle(0);

    adc1_config_channel_atten((adc1_channel_t)0, (adc_atten_t)ADC_11db);
}

void loop() {
    
    // own loop to prevent delays (5ms each 2s)
    while(1) {

        // read temerature
        int adcVal = VREF - adc1_get_raw((adc1_channel_t)0);
        float Rt = 10.0 * adcVal / (VREF - adcVal);
        float tempK = 1 / (log(Rt / 10) / 3950 + 1 / (273.15 + 25));
        float tempC = tempK - 273.15;
        package.values.temperature = (int16_t)(tempC * 10);

        // get angle from sensor
        package.values.angle = as5600.readAngle(1);

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
        for (i = 0; i < 8; i++) {
            package.values.csum ^= package.data[i];
        }

        // send package
        Serial.write((byte *)package.data, 10);

    }

}

