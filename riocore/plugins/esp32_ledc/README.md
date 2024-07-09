# esp32_ledc
ledc plugin to generate up to 16 PWM signals

only for esp32

## Basic-Example:
```
{
    "type": "esp32_ledc",
    "pins": {
        "pwm1": {
            "pin": "0"
        }
    }
}
```

## Pins:
### pwm1:

 * direction: output
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
### pwm1:

 * type: float
 * direction: output


## Interfaces:
### pwm1:

 * size: 8 bit
 * direction: output


## Full-Example:
```
{
    "type": "esp32_ledc",
    "name": "",
    "pins": {
        "pwm1": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "pwm1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "pwm1",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```
