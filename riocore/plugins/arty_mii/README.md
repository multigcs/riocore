# arty_mii
udp interface for host comunication - experimental - Arty7-35t only

## Basic-Example:
```
{
    "type": "arty_mii",
    "pins": {
        "phy_rx_clk": {
            "pin": "F15"
        },
        "phy_rxd0": {
            "pin": "D18"
        },
        "phy_rxd1": {
            "pin": "E17"
        },
        "phy_rxd2": {
            "pin": "E18"
        },
        "phy_rxd3": {
            "pin": "G17"
        },
        "phy_rx_dv": {
            "pin": "G16"
        },
        "phy_rx_er": {
            "pin": "C17"
        },
        "phy_tx_clk": {
            "pin": "H16"
        },
        "phy_txd0": {
            "pin": "H14"
        },
        "phy_txd1": {
            "pin": "J14"
        },
        "phy_txd2": {
            "pin": "J13"
        },
        "phy_txd3": {
            "pin": "H17"
        },
        "phy_tx_en": {
            "pin": "H15"
        },
        "phy_col": {
            "pin": "D17"
        },
        "phy_crs": {
            "pin": "G14"
        },
        "phy_ref_clk": {
            "pin": "G18"
        },
        "phy_reset_n": {
            "pin": "C16"
        }
    }
}
```

## Pins:
### phy_rx_clk:

 * direction: input
 * pullup: False
 * default: F15

### phy_rxd0:

 * direction: input
 * pullup: False
 * default: D18

### phy_rxd1:

 * direction: input
 * pullup: False
 * default: E17

### phy_rxd2:

 * direction: input
 * pullup: False
 * default: E18

### phy_rxd3:

 * direction: input
 * pullup: False
 * default: G17

### phy_rx_dv:

 * direction: input
 * pullup: False
 * default: G16

### phy_rx_er:

 * direction: input
 * pullup: False
 * default: C17

### phy_tx_clk:

 * direction: input
 * pullup: False
 * default: H16

### phy_txd0:

 * direction: output
 * pullup: False
 * default: H14

### phy_txd1:

 * direction: output
 * pullup: False
 * default: J14

### phy_txd2:

 * direction: output
 * pullup: False
 * default: J13

### phy_txd3:

 * direction: output
 * pullup: False
 * default: H17

### phy_tx_en:

 * direction: output
 * pullup: False
 * default: H15

### phy_col:

 * direction: input
 * pullup: False
 * default: D17

### phy_crs:

 * direction: input
 * pullup: False
 * default: G14

### phy_ref_clk:

 * direction: output
 * pullup: False
 * default: G18

### phy_reset_n:

 * direction: output
 * pullup: False
 * default: C16


## Options:
### mac:
MAC-Address

 * type: str
 * default: AA:AF:FA:CC:E3:1C

### ip:
IP-Address

 * type: str
 * default: 192.168.10.194

### port:
UDP-Port

 * type: int
 * default: 2390

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:


## Interfaces:


## Full-Example:
```
{
    "type": "arty_mii",
    "mac": "AA:AF:FA:CC:E3:1C",
    "ip": "192.168.10.194",
    "port": 2390,
    "name": "",
    "pins": {
        "phy_rx_clk": {
            "pin": "F15",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "phy_rxd0": {
            "pin": "D18",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_rxd1": {
            "pin": "E17",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_rxd2": {
            "pin": "E18",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_rxd3": {
            "pin": "G17",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_rx_dv": {
            "pin": "G16",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_rx_er": {
            "pin": "C17",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_tx_clk": {
            "pin": "H16",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_txd0": {
            "pin": "H14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "phy_txd1": {
            "pin": "J14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "phy_txd2": {
            "pin": "J13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "phy_txd3": {
            "pin": "H17",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "phy_tx_en": {
            "pin": "H15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "phy_col": {
            "pin": "D17",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_crs": {
            "pin": "G14",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "phy_ref_clk": {
            "pin": "G18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "phy_reset_n": {
            "pin": "C16",
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
 * sync_signal.v
 * ssio_sdr_in.v
 * mii_phy_if.v
 * eth_mac_mii_fifo.v
 * eth_mac_mii.v
 * eth_mac_1g.v
 * axis_gmii_rx.v
 * axis_gmii_tx.v
 * lfsr.v
 * eth_axis_rx.v
 * eth_axis_tx.v
 * udp_complete.v
 * udp_checksum_gen.v
 * udp.v
 * udp_ip_rx.v
 * udp_ip_tx.v
 * ip_complete.v
 * ip.v
 * ip_eth_rx.v
 * ip_eth_tx.v
 * ip_arb_mux.v
 * arp.v
 * arp_cache.v
 * arp_eth_rx.v
 * arp_eth_tx.v
 * eth_arb_mux.v
 * arbiter.v
 * priority_encoder.v
 * axis_fifo.v
 * axis_async_fifo.v
 * axis_async_fifo_adapter.v
 * sync_reset.v
 * arty_mii.v
