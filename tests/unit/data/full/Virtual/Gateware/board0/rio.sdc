// Sysclock
create_clock -period 37.037 -waveform {0.000 18.52} -name sysclk_in [get_ports {sysclk_in}]

// Pins
create_clock -period 100.000 -waveform {0.000 50.00} -name PINOUT_BOARD0_W5500_SCLK [get_ports {PINOUT_BOARD0_W5500_SCLK}]
