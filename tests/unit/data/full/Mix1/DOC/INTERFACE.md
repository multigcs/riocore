# Interface
## Host to FPGA
| POS | SIZE | NAME |
| --- | --- | --- |
| 0 | 32bits | RX_HEADER |
| 32 | 32bits | VAROUT32_STEPDIR0_VELOCITY |
| 64 | 32bits | VAROUT32_STEPDIR1_VELOCITY |
| 96 | 1bit | VAROUT1_STEPDIR0_ENABLE |
| 97 | 1bit | VAROUT1_STEPDIR1_ENABLE |
| 98 | 1bit | VAROUT1_BITOUT0_BIT |

## FPGA to Host
| POS | SIZE | NAME |
| --- | --- | --- |
| 0 | 32bits | TX_HEADER |
| 32 | 32bits | TIMESTAMP |
| 64 | 32bits | VARIN32_STEPDIR0_POSITION |
| 96 | 32bits | VARIN32_STEPDIR1_POSITION |
| 128 | 1bit | VARIN1_BITIN0_BIT |
