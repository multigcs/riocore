# Signals
| Plugin | ID | Name | Dir | Hal-Pin | Type | Description |
| --- | --- | --- | --- | --- | --- | --- |
| gpioout | gpioout0 | hal_gpio.GPIO26-out | <- | halui.machine.is-on | net |  |
| gpioin | gpioin0 | hal_gpio.GPIO25-in | -> | joint.0.home-sw-in | net |  |
|  | gpioin1 | hal_gpio.SPI_CE0_N-in | -> | joint.1.home-sw-in | net |  |
|  | gpioin2 | hal_gpio.SPI_CE1_N-in | -> | joint.2.home-sw-in | net |  |
|  | gpioin4 | hal_gpio.GPIO13-in | -> | motion.probe-input | net |  |
| pwmgen | pwmgen0 | pwmgen.0.value | <- | spindle.0.speed-out | net |  |
|  |  | pwmgen.0.enable | <- | spindle.0.on | net |  |
