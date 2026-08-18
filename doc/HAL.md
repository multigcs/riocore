# Hal generator
The HAL generator has a few extra features designed to make life easier ;)

for output signals like this:

![pins_virtual](./images/hal-logic.png)

you can start a little demo to play with (-> Tab float/bool):
```
rio-generator -S riocore/configs/haldemo/virtual-signals-axis-pyvcp.json
```

![pins_virtual](./images/hal-demo.png)


here are some examples:

# bit/boolean
```
!halui.mode.is-auto
```
```
(halui.machine.is-on and motion.is-all-homed and !halui.mode.is-auto and !axisui.error) or halui.program.is-paused
```
```
toggle(riov.Bool1.value)
```
```
delay(riov.Bool1.value, 1, 1)
```
```
oneshot(riov.Bool1.value, 0.3, 0, 1)
```

# float functions:
```
limit(riov.Float1.value, -50, 50)
```
```
deadzone(riov.Float1.value, 0, 50)
```
```
abs(riov.Float1.value)
```
```
((riov.Float1.value + riov.Float2.value) - riov.Float2.value) * 5
```

# min and max value with reset pin
```
min(riov.Float1.value, riov.Reset)
```
```
max(riov.Float1.value, riov.Reset)
```

# bool to float
```
mux2(riov.Bool1.value, -50, 50)
```

# float to bool
```
riov.Float1.value < -20
```
```
riov.Float1.value > 20
```
```
riov.Float1.value <> -20,20
```
