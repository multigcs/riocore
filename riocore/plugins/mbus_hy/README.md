# mbus_hy

<img align="right" width="320" src="image.png">

**modbus hy vfd**

modbus hy vfd

Keywords: modbus

## Pins:
*FPGA-pins*
### MODBUS:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### address:
device address

 * type: int
 * min: 1
 * max: 255
 * default: 1

### priority:
device priority

 * type: int
 * min: 1
 * max: 9
 * default: 9

### timeout:
device timeout

 * type: int
 * min: 10
 * max: 400
 * default: 160

### delay:
device delay

 * type: int
 * min: 10
 * max: 400
 * default: 100


## Signals:
*signals/pins in LinuxCNC*
### speed_command:

 * type: float
 * direction: output
 * unit: RPM

### speed_fb_rps:

 * type: float
 * direction: input
 * unit: RPS

### spindle_at_speed_tolerance:

 * type: float
 * direction: output
 * unit: 

### spindle_forward:

 * type: bit
 * direction: output

### spindle_reverse:

 * type: bit
 * direction: output

### spindle_on:

 * type: bit
 * direction: output

### at_speed:

 * type: bit
 * direction: input
 * unit: 

### max_freq:

 * type: float
 * direction: input
 * unit: Hz

### base_freq:

 * type: float
 * direction: input
 * unit: Hz

### freq_lower_limit:

 * type: float
 * direction: input
 * unit: Hz

### rated_motor_voltage:

 * type: float
 * direction: input
 * unit: V

### rated_motor_current:

 * type: float
 * direction: input
 * unit: A

### rpm_at_50hz:

 * type: float
 * direction: input
 * unit: RPM

### rated_motor_rev:

 * type: float
 * direction: input
 * unit: RPM

### speed_fb:

 * type: float
 * direction: input
 * unit: RPM

### error_count:

 * type: float
 * direction: input
 * unit: 

### hycomm_ok:

 * type: bit
 * direction: input
 * unit: 

### frq_set:

 * type: float
 * direction: input
 * unit: Hz

### frq_get:

 * type: float
 * direction: input
 * unit: Hz

### ampere:

 * type: float
 * direction: input
 * unit: A

### rpm:

 * type: float
 * direction: input
 * unit: RPM

### dc_volt:

 * type: float
 * direction: input
 * unit: V

### ac_volt:

 * type: float
 * direction: input
 * unit: V

### vfd_errors:
vfd

 * type: float
 * direction: input


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "mbus_hy",
    "pins": {
        "MODBUS": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "mbus_hy",
    "name": "",
    "address": 1,
    "priority": 9,
    "timeout": 160,
    "delay": 100,
    "pins": {
        "MODBUS": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "speed_command": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "speed_command",
                "section": "outputs",
                "type": "scale"
            }
        },
        "speed_fb_rps": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "speed_fb_rps",
                "section": "inputs",
                "type": "meter"
            }
        },
        "spindle_at_speed_tolerance": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "spindle_at_speed_tolerance",
                "section": "outputs",
                "type": "scale"
            }
        },
        "spindle_forward": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "spindle_forward",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "spindle_reverse": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "spindle_reverse",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "spindle_on": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "spindle_on",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "at_speed": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "at_speed",
                "section": "inputs",
                "type": "led"
            }
        },
        "max_freq": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "max_freq",
                "section": "inputs",
                "type": "meter"
            }
        },
        "base_freq": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "base_freq",
                "section": "inputs",
                "type": "meter"
            }
        },
        "freq_lower_limit": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "freq_lower_limit",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rated_motor_voltage": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rated_motor_voltage",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rated_motor_current": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rated_motor_current",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rpm_at_50hz": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rpm_at_50hz",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rated_motor_rev": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rated_motor_rev",
                "section": "inputs",
                "type": "meter"
            }
        },
        "speed_fb": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "speed_fb",
                "section": "inputs",
                "type": "meter"
            }
        },
        "error_count": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "error_count",
                "section": "inputs",
                "type": "meter"
            }
        },
        "hycomm_ok": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "hycomm_ok",
                "section": "inputs",
                "type": "led"
            }
        },
        "frq_set": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "frq_set",
                "section": "inputs",
                "type": "meter"
            }
        },
        "frq_get": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "frq_get",
                "section": "inputs",
                "type": "meter"
            }
        },
        "ampere": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "ampere",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rpm": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rpm",
                "section": "inputs",
                "type": "meter"
            }
        },
        "dc_volt": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "dc_volt",
                "section": "inputs",
                "type": "meter"
            }
        },
        "ac_volt": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "ac_volt",
                "section": "inputs",
                "type": "meter"
            }
        },
        "vfd_errors": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "vfd_errors",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```
