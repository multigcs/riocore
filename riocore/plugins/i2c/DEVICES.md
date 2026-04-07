# some tested modbus devices


## NT18B07

7x Temperatur In (NTC)

```
"temp7": {
    "address": 18,
    "type": 3,
    "register": 0,
    "values": 2,
    "scale": 0.1,
    "unit": "\u00b0C",
    "error_values": "",
    "format": "0.1f",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
}
```

https://www.amazon.de/gp/product/B0BYNN6ZSQ


## N4DAC02

2CH Analog-Out

the part is total rubbish !!!

https://www.amazon.de/gp/product/B09H79BTFT


## DDS519MR

Energie-Meter

needs to change serial setup (Parity: even -> none)

```
    # read voltage
    # data = [address, 4, 0, 0, 0, 2]

    # set parity to none
    # float_data = list(struct.pack('>f', 2.0))
    # data = [address, 0x10, 0, 0x02, 0, 0x02, 0x04] + float_data

    # set address to 16
    # float_data = list(struct.pack('>f', 16.0))
    # data = [address, 0x10, 0, 0x08, 0, 0x02, 0x04] + float_data
```

```
"voltage": {
    "address": 16,
    "type": 4,
    "register": 0,
    "is_float": true,
    "values": 1,
    "scale": 1.0,
    "unit": "V",
    "error_values": "",
    "format": "0.1f",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
},
"current": {
    "address": 16,
    "type": 4,
    "register": 8,
    "is_float": true,
    "values": 1,
    "scale": 1.0,
    "unit": "A",
    "error_values": "",
    "format": "0.2f",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
},
"power": {
    "address": 16,
    "type": 4,
    "register": 18,
    "is_float": true,
    "values": 1,
    "scale": 1.0,
    "unit": "W",
    "error_values": "",
    "format": "0.1f",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
},
"power_factor": {
    "address": 16,
    "type": 4,
    "register": 42,
    "is_float": true,
    "values": 1,
    "scale": 1.0,
    "unit": "Cos",
    "error_values": "",
    "format": "0.2f",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
},
"freq": {
    "address": 16,
    "type": 4,
    "register": 54,
    "is_float": true,
    "values": 1,
    "scale": 1.0,
    "unit": "Hz",
    "error_values": "",
    "format": "0.1f",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
},
"power_total": {
    "address": 16,
    "type": 4,
    "register": 256,
    "is_float": true,
    "values": 1,
    "scale": 1.0,
    "unit": "kWh",
    "error_values": "",
    "format": "0.1f",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
}
```

https://www.amazon.de/gp/product/B08P596DMV


## EBYTE MA01-AXCX4020

4x Digital In
2x Digital Out (Relais)


```
"do2": {
    "address": 11,
    "type": 15,
    "register": 0,
    "values": 2,
    "scale": 1.0,
    "unit": "",
    "error_values": "0 0",
    "format": "d",
    "timeout": 100,
    "delay": 60,
    "direction": "output"
},
"di4": {
    "address": 11,
    "type": 2,
    "register": 0,
    "values": 4,
    "scale": 1.0,
    "unit": "",
    "error_values": "",
    "format": "d",
    "timeout": 100,
    "delay": 60,
    "direction": "input"
},
```


https://www.amazon.de/gp/product/B097PGBWV9


## EBYTE MA01-XACX0440

4x Analog-In (0-20mA)
4x Digital-Out (Relais)

```
"do4": {
    "address": 32,
    "type": 15,
    "register": 0,
    "values": 4,
    "scale": 1.0,
    "unit": "",
    "error_values": "",
    "format": "d",
    "timeout": 100,
    "delay": 60,
    "direction": "output"
}
"ain": {
    "address": 32,
    "type": 4,
    "register": 0,
    "values": 4,
    "delay": 100,
    "scale": 0.0061,
    "unit": "mA",
    "format": "04.1f",
    "direction": "input"
},
```

https://www.amazon.de/gp/product/B09P4S3TX1


