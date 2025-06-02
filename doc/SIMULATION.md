# Simulation

## inside hal-component
you can activate this simulation by editing the json config file by hand:
```
    "linuxcnc": {
        "simulation": true,
    }
```
this option will disable the UDP/SPI interface function
and simulate joint movements (the position feedback)


## udp client simulation in c
for this simulation type, you need to set your device ip to 127.0..0.1 (e.g. in w5500 plugin)
and start the simulator in another terminal like this (depends on your config output folder):
```
./Output/OctoBot/Simulator/start.sh
```
for machine type 'mill' and 'corexy' there is a ugliy opengl frontend
to see the movements.

for melfa you can connect the simulator to a webots simulation (https://cyberbotics.com/)[https://cyberbotics.com/]

for all other machine type's, you have only text output of the values


## udp client simulation in python
the last simulator option is a python tool:
```
bin/rio-udpsim PATH_TO_YOUR_JSON_CONFIG
```
this is text only and not very fast, so the risk of joint follow errors is high

you need also set your device ip to 127.0..0.1 (e.g. in w5500 plugin)
