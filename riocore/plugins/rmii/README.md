# rmii

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**rmii udp interface**

rmii ethernet - udp interface - only for tangprimer20k with gowin toolchain - problems with yosys (bram)

Keywords: interface network ethernet udp

## Limitations
* boards: TangPrimer20K
* toolchains: gowin

## Pins:
*FPGA-pins*
### netrmii_clk50m:

 * direction: input

### netrmii_rx_crs:

 * direction: input

### netrmii_mdc:

 * direction: output

### netrmii_txen:

 * direction: output

### netrmii_mdio:

 * direction: inout

### netrmii_txd_0:

 * direction: output

### netrmii_txd_1:

 * direction: output

### netrmii_rxd_0:

 * direction: input

### netrmii_rxd_1:

 * direction: input

### phyrst:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### mac:
MAC-Address

 * type: str
 * default: AA:AF:FA:CC:E3:1C

### ip:
IP-Address

 * type: str
 * default: 192.168.10.194

### mask:
Network-Mask

 * type: str
 * default: 255.255.255.0

### gw:
Gateway IP-Address

 * type: str
 * default: 192.168.10.1

### port:
UDP-Port

 * type: int
 * default: 2390


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "rmii",
    "pins": {
        "netrmii_clk50m": {
            "pin": "0"
        },
        "netrmii_rx_crs": {
            "pin": "1"
        },
        "netrmii_mdc": {
            "pin": "2"
        },
        "netrmii_txen": {
            "pin": "3"
        },
        "netrmii_mdio": {
            "pin": "4"
        },
        "netrmii_txd_0": {
            "pin": "5"
        },
        "netrmii_txd_1": {
            "pin": "6"
        },
        "netrmii_rxd_0": {
            "pin": "7"
        },
        "netrmii_rxd_1": {
            "pin": "8"
        },
        "phyrst": {
            "pin": "9"
        }
    }
}
```

## Full-Example:
```
{
    "type": "rmii",
    "name": "",
    "mac": "AA:AF:FA:CC:E3:1C",
    "ip": "192.168.10.194",
    "mask": "255.255.255.0",
    "gw": "192.168.10.1",
    "port": 2390,
    "pins": {
        "netrmii_clk50m": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "netrmii_rx_crs": {
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
        "netrmii_mdc": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_txen": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_mdio": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_txd_0": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_txd_1": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_rxd_0": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_rxd_1": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phyrst": {
            "pin": "9",
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
 * [udp.v](udp.v)
 * [rmii.v](rmii.v)
