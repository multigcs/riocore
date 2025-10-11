#!/usr/bin/env python3
#
# loadusr -Wn rpii2c ./rpii2c.py PREFIX TYPE ADDR CFG [PREFIX TYPE ADDR CFG [...]]
# loadusr -Wn rpii2c ./rpii2c.py  io0 pcf8574 0x20 00000000  io1 pcf8574 0x21 11111111  adc0 ads1115 0x48 0
#  pcf8574 CFG: 8bit invert-mask
#  ads1115 CFG: unused
#  lm75    CFG: unused
#


import sys
import time
import hal
import smbus

ads1115_setupRegister1 = [
    "100",  # 128 SPS
    "0",  # Traditional Comparator
    "0",  # Active low alert
    "0",  # Non latching
    "11",  # Disable comparator
]
ads1115_setupRegister2 = [
    "1",  # Start Conversion
    "100",  # Channel 0 Single ended
    "001",  # FSR +- 4.096v
    "1",  # Single shot mode
]


configs = []
for an in range((len(sys.argv) - 1) // 4):
    instance = sys.argv[an * 4 + 1]
    device = sys.argv[an * 4 + 2]
    addr = sys.argv[an * 4 + 3]
    invert_mask = sys.argv[an * 4 + 4]
    configs.append((instance, device, int(addr[2:], 16), invert_mask))


h = hal.component("rpii2c")
for config in configs:
    instance, device, addr, invert_mask = config
    if device == "pcf8574":
        for pn in range(8):
            h.newpin(f"{instance}.p{pn:02d}-in", hal.HAL_BIT, hal.HAL_OUT)
            h.newpin(f"{instance}.p{pn:02d}-in-not", hal.HAL_BIT, hal.HAL_OUT)
            h.newpin(f"{instance}.p{pn:02d}-out", hal.HAL_BIT, hal.HAL_IN)
            h[f"{instance}.p{pn:02d}-out"] = True
    elif device == "lm75":
        h.newpin(f"{instance}.temp_c", hal.HAL_FLOAT, hal.HAL_OUT)
        h.newpin(f"{instance}.temp_f", hal.HAL_FLOAT, hal.HAL_OUT)
    elif device == "ads1115":
        for an in range(4):
            h.newpin(f"{instance}.adc{an}", hal.HAL_FLOAT, hal.HAL_OUT)
h.ready()

bus = smbus.SMBus(1)

while True:
    for config in configs:
        instance, device, addr, invert_mask = config
        try:
            if device == "lm75":
                bus.write_byte_data(addr, 0x01, 0x00)

        except Exception as error:
            print(f"ERROR: device init {device} @ 0x{addr:02x}: {error}")

    for config in configs:
        instance, device, addr, invert_mask = config
        try:
            if device == "pcf8574":
                out_bits = ""
                for pn in range(8):
                    value = 0
                    if h[f"{instance}.p{pn:02d}-out"]:
                        value = 1
                    if invert_mask[pn] == "1":
                        value = 1 - value
                    out_bits += str(value)

                out_data = int(out_bits, 2)
                # print(addr[2:], out_bits, out_data)
                bus.write_byte(addr, out_data)

                data = bus.read_byte(addr)
                data = f"{data:08b}"
                for pn in range(8):
                    value = False
                    if data[7 - pn] == "1":
                        value = True
                    if invert_mask[pn] == "1":
                        value = not value
                    h[f"{instance}.p{pn:02d}-in"] = value
                    h[f"{instance}.p{pn:02d}-in-not"] = not value

            elif device == "lm75":
                data = bus.read_i2c_block_data(addr, 0x00, 2)
                cTemp = (data[0] * 256 + (data[1] & 0x80)) / 128
                if cTemp > 255:
                    cTemp -= 512
                h[f"{instance}.temp_c"] = cTemp * 0.5
                h[f"{instance}.temp_f"] = cTemp * 1.8 + 32

            elif device == "ads1115":
                for an in range(4):
                    ads1115_setupRegister2[1] = f"{4 + an:03b}"
                    reg1 = int("".join(ads1115_setupRegister1), 2)
                    reg2 = int("".join(ads1115_setupRegister2), 2)
                    bus.write_i2c_block_data(addr, 1, [reg2, reg1])
                    for rn in range(5):
                        data = bus.read_i2c_block_data(addr, 1, 1)
                        if (data[0] & (1 << 7)) != 0:
                            break
                        time.sleep(0.01)
                    data = bus.read_i2c_block_data(addr, 0, 2)
                    value = (data[0] << 8) + data[1]
                    value = (value >> 3) / 1000.0
                    h[f"{instance}.adc{an}"] = value

        except Exception as error:
            print(f"ERROR: device read {device} @ 0x{addr:02x}: {error}")

    time.sleep(0.01)
