# Tangbob
<img align="right" height="320" src="board.png">
Tangbob with one 5x china BOB

* Board: [Tangbob](https://github.com/multigcs/riocore/blob/main/riocore/boards/Tangbob/README.md)
* Config-Path: tests/unit/data/full/Tangbob.json
* Output-Path: tests/unit/output/Tangbob
* Toolchain: gowin
* Protocol: UDP

## Axis/Joints
| Axis | Joint | Plugin | Home-Seq. |
| --- | --- | --- | --- |
| X | 0 | stepdir0 ([stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md)) | 2 | 
| Y | 1 | stepdir1 ([stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md)) | 2 | 
| Z | 2 | stepdir2 ([stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md)) | 1 | 

## Plugins
| Type | Info | Instance | Image |
| --- | --- | --- | --- |
| [breakout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/breakout/README.md) | 5Axis China-BOB | china-bob5x0 | <img src="breakout.png" height="48"> |
| [w5500](https://github.com/multigcs/riocore/blob/main/riocore/plugins/w5500/README.md) | udp interface for host comunication | w55000 | <img src="w5500.png" height="48"> |
| [wled](https://github.com/multigcs/riocore/blob/main/riocore/plugins/wled/README.md) | ws2812b interface | wled0 | <img src="wled.png" height="48"> |
| [modbus](https://github.com/multigcs/riocore/blob/main/riocore/plugins/modbus/README.md) | generic modbus plugin | modbus0 | <img src="modbus.png" height="48"> |
| [blink](https://github.com/multigcs/riocore/blob/main/riocore/plugins/blink/README.md) | blinking output pin | blink0 | <img src="blink.png" height="48"> |
| [i2cbus](https://github.com/multigcs/riocore/blob/main/riocore/plugins/i2cbus/README.md) | I2C-Bus | i2cbus0 | <img src="i2cbus.png" height="48"> |
| [stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md) | step/dir output for stepper drivers | stepdir0, stepdir1, stepdir2 | <img src="stepdir.png" height="48"> |
| [bitin](https://github.com/multigcs/riocore/blob/main/riocore/plugins/bitin/README.md) | single input pin | bitin0, bitin1, bitin2 | <img src="bitin.png" height="48"> |
