# Signals
| Plugin | ID | Name | Dir | Hal-Pin | Type | Description |
| --- | --- | --- | --- | --- | --- | --- |
| bitin | bitin0 | fpga0.bitin0.bit | -> | joint.0.home-sw-in | net |  |
|  | bitin1 | fpga0.bitin1.bit | -> | joint.1.home-sw-in | net |  |
|  | bitin2 | fpga0.bitin2.bit | -> | joint.2.home-sw-in | net |  |
| wled | wled | fpga0.wled.0_green | <- | (!halui.mode.is-auto and !axisui.error) or halui.program.is-paused | net |  |
|  |  | fpga0.wled.0_blue | <- | halui.mode.is-auto | net |  |
|  |  | fpga0.wled.0_red | <- | axisui.error | net |  |
| bitout | bitout0 | fpga0.bitout0.bit | <- | spindle.0.on | net |  |
