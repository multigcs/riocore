# RPI4


* Config-Path: tests/unit/data/full/RPI4.json
* Output-Path: tests/unit/output/RPI4

## Axis/Joints
| Axis | Joint | Plugin | Home-Seq. |
| --- | --- | --- | --- |
| X | 0 | stepgen0 ([stepgen](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepgen/README.md)) | 2 | 
| Y | 1 | stepgen1 ([stepgen](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepgen/README.md)) | 2 | 
| Z | 2 | stepgen2 ([stepgen](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepgen/README.md)) | 1 | 

## Plugins
| Type | Info | Instance | Image |
| --- | --- | --- | --- |
| [breakout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/breakout/README.md) | rpi-db25hat | rpi-db25hat0, china-bob5x0 | <img src="breakout.png" height="48"> |
| [stepgen](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepgen/README.md) | software step pulse generation | stepgen0, stepgen1, stepgen2 | <img src="stepgen.png" height="48"> |
| [gpioout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/gpioout/README.md) | gpio output | gpioout0, gpioout1 | <img src="gpioout.png" height="48"> |
| [gpioin](https://github.com/multigcs/riocore/blob/main/riocore/plugins/gpioin/README.md) | gpio input | gpioin0, gpioin1, gpioin2, gpioin3, gpioin4 | <img src="gpioin.png" height="48"> |
| [pwmgen](https://github.com/multigcs/riocore/blob/main/riocore/plugins/pwmgen/README.md) | software PWM/PDM generation | pwmgen0 | <img src="pwmgen.png" height="48"> |
| [rpigpio](https://github.com/multigcs/riocore/blob/main/riocore/plugins/rpigpio/README.md) | gpio support | rpigpio0 | <img src="rpigpio.png" height="48"> |
