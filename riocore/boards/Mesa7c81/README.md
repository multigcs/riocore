# Mesa7c81
**Mesa7c81 over SPI - WIP**

## Write bitfile via spi
```
echo 25 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio25/direction
echo 1 > /sys/class/gpio/gpio25/value
flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=7000 -w rio-2048.bin
echo 0 > /sys/class/gpio/gpio25/value
```


* URL: [https://eusurplus.com/index.php?route=product/product&product_id=131](https://eusurplus.com/index.php?route=product/product&product_id=131)
* Toolchain: [ise](../../generator/toolchains/ise/README.md)
* Family: xc6
* Type: xc6slx9-2tqg144
* Package: tqg144
* Flashcmd: openFPGALoader -v -c usb-blaster --fpga-part xc6slx9tqg144 -f rio.bit
* Clock: 50.000Mhz -> PLL -> 100.000Mhz (Pin:P50)
* Example-Configs: [Mesa7c81](../../configs/Mesa7c81)

![board.png](board.png)

