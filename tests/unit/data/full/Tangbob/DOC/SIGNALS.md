# Signals
| Plugin | ID | Name | Dir | Hal-Pin | Type | Description |
| --- | --- | --- | --- | --- | --- | --- |
| wled | wled0 | wled0.0_green | <- | (!halui.mode.is-auto and !axisui.error) or halui.program.is-paused | net |  |
|  |  | wled0.0_blue | <- | halui.mode.is-auto | net |  |
|  |  | wled0.0_red | <- | axisui.error | net |  |
| bitin | bitin0 | bitin0.bit | -> | joint.0.home-sw-in | net |  |
|  | bitin1 | bitin1.bit | -> | joint.1.home-sw-in | net |  |
|  | bitin2 | bitin2.bit | -> | joint.2.home-sw-in | net |  |
