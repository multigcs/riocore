// Sysclock
create_clock -period 37.037 -waveform {0.000 18.52} -name sysclk_in [get_ports {sysclk_in}]

// Pins
create_clock -period 100.000 -waveform {0.000 50.00} -name PINOUT_FPGA0_W5500_SCLK [get_ports {PINOUT_FPGA0_W5500_SCLK}]
create_clock -period 1000.000 -waveform {0.000 500.00} -name PINOUT_I2CBUS0_SCL [get_ports {PINOUT_I2CBUS0_SCL}]
create_clock -period 1000.000 -waveform {0.000 500.00} -name PININOUT_I2CBUS0_SDA [get_ports {PININOUT_I2CBUS0_SDA}]
