# Simulation

## inside hal-component
```
bin/rio-generator -S config.json
```
this option will disable the UDP/SPI interface function
and simulate the position feedback of joint movements,
all inside the linuxcnc component


## udp client simulation in c
for this simulation type, you need to set your device ip to 127.0..0.1 (e.g. in w5500 plugin)
and start the simulator in another terminal like this (depends on your config output folder):
```
bin/rio-generator -U config.json
```
for machine type 'mill' there is a ugliy opengl frontend
to see the movements.

for melfa you can connect the simulator to a webots simulation (https://cyberbotics.com/)[https://cyberbotics.com/]

for all other machine type's, you have only text output of the values

