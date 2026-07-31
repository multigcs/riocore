# mtconnect

<img align="right" width="320" src="image.png">

**mtconnect support**

mtconnect agent

* Keywords: log mqtt mtconnect digital-twin
* URL: https://github.com/sliptonic/linuxcnc/tree/feature/mtconnect-agent

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### image:
hardware type

 * type: imgselect
 * default: generic

### device_name:

 * type: str
 * default: mtconnect_demo

### uuid:

 * type: str
 * default: linuxcnc-rio-0001

### sample_hz:

 * type: int
 * min: 1
 * max: 1000
 * default: 10

### transport:

 * type: select
 * default: http
 * options: http, mqtt, both

### http_port:

 * type: int
 * min: 1024
 * max: 49151
 * default: 5000

### mqtt_broker:

 * type: str
 * default: localhost

### mqtt_port:

 * type: int
 * min: 10
 * max: 65535
 * default: 1883

### mqtt_prefix:

 * type: str
 * default: MTConnect

### model_auto:

 * type: str
 * default: 1

### model_chain:

 * type: str
 * default: X Y Z

### model_parent_z:

 * type: str
 * default: BASE

### model_invert:

 * type: str
 * default: X Y


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*

