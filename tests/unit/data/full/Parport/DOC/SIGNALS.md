# Signals
| Plugin | ID | Name | Dir | Hal-Pin | Type | Description |
| --- | --- | --- | --- | --- | --- | --- |
| pwmgen | pwmgen0 | pwmgen.0.value | <- | spindle.0.speed-out | net |  |
|  |  | pwmgen.0.enable | <- | spindle.0.on | net |  |
| gpioout | gpioout0 | parport.0.pin-14-out | <- | halui.machine.is-on | net |  |
|  | gpioout1 | parport.0.pin-17-out | <- | spindle.0.on | net |  |
| gpioin | gpioin0 | parport.0.pin-10-in-not | -> | joint.0.home-sw-in | net |  |
|  | gpioin1 | parport.0.pin-11-in-not | -> | joint.1.home-sw-in | net |  |
|  | gpioin2 | parport.0.pin-12-in-not | -> | joint.2.home-sw-in | net |  |
|  | gpioin4 | parport.0.pin-13-in-not | -> | motion.probe-input | net |  |
