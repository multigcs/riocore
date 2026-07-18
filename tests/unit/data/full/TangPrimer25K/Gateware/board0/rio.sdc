// Sysclock
create_clock -period 20.000 -waveform {0.000 10.00} -name sysclk_in [get_ports {sysclk_in}]
create_clock -period 10.000 -waveform {0.000 5.00} -name sysclk [get_nets {sysclk}]
