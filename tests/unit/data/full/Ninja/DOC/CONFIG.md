# Ninja


* Board: [](https://github.com/multigcs/riocore/blob/main/riocore/boards//README.md)
* Config-Path: tests/unit/data/full/Ninja.json
* Output-Path: tests/unit/output/Ninja

## Axis/Joints
| Axis | Joint | Plugin | Home-Seq. |
| --- | --- | --- | --- |
| X | 0 | ninja1 ([ninja](https://github.com/multigcs/riocore/blob/main/riocore/plugins/ninja/README.md)) | 2 | 
| Y | 1 | ninja2 ([ninja](https://github.com/multigcs/riocore/blob/main/riocore/plugins/ninja/README.md)) | 2 | 
| Z | 2 | ninja3 ([ninja](https://github.com/multigcs/riocore/blob/main/riocore/plugins/ninja/README.md)) | 1 | 

## Plugins
| Type | Info | Instance | Image |
| --- | --- | --- | --- |
| [ninja](https://github.com/multigcs/riocore/blob/main/riocore/plugins/ninja/README.md) | stepgen-ninja | ninja0, ninja1, ninja2, ninja3, ninjapwmgen0 | <img src="ninja.png" height="48"> |
| [gpioin](https://github.com/multigcs/riocore/blob/main/riocore/plugins/gpioin/README.md) | gpio input | gpioin0, gpioin1, gpioin2 | <img src="gpioin.png" height="48"> |
| [gpioout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/gpioout/README.md) | gpio output | gpioout2, gpioout3, gpiooutgpioout | <img src="gpioout.png" height="48"> |
| [halinput](https://github.com/multigcs/riocore/blob/main/riocore/plugins/halinput/README.md) | joypad support | halinputhalinput | <img src="halinput.png" height="48"> |
