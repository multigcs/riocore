import glob
import sys
import os

riocore_path = os.path.dirname(os.path.dirname(__file__))

from riocore.generator import cclient


class Firmware:
    def __init__(self, project):
        self.project = project
        self.pio_path = os.path.join(project.config["output_path"], "Firmware")
        self.pio_src_path = os.path.join(self.pio_path, "src")
        self.pio_lib_path = os.path.join(self.pio_path, "lib", "riocore")
        project.config["riocore_path"] = riocore_path

    def generator(self, generate_pll=True):
        self.config = self.project.config.copy()
        toolchain = self.config.get("toolchain")

        os.makedirs(self.pio_src_path, exist_ok=True)
        os.makedirs(self.pio_lib_path, exist_ok=True)

        self.expansion_pins = []
        for plugin_instance in self.project.plugin_instances:
            for pin in plugin_instance.expansion_outputs():
                self.expansion_pins.append(pin)
            for pin in plugin_instance.expansion_inputs():
                self.expansion_pins.append(pin)

        self.virtual_pins = []
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"].startswith("VIRT:"):
                    pinname = pin_config["pin"]
                    if pinname not in self.virtual_pins:
                        self.virtual_pins.append(pinname)

        cclient.riocore_h(self.project, self.pio_lib_path)
        cclient.riocore_c(self.project, self.pio_lib_path)
        if toolchain == "platformio":
            self.platformio()

    def platformio(self):
        output = []
        output.append("")

        output.append("""
#define ETH_CLK_MODE ETH_CLOCK_GPIO17_OUT
#define ETH_PHY_POWER 12

#include <ETH.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>

extern "C" {
    #include <riocore.h>
}

WiFiUDP Udp;

void setup(){
    Serial.begin(115200);
    while (!Serial);

    ETH.begin();

    // setup static ip
    IPAddress myIP(192, 168, 80, 141);
    IPAddress myGW(192, 168, 80, 1);
    IPAddress mySN(255, 255, 255, 0);
    ETH.config(myIP, myGW, mySN);

    Udp.begin(SRC_PORT);

    riocore_setup();

    Serial.println("UDP2SPI Bridge for LinuxCNC - RIO");
}
""")

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            if hasattr(plugin_instance, "firmware_defines"):
                output.append(plugin_instance.firmware_defines())
        output.append("")

        output.append("void riocore_setup(void) {")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            if hasattr(plugin_instance, "firmware_setup"):
                output.append(plugin_instance.firmware_setup())
        output.append("}")
        output.append("")

        output.append("void riocore_loop(void) {")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            if hasattr(plugin_instance, "firmware_loop"):
                output.append(plugin_instance.firmware_loop())
        output.append("}")
        output.append("")

        output.append("void simulation(void) {")
        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            expansion = data_config.get("expansion", False)
            if multiplexed or expansion:
                continue
            if data_config["direction"] == "input":
                if hasattr(plugin_instance, "simulate_c"):
                    output.append(plugin_instance.simulate_c(1000, data_name))

        output.append("}")
        output.append("")

        output.append("""

void loop() {
    int packetSize = Udp.parsePacket();
    if (packetSize) {
        IPAddress remoteIp = Udp.remoteIP();
        int len = Udp.read(rxBuffer, BUFFER_SIZE);
        if (rxBuffer[0] == 0x74 && rxBuffer[1] == 0x69 && rxBuffer[2] == 0x72 && rxBuffer[3] == 0x77) {
            read_rxbuffer(rxBuffer);

            riocore_loop();

            write_txbuffer(txBuffer);
            Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
            Udp.write((uint8_t*)txBuffer, BUFFER_SIZE);
            Udp.endPacket();

            simulation();
        }
    }

    //Serial.write((uint8_t*)packetBuffer, len);
}
""")

        open(os.path.join(self.pio_src_path, "main.ino"), "w").write("\n".join(output))

        output = []
        output.append("")
        output.append("[env:esp32-evb]")
        output.append("platform = espressif32")
        output.append("board = esp32-poe-iso")
        output.append("framework = arduino")
        output.append("")
        open(os.path.join(self.pio_path, "platformio.ini"), "w").write("\n".join(output))

        print(f"writing firmware to: {self.pio_path}")

