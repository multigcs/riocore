# MQTT-Bridge

riocore includes a simple bridge between RIO and MQTT (Message Queueing Telemetry Transport)

It cannot be used in conjunction with LinuxCNC !

This connection is intended for other measurement and automation purposes


## depends
```
sudo apt-get install mosquitto mosquitto-clients libpaho-mqtt-dev
```

## Example
you can start a mqtt bridge with a command like this:
```
sh Output/Tangbob/MQTT/fpga0/start.sh
```

and check the bridge with rostopic:
```
$ mosquitto_sub -h localhost -t "#" -v
/rio/joint_0/position 0.000000
/rio/joint_1/position 0.000000
/rio/joint_2/position 0.000000
/rio/joint_3/position 0.000000
/rio/modbus0/temperature 0.000000
/rio/i2cbus0/lm75_0_temp 0.000000
/rio/i2cbus0/lm75_0_valid 0
/rio/home_x/bit 0
/rio/home_y/bit 0
/rio/home_z/bit 0
/rio/e_stop/bit 0
/rio/probe/bit 0
```

or test the output with something like that:
```
mosquitto_pub -h  localhost -t /rio/wled0/0_green -m 1
mosquitto_pub -h  localhost -t /rio/wled0/0_green -m 0
```

## Templates
there is also a generated node-red template with all mqtt I/O's
```
Output/Tangbob/MQTT/fpga0/node-red.json
```
and a test html page to view/set all mqtt messages
```
Output/Tangbob/MQTT/fpga0/test.html
```

