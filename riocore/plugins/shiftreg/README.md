# shiftreg
**Expansion to add I/O's via shiftregister's**


do not use this for high frequency signals !!!

jitter measured with a EPM240 as 40bit Shiftreg:
```
@10Mhz clock and 5 byte data ~= 3.7us jitter
```

## Output-Expansion with 74HC595:

| EXP | 74HC595 | FUNC |
| --- | --- | --- |
| out | 14 | DS |
| in |  | |
| sclk | 11 | SH_CP / SRCLK |
| load | 12 | ST_CP / RCLK |

## Input-Expansion with 74HC165:

| EXP | 74HC165 | FUNC |
| --- | --- | --- |
| out |  | |
| in |  | SER |
| sclk | 2 | CLK |
| load |  | SH/LD |

### LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA
[![LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA](https://img.youtube.com/vi/NlLd5CRCOac/0.jpg)](https://www.youtube.com/shorts/NlLd5CRCOac "LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA")

        

Keywords: expansion digital io


![image.png](image.png)

## Basic-Example:
```
{
    "type": "shiftreg",
    "pins": {
        "out": {
            "pin": "0"
        },
        "in": {
            "pin": "1"
        },
        "sclk": {
            "pin": "2"
        },
        "load": {
            "pin": "3"
        }
    }
}
```

## Pins:
*FPGA-pins*
### out:
output data (DS on 74HC595)

 * direction: output

### in:
input data (SER_OUT on 74HC165)

 * direction: input

### sclk:
input data (CLK on 74HC165/ CH_CP/SRCLK on 74HC595)

 * direction: output

### load:
input data (SH/LD on 74HC165/ ST_CP/RCLK on 74HC595)

 * direction: output


## Options:
*user-options*
### speed:
interface clock

 * type: int
 * min: 100000
 * max: 10000000
 * default: 1000000

### bits:
number of bits (IO's)

 * type: int
 * min: 8
 * max: 1024
 * default: 8

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Full-Example:
```
{
    "type": "shiftreg",
    "speed": 1000000,
    "bits": 8,
    "name": "",
    "pins": {
        "out": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "in": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "sclk": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "load": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {}
}
```

## Verilogs:
 * [shiftreg.v](shiftreg.v)
