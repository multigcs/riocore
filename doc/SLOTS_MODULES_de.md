# SLOTS

in den json board und config dateien lassen sich 'slots' eintragen,
die ermöglichen eine art Pin-Mappping um

1. plugins einfacher einem Port zuzuordnen
2. module einem slot zuzuweisen um nicht jeden pin einzeln anzugeben

kleines beispiel anhand der 'PMOD_1A' buchse am ICEBreakerV1.0e board's:

```
"slots": [
    {
        "name": "PMOD_1A",
        "comment": "PMOD 1A",
        "pins": {
            "P1": "4",
            "P2": "2",
            "P3": "47",
            "P4": "45",
            "P7": "3",
            "P8": "48",
            "P9": "46",
            "P10": "44"
        }
    }
]
```

in der config lässt sich nun der '44' wie folgt angeben ('SLOT_NAME:PIN_NAME'):
```
        {
            "type": "bitout",
            "name": "relais",
            "pins": {
                "bit": {
                    "pin": "PMOD_1A:P10"
                }
            }
        },
```

aber noch einfacher geht es wenn mehrere pins und plugins gemeinsamm genutzt werden,
wie z.B. wenn ein vorhandenes 'modul' genutzt wird....

# MODULES

mit der hilfe von 'modules' lassen sich vereinfacht wiederkehrende
konfigurationen als eine art template anlegen.

hier ein beispiel anhand des W5500-Ethernet moduls:

```
{
  "comment": "W5500-Ethernet",
  "plugins": [
        {
            "name": "w5500",
            "type": "w5500",
            "mac": "AA:AF:FA:CC:E3:1C",
            "ip": "192.168.10.195",
            "port": 2390,
            "pins": {
                "mosi": {
                    "pin": "P4"
                },
                "miso": {
                    "pin": "P3"
                },
                "sclk": {
                    "pin": "P2"
                },
                "sel": {
                    "pin": "P1"
                }
            }
        }
    ]
}
```

so hat man ein modul mit vordefinierter Pinbelegung und vereinheitlichem stecker,
in diesem fall ein PMOD stecker (2x6pin-Stiftleiste)

dieses modul lässt sich nun sehr einfach in neue configurationen,
unabhängig vom board, eintragen:

```
    "modules": [
        {
            "slot": "PMOD_2",
            "module": "w5500"
        }
    ],
```

somit sind alle pins gemappt und alle defaults gesetzt
es ist auch möglich die defaults zu überschreiben:

```
    "modules": [
        {
            "slot": "PMOD_2",
            "module": "w5500",
            "setup": {
                "w5500": {
                    "ip": "192.168.1.220",
                }
            }
        }
    ],
```

dabei bezieht sich der name 'w5500' unter dem 'setup'
auf den 'namen' des plugins in der 'module' konfiguration




