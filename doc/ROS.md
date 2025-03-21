# ROS-Bridge

riocore includes a simple bridge between RIO and ROS [https://www.ros.org/](https://www.ros.org/)

## Example
you can start a ros bridge with a command like this:
```
$ bin/rio-rosbridge -p /tangbob riocore/configs/Tangbob/config.json 192.168.10.194:2390
```

and check the bridge with rostopic:
```
$ rostopic list
/rosout
/rosout_agg
/tangbob/e_stop/bit
/tangbob/enable/bit
/tangbob/home_x/bit
/tangbob/home_y/bit
/tangbob/home_z/bit
/tangbob/i2cbus0/lm75_0_temp
/tangbob/i2cbus0/lm75_0_valid
/tangbob/joint_0/enable
/tangbob/joint_0/position
/tangbob/joint_0/velocity
/tangbob/joint_1/enable
/tangbob/joint_1/position
/tangbob/joint_1/velocity
/tangbob/joint_2/enable
/tangbob/joint_2/position
/tangbob/joint_2/velocity
/tangbob/joint_3/enable
/tangbob/joint_3/position
/tangbob/joint_3/velocity
/tangbob/modbus0/current
/tangbob/modbus0/current_errors
/tangbob/modbus0/current_valid
/tangbob/modbus0/freq
/tangbob/modbus0/freq_errors
/tangbob/modbus0/freq_valid
/tangbob/modbus0/power
/tangbob/modbus0/power_errors
/tangbob/modbus0/power_factor
/tangbob/modbus0/power_factor_errors
/tangbob/modbus0/power_factor_valid
/tangbob/modbus0/power_total
/tangbob/modbus0/power_total_errors
/tangbob/modbus0/power_total_valid
/tangbob/modbus0/power_valid
/tangbob/modbus0/voltage
/tangbob/modbus0/voltage_errors
/tangbob/modbus0/voltage_valid
/tangbob/probe/bit
/tangbob/pwm/dty
/tangbob/pwm/enable
/tangbob/spindle_enable/bit
/tangbob/wled0/0_blue
/tangbob/wled0/0_green
/tangbob/wled0/0_red
```

or test the output with something like that:
```
rostopic pub -1 /tangbob/wled0/0_green std_msgs/Bool "data: 1"
rostopic pub -1 /tangbob/wled0/0_green std_msgs/Bool "data: 0"
```

```
rostopic echo /tangbob/joint_0/position
```


