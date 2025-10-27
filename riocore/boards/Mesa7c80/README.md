# Mesa7c80
**Mesa7c80 over SPI - untested, i have no hardware**

The bitstream can be written via SPI, but you should have a USB Blaster handy so that you can flash via JTAG in an emergency.

It is also possible to operate this board with a W5500 via Ethernet, but flashing is then only possible via JTAG.

Smartserial is not supported by RIO, but the 2 ports can be used for Modbus.

* URL: [https://eusurplus.com/index.php?route=product/product&product_id=131](https://eusurplus.com/index.php?route=product/product&product_id=131)
* Toolchain: [ise](../../generator/toolchains/ise/README.md)
* Family: xc6
* Type: xc6slx9-2tqg144
* Package: tqg144
* Flashcmd: openFPGALoader -v -c usb-blaster --fpga-part xc6slx9tqg144 -f rio.bit
* Clock: 50.000Mhz -> PLL -> 100.000Mhz (Pin:P50)
* Example-Configs: [Mesa7c80](../../configs/Mesa7c80)

![board.png](board.png)

