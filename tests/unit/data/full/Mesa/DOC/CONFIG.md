# Mesa


* Config-Path: tests/unit/data/full/Mesa.json
* Output-Path: tests/unit/output/Mesa

## Axis/Joints
| Axis | Joint | Plugin | Home-Seq. |
| --- | --- | --- | --- |
| X | 0 | mesa1 ([mesa](https://github.com/multigcs/riocore/blob/main/riocore/plugins/mesa/README.md)) | 2 | 
| Y | 1 | mesa2 ([mesa](https://github.com/multigcs/riocore/blob/main/riocore/plugins/mesa/README.md)) | 2 | 
| Z | 2 | mesa3 ([mesa](https://github.com/multigcs/riocore/blob/main/riocore/plugins/mesa/README.md)) | 1 | 

## Plugins
| Type | Info | Instance | Image |
| --- | --- | --- | --- |
| [breakout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/breakout/README.md) | 5Axis China-BOB | china-bob5x0 | <img src="breakout.png" height="48"> |
| [mesa](https://github.com/multigcs/riocore/blob/main/riocore/plugins/mesa/README.md) | mesa | mesa0, mesa1, mesa2, mesa3, mesapwmgen0 | <img src="mesa.png" height="48"> |
| [gpioin](https://github.com/multigcs/riocore/blob/main/riocore/plugins/gpioin/README.md) | gpio input | gpioin0, gpioin1, gpioin2 | <img src="gpioin.png" height="48"> |
| [gpioout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/gpioout/README.md) | gpio output | gpioout2, gpiooutgpioout | <img src="gpioout.png" height="48"> |
