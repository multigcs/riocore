# bitout


singe bit output pin

## Basic-Example:
```
{
    "type": "bitout",
    "pins": {
        "bit": {
            "pin": "0"
        }
    }
}
```

## Pins:
### bit:

 * direction: output
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None

### net:
target net in LinuxCNC

 * type: str
 * default: None


## Signals:
### bit:

 * type: bit
 * direction: output


## Interfaces:
### bit:

 * size: 1 bit
 * direction: output


## Full-Example:
```
{
    "type": "bitout",
    "name": "",
    "net": "",
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
    "signals": {
        "bit": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "bit",
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```
