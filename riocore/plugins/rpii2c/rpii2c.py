#!/usr/bin/env python3
#
# loadusr -Wn rpii2c ./rpii2c.py PREFIX TYPE ADDR CFG [PREFIX TYPE ADDR CFG [...]]
# loadusr -Wn rpii2c ./rpii2c.py  io0 pcf8574 0x20 00000000  io1 pcf8574 0x21 11111111  adc0 ads1115 0x48 0
#  pcf8574 CFG: 8bit invert-mask
#  ads1115 CFG: unused
#  lm75    CFG: unused
#  hd44780 CFG: formatstring
#


import re
import sys
import time
import hal
import smbus

fmt_pattern = re.compile(r"\{(?P<val>[a-z0-9_-]*):(?P<fmt>[0-9\.]*)(?P<type>[a-z])\}")


class hd44780:
    def __init__(self, bus, addr):
        self.bus = bus
        self.addr = addr
        for cmd in (
            0x03,
            0x03,
            0x03,
            0x02,
            (0x20 | 0x08 | 0x00 | 0x00),
            (0x08 | 0x04),
            (0x04 | 0x02),
        ):
            self.writecmd(cmd)
        time.sleep(0.2)
        self.clear()
        self.display(0, 0, "     LinuxCNC       ")
        self.display(0, 1, "   i2c component    ")
        self.display(0, 2, "       2025         ")
        self.display(0, 3, "  by Oliver Dippel  ")
        time.sleep(0.3)
        self.clear()

    def write(self, data):
        self.bus.write_byte(self.addr, data | 0x08)
        time.sleep(0.0001)
        self.bus.write_byte(self.addr, data | 0x04 | 0x08)
        time.sleep(0.0005)
        self.bus.write_byte(self.addr, ((data & ~0x04) | 0x08))
        time.sleep(0.0001)

    def writecmd(self, cmd):
        self.write((cmd & 0xF0))
        self.write(((cmd << 4) & 0xF0))

    def writedata(self, cmd, mode=0):
        self.write(0x1 | (cmd & 0xF0))
        self.write(0x1 | ((cmd << 4) & 0xF0))

    def clear(self):
        self.writecmd(0x01)
        self.writecmd(0x02)

    def display(self, x, y, text):
        self.writecmd((0x80, 0xC0, 0x94, 0xD4)[y] + x)
        for char in text:
            self.writedata(ord(char))


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
    cfgstring = sys.argv[an * 4 + 4]
    configs.append((instance, device, int(addr[2:], 16), cfgstring))

devices = {}
for config in configs:
    instance, device, addr, cfgstring = config
    devices[instance] = {}

h = hal.component("rpii2c")
for config in configs:
    instance, device, addr, cfgstring = config
    if device == "pcf8574":
        for pn in range(8):
            h.newpin(f"{instance}.p{pn:02d}-in", hal.HAL_BIT, hal.HAL_OUT)
            h.newpin(f"{instance}.p{pn:02d}-in-not", hal.HAL_BIT, hal.HAL_OUT)
            h.newpin(f"{instance}.p{pn:02d}-out", hal.HAL_BIT, hal.HAL_IN)
            h[f"{instance}.p{pn:02d}-out"] = True
    elif device == "lm75":
        h.newpin(f"{instance}.temp_c", hal.HAL_FLOAT, hal.HAL_OUT)
        h.newpin(f"{instance}.temp_f", hal.HAL_FLOAT, hal.HAL_OUT)
    elif device == "hd44780":
        names = fmt_pattern.findall(cfgstring)
        if names is not None:
            vdict = {}
            keys = set()
            for val_n, parts in enumerate(sorted(set(names))):
                vdict[parts[0]] = parts
                keys.add(parts[0])
            devices[instance]["keys"] = keys
            for parts in vdict.values():
                name = parts[0]
                vfmt = parts[1]
                vtype = parts[2]
                if vfmt == "1" and vtype == "d":
                    h.newpin(f"{instance}.{name}", hal.HAL_BIT, hal.HAL_IN)
                elif vtype == "d":
                    h.newpin(f"{instance}.{name}", hal.HAL_U32, hal.HAL_IN)
                else:
                    h.newpin(f"{instance}.{name}", hal.HAL_FLOAT, hal.HAL_IN)

    elif device == "ads1115":
        for an in range(4):
            h.newpin(f"{instance}.adc{an}", hal.HAL_FLOAT, hal.HAL_OUT)
h.ready()

# init i2c bus
bus = smbus.SMBus(1)

# init i2c devices
for config in configs:
    instance, device, addr, cfgstring = config
    try:
        if device == "lm75":
            bus.write_byte_data(addr, 0x01, 0x00)
        elif device == "hd44780":
            devices[instance]["lib"] = hd44780(bus, addr)
    except Exception as error:
        print(f"ERROR: device init {device} @ 0x{addr:02x}: {error}")

while True:
    # read loop
    for config in configs:
        instance, device, addr, cfgstring = config
        try:
            if device == "pcf8574":
                out_bits = ""
                for pn in range(8):
                    value = 0
                    if h[f"{instance}.p{pn:02d}-out"]:
                        value = 1
                    if cfgstring[pn] == "1":
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
                    if cfgstring[pn] == "1":
                        value = not value
                    h[f"{instance}.p{pn:02d}-in"] = value
                    h[f"{instance}.p{pn:02d}-in-not"] = not value

            elif device == "hd44780":
                values = {}
                for key in devices[instance]["keys"]:
                    values[key] = h[f"{instance}.{key}"]
                cfgstring = cfgstring.replace("\\n", "|")
                for ln, formatstr in enumerate(cfgstring.split("|")):
                    text = formatstr.format(**values)
                    devices[instance]["lib"].display(0, ln, text)

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
