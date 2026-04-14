// Sysclock
create_clock -period 20.000 -waveform {0.000 10.00} -name sysclk_in [get_ports {sysclk_in}]
create_clock -period 10.000 -waveform {0.000 5.00} -name sysclk [get_nets {sysclk}]

// Pins
create_clock -period 100.000 -waveform {0.000 50.00} -name PINOUT_W55000_SCLK [get_ports {PINOUT_W55000_SCLK}]
