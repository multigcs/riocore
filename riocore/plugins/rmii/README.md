# rmii
**rmii udp interface (experimental)**

rmii ethernet - udp interface - only for tangprimer20k with gowin toolchain - problems with yosys (bram)

## Basic-Example:
```
{
    "type": "rmii",
    "pins": {
        "phyrst": {
            "pin": "0"
        },
        "netrmii_clk50m": {
            "pin": "1"
        },
        "netrmii_rx_crs": {
            "pin": "2"
        },
        "netrmii_mdc": {
            "pin": "3"
        },
        "netrmii_txen": {
            "pin": "4"
        },
        "netrmii_mdio": {
            "pin": "5"
        },
        "netrmii_txd_0": {
            "pin": "6"
        },
        "netrmii_txd_1": {
            "pin": "7"
        },
        "netrmii_rxd_0": {
            "pin": "8"
        },
        "netrmii_rxd_1": {
            "pin": "9"
        }
    }
}
```

## Pins:
*FPGA-pins*
### phyrst:

 * direction: output

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


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Full-Example:
```
{
    "type": "rmii",
    "name": "",
    "pins": {
        "phyrst": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_clk50m": {
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
        "netrmii_rx_crs": {
            "pin": "2",
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
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_txen": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_mdio": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_txd_0": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_txd_1": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "netrmii_rxd_0": {
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
        "netrmii_rxd_1": {
            "pin": "9",
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
    "signals": {}
}
```

## Verilogs:
 * [udp.v](udp.v)
 * [rmii.v](rmii.v)
