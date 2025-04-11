import os

import riocore

riocore_path = os.path.dirname(riocore.__file__)


class gpio_rpi:
    IMAGE = riocore_path + "/files/rpi-gpio.png"
    pinout = (
        "3V3",
        "5V",
        "GPIO2",
        "5V",
        "GPIO3",
        "GND",
        "GPIO4",
        "GPIO14",
        "GND",
        "GPIO15",
        "GPIO17",
        "GPIO18",
        "GPIO27",
        "GND",
        "GPIO22",
        "GPIO23",
        "3V3",
        "GPIO24",
        "GPIO10",
        "GND",
        "GPIO9",
        "GPIO25",
        "GPIO11",
        "GPIO8",
        "GND",
        "GPIO7",
        "GPIO0",
        "GPIO1",
        "GPIO5",
        "GND",
        "GPIO6",
        "GPIO12",
        "GPIO19",
        "GND",
        "GPIO19",
        "GPIO16",
        "GPIO26",
        "GPIO20",
        "GND",
        "GPIO21",
    )

    def __init__(self, gid, gpio):
        self.inputs = []
        self.outputs = []
        self.gid = gid
        self.gpio = gpio
        self.mode = gpio.get("mode", "out")
        rpi_pins = gpio.get("pins", {})
        inputs = rpi_pins.get("inputs", [])
        outputs = rpi_pins.get("outputs", [])

        for pin_num in range(0, 40):
            pin_name = self.pinout[pin_num]
            if pin_name in inputs:
                self.inputs.append(f"hal_pi_gpio.pin-{pin_num + 1:02d}-in")
            elif pin_name in outputs:
                self.outputs.append(f"hal_pi_gpio.pin-{pin_num + 1:02d}-out")

    def slotpins(self, x_offset, networks={}):
        pins = {}
        direction = "all"
        for pin_num in range(0, 40):
            pin_name = self.pinout[pin_num]
            if pin_name.startswith("GPIO"):
                x_pos = x_offset + 40 + (pin_num % 2) * 110
                y_pos = 60 + (pin_num // 2) * 20.5
                halname = ""
                pn = int(pin_name.replace("GPIO", ""))
                if f"hal_pi_gpio.pin-{pin_num + 1:02d}-in" in self.inputs:
                    halname = f"hal_pi_gpio.pin-{pin_num + 1:02d}-in"
                elif f"hal_pi_gpio.pin-{pin_num + 1:02d}-out" in self.outputs:
                    halname = f"hal_pi_gpio.pin-{pin_num + 1:02d}-out"

                pins[pin_name] = {
                    "title": pin_name,
                    "pin": halname,
                    "pos": [int(x_pos), int(y_pos)],
                    "direction": direction,
                    "slotname": "rpi_gpio",
                    "net": networks.get(halname, ""),
                }

        return pins

    def loader(cls, gpio_config):
        output = []
        rpigpios = []
        for gpio in gpio_config:
            if gpio.get("type") == "rpi":
                rpi_pins = gpio.get("pins", {})
                rpigpios.append(rpi_pins)

        if rpigpios and False:
            output.append("# rpi gpio component")
            inputs = rpigpios[0].get("inputs", [])
            outputs = rpigpios[0].get("outputs", [])
            resets = rpigpios[0].get("reset", [])
            args = []
            if inputs:
                args.append(f"inputs={','.join(inputs)}")
            if outputs:
                args.append(f"outputs={','.join(outputs)}")
            if resets:
                args.append(f"resets={','.join(resets)}")
            output.append(f"loadrt hal_gpio {' '.join(args)}")
            output.append("addf hal_gpio.read base-thread")
            output.append("addf hal_gpio.write base-thread")
            output.append("")

        elif rpigpios:
            output.append("# hal_pi_gpio component")
            inputs = rpigpios[0].get("inputs", [])
            outputs = rpigpios[0].get("outputs", [])
            resets = rpigpios[0].get("reset", [])
            mask_dir = 0
            mask_exclude = 0
            for bit_num, pin_num in enumerate(range(2, 28)):
                pname = f"GPIO{pin_num}"
                if pname in outputs:
                    mask_dir |= 1 << bit_num
                elif pname not in inputs:
                    mask_exclude |= 1 << bit_num

            args = []
            args.append(f"dir={mask_dir}")
            args.append(f"exclude={mask_exclude}")
            output.append(f"loadrt hal_pi_gpio {' '.join(args)}")
            output.append("addf hal_pi_gpio.read base-thread")
            output.append("addf hal_pi_gpio.write base-thread")
            output.append("")
        return "\n".join(output)


class gpio_parport:
    IMAGE = riocore_path + "/files/db25.png"
    mode_outputs = {
        "in": [1, 14, 16, 17],
        "out": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
        "epp": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
        "x": [2, 3, 4, 5, 6, 7, 8, 9],
    }

    def __init__(self, gid, gpio):
        self.inputs = []
        self.outputs = []
        self.gid = gid
        self.gpio = gpio
        self.mode = gpio.get("mode", "out")
        self.outpins = self.mode_outputs.get(self.mode.split()[-1])

        for pin_num in range(1, 18):
            if pin_num in self.outpins:
                direction = "output"
            else:
                direction = "input"
            pin_name = f"parport.{gid}.pin-{pin_num:02d}-{direction.replace('put', '')}"
            if pin_num in self.outpins:
                self.outputs.append(pin_name)
            else:
                self.inputs.append(pin_name)

    def slotpins(self, x_offset, networks={}):
        pins = {}
        for pin_num in range(1, 18):
            title = f"P{self.gid}.{pin_num}"
            if pin_num in self.outpins:
                direction = "output"
            else:
                direction = "input"
            pin_name = f"parport.{self.gid}.pin-{pin_num:02d}-{direction.replace('put', '')}"
            if pin_num < 14:
                x_pos = x_offset + 20
                y_pos = 97 + (pin_num - 1) * 32.4
            else:
                x_pos = x_offset + 110
                y_pos = 97 + 15 + (pin_num - 14) * 32.4

            pins[title] = {
                "title": title,
                "pin": pin_name,
                "pos": [int(x_pos), int(y_pos)],
                "direction": direction,
                "slotname": f"parport.{self.gid}",
                "net": networks.get(pin_name, ""),
            }

        return pins

    def loader(cls, gpio_config):
        output = []
        parports = []
        for gpio in gpio_config:
            if gpio.get("type") == "parport":
                pp_addr = gpio.get("address", "0x378")
                pp_mode = gpio.get("mode", "out")
                parports.append(f"{pp_addr} {pp_mode}")

        if parports:
            output.append(f"# parport component for {len(parports)} port(s)")
            output.append(f'loadrt hal_parport cfg="{" ".join(parports)}"')
            for pn, pmode in enumerate(parports):
                output.append(f"addf parport.{pn}.read base-thread")
                output.append(f"addf parport.{pn}.write base-thread")
                output.append(f"addf parport.{pn}.reset base-thread")
                output.append(f"setp parport.{pn}.reset-time 5000")
            output.append("")

        return "\n".join(output)
