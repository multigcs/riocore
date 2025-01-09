# LX9MicroBoard
**LX9MicroBoard - Spartan6 devboard
on my debian12, it works with openFPGAloader**

* URL: [https://www.avnet.com/opasdata/d120001/medias/docus/178/PB-AES-S6MB-LX9-G-V1.pdf](https://www.avnet.com/opasdata/d120001/medias/docus/178/PB-AES-S6MB-LX9-G-V1.pdf)
* Toolchain: [ise](../../generator/toolchains/ise/README.md)
* Family: xc6
* Type: xc6slx9-csg324
* Package: csg324
* Flashcmd: openFPGALoader -v -c usb-blaster --fpga-part xc6slx9csg324 -f rio.bit
* Clock: 100.000Mhz (Pin:C10)
* Example-Configs: [LX9MicroBoard](../../configs/LX9MicroBoard)

![board.png](board.png)

