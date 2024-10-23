# sonar
**sonar sensor for distance measurement**

to messure distance via cheap ultra-sonic sensors (like filling level of bigger water tanks)

Keywords: distance ultrasonic level oil water


![image.png](image.png)

## Basic-Example:
```
{
    "type": "sonar",
    "pins": {
        "trigger": {
            "pin": "0"
        },
        "echo": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### trigger:

 * direction: output

### echo:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### distance:
distance between sensor and object

 * type: float
 * direction: input
 * unit: cm


## Interfaces:
*transport layer*
### distance:

 * size: 32 bit
 * direction: input


## Full-Example:
```
{
    "type": "sonar",
    "name": "",
    "pins": {
        "trigger": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "echo": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "distance": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "distance",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [sonar.v](sonar.v)
