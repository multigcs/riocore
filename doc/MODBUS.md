# Modbus

## config

### cmdmapping

mapping single bool outputs to int cmd value (for some FVD's)

cmdmapping is a comma seperated list of key/values pairs:

 `reset:7, !on:6, ffw:1, rev:2`

* the key is the suffix of the new halpin name
* the value is the new modbus value to send
* an '!' on the beginning of the key will invert the logic
* the first pair have the highest priority
* the 'error_values' are used as initial value

this example will create 4 halpins that are mapped to one modbus command (6: Force Single Register):

```
{
    "type": "modbus",
    "pins": {
        ...
    },
    "config": {
        "CMD": {
            "address": 1,
            "type": 6,
            "register": 8192,
            "values": 1,
            "datatype": "int",
            "scale": 1.0,
            "unit": "",
            "error_values": "6",
            "format": "d",
            "timeout": 300,
            "delay": 60,
            "priority": 0,
            "direction": "output",
            "cmdmapping": "!on:6, ffw:1, rev:2"
        }
    },
    "signals": {
        "CMD_on": {
            "net": "spindle.0.on"
        },
        "CMD_ffw": {
            "net": "spindle.0.forward"
        },
        "CMD_rev": {
            "net": "spindle.0.reverse"
        }
    }
}

```

for better understanding, this are the commands, the modbus FVD in this example understands
```
1：Forward operation
2：Reverse operation
6：Speed-down stop
7：Fault reset
```

the generated hal-connections:
```
net sig_spindle_0_forward                <= spindle.0.forward
net sig_spindle_0_on                     <= spindle.0.on
net sig_spindle_0_reverse                <= spindle.0.reverse

net sig_spindle_0_forward                => board0.modbus0.CMD_ffw
net sig_spindle_0_on                     => board0.modbus0.CMD_on
net sig_spindle_0_reverse                => board0.modbus0.CMD_rev
```

the generated halcomponent:
```
if (value_CMD_on == 0) { // inverted(!)
    value_CMD = 6;
} else if (value_CMD_ffw == 1) {
    value_CMD = 1;
} else if (value_CMD_rev == 1) {
    value_CMD = 2;
}
```


