# ICEBreakerV1.0e
<img align="right" height="320" src="board.png">
Small and low cost FPGA educational and development board

* Board: [ICEBreakerV1.0e](https://github.com/multigcs/riocore/blob/main/riocore/boards/ICEBreakerV1.0e/README.md)
* Config-Path: tests/unit/data/full/ICEBreakerV1.0e.json
* Output-Path: tests/unit/output/ICEBreakerV1.0e
* Toolchain: icestorm
* Protocol: UDP

## Axis/Joints
| Axis | Joint | Plugin | Home-Seq. |
| --- | --- | --- | --- |
| X | 0 | stepdir0 ([stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md)) | 0 | 
| Y | 1 | stepdir1 ([stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md)) | 0 | 
| Z | 2 | stepdir2 ([stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md)) | 0 | 

## Plugins
| Type | Info | Instance | Image |
| --- | --- | --- | --- |
| [w5500](https://github.com/multigcs/riocore/blob/main/riocore/plugins/w5500/README.md) | udp interface for host comunication | w55000 | <img src="w5500.png" height="48"> |
| [stepdir](https://github.com/multigcs/riocore/blob/main/riocore/plugins/stepdir/README.md) | step/dir output for stepper drivers | stepdir0, stepdir1, stepdir2 | <img src="stepdir.png" height="48"> |
| [blink](https://github.com/multigcs/riocore/blob/main/riocore/plugins/blink/README.md) | blinking output pin | blink0 | <img src="blink.png" height="48"> |
| [bitin](https://github.com/multigcs/riocore/blob/main/riocore/plugins/bitin/README.md) | single input pin | bitin0, bitin1, bitin2, bitin3, bitin4, bitin5 | <img src="bitin.png" height="48"> |
| [bitout](https://github.com/multigcs/riocore/blob/main/riocore/plugins/bitout/README.md) | singe bit output pin | bitout0, bitout1 | <img src="bitout.png" height="48"> |
