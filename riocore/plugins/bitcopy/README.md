# bitcopy
**copy a bit/pin to an other output pin**

outputs a copy of a bit/pin

```mermaid
graph LR;
    Origin-->Original Modifiers-Pipeline-->Original-Pin;
    Origin-->BitCopy Modifiers-Pipeline-->BitCopy-Pin;
```


Example:
* you can create an inverted output pin for symetric signals
* 
        

Keywords: pin bit copy


![image.png](image.png)

## Basic-Example:
```
{
    "type": "bitcopy",
    "pins": {
        "bit": {
            "pin": "0"
        }
    }
}
```

## Pins:
*FPGA-pins*
### bit:

 * direction: output


## Options:
*user-options*
### origin:
Origin Bit/Pin

 * type: vpins
 * default: ERROR

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
    "type": "bitcopy",
    "origin": "ERROR",
    "name": "",
    "pins": {
        "bit": {
            "pin": "0",
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
