# Changelog

## v0.9.4

### Gui and Generator
* adding new experimental grafical setup tool: rio-flow
* support for more hal components (conv-*-*, limit, wcomp, delay)

### Plugins
* adding experimental riosub plugin, to chain multiple FPGA's
* adding absulute encoder plugins (experimental) for panasonic, t3d, stepperonline
* adding new spi interface with programming support (spi passthrough)
* modbus: some little fixes

### Modifiers
* adding delay with separately configurable rising/faling edges

### Boards
* adding Mesa 7c81 support

### Toolchains
* vivado: initial support for Xilinx Zynq 7010
* ise: pll support for Spartan6

### Generator
* adding experimental easycat support (EtherCat-Bridge)
* adding experimental support for breakout-boards (for rio-flow / only one at the moment)


## v0.9.3

### Gui and Generator
* adding experimental parport / rpi gpio support
* adding experimental gpio component support (pwmgen/stepgen/encoder)
* display diffs in Json Tab
* adding [Simulator](doc/SIMULATION.md) via UDP with simple 3D-View
* adding [ros](doc/ROS.md) support (ros-bridge - Robot Operating System)
* adding [mqtt](doc/MQTT.md) support (mqtt-bridge - Message Queueing Telemetry Transport)
* adding [jslib](doc/JSLIB.md) generator (Javascript library)

### Plugins
* adding as5600 over pwm plugin
* adding caliper plugin
* adding hallsensor plugin
* adding yaskawa absulute encoder plugin (experimental)
* adding riodrive can-bus plugin (experimental)
* adding rioencoder plugin (experimental)
* adding bldc foc plugin (experimental)


## v0.9.2

### Gui and Generator
* better overview graph
* adding icons to some table's/tree's

### Plugins
* better freqin (valid flag)

### Pin-Modifier
* fixing debouncer

### Toolchans
* initial/experimental Efinix / Efinity support


## v0.9.1

### Gui and Generator
* support for gladevcp, pyvcp, qtpyvcp, qtvcp
* some little fixes and improvements
* adding support for virtual pins
* now you can use the same input pin in multiple plugins
* now runs partially on Windows/MacOS (not realy supported)

### Plugins
* new plugin: [i2cbus](riocore/plugins/i2cbus/README.md) (i2c bus support with some device drivers)
* new plugin: [pdmout](riocore/plugins/pdmout/README.md) (delta-sigma modulator / dac)
* new plugin: [sinepwm](riocore/plugins/sinepwm/README.md) (generates sine waves)
* new plugin: [hbridge](riocore/plugins/hbridge/README.md) (to control DC-Motors)
* better [stepdir](riocore/plugins/stepdir/README.md) plugin (with pulse_len and dir_delay configuration)
* some more new small plugins for extended configurations
* the old i2c based sensors are removed (now in i2cbus)
* fixes for the quadencoder(z) rps/rpm calculation

### Pin-Modifier
* better debouncer (now, the delay is in milliseconds, which makes the whole thing easier to configure.)
* new modifier: oneshot (creates a variable-length output pulse when the input changes state)
* overwiew : [doc/MODIFIERS.md](doc/MODIFIERS.md)

### Addons
* adding Spacemouse support
