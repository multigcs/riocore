# CYC1000


* Config-Path: tests/unit/data/full/CYC1000.json
* Output-Path: tests/unit/output/CYC1000

## Axis/Joints
| Axis | Joint | Plugin | Home-Seq. |
| --- | --- | --- | --- |
| X | 0 | stepdir0 ([stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md)) | 0 | 

## Plugins
| Type | Info | Instance | Image |
| --- | --- | --- | --- |
| [fpga](https://github.com/multigcs/riocore/blob/main/riocore/plugins/fpga/README.md) | TEI0003 | board0 | - |
| [blink](https://github.com/multigcs/riocore/blob/main/riocore/plugins/blink/README.md) | blinking output pin | blink0 | <img src="blink.png" height="48"> |
| [bitin](https://github.com/multigcs/riocore/blob/main/riocore/plugins/bitin/README.md) | single input pin | bitin0 | <img src="bitin.png" height="48"> |
| [bitout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/bitout/README.md) | singe bit output pin | bitout0, bitout1 | <img src="bitout.png" height="48"> |
| [pwmout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/pwmout/README.md) | pwm output | pwmout0 | <img src="pwmout.png" height="48"> |
| [w5500](https://github.com/multigcs/riocore/blob/main/riocore/plugins/w5500/README.md) | udp interface for host comunication | w55000 | <img src="w5500.png" height="48"> |
| [stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md) | step/dir output for stepper drivers | stepdir0 | <img src="stepdir.png" height="48"> |
