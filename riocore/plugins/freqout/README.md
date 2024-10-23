# freqout
**frequency output**

to output variable frequency signals

Keywords: frequency


![image.png](image.png)

## Basic-Example:
```
{
    "type": "freqout",
    "pins": {
        "freq": {
            "pin": "0"
        }
    }
}
```

## Pins:
*FPGA-pins*
### freq:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### frequency:
output frequency

 * type: float
 * direction: output
 * min: 0
 * max: 1000000
 * unit: Hz


## Interfaces:
*transport layer*
### frequency:

 * size: 32 bit
 * direction: output


## Full-Example:
```
{
    "type": "freqout",
    "name": "",
    "pins": {
        "freq": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "frequency": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "frequency",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * [freqout.v](freqout.v)
