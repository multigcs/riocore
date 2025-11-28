
# https://github.com/xjtuecho/EBAZ4205/blob/master/README.md
# https://github.com/XyleMora/EBAZ4205/blob/main/Documents/Schematics/ebaz4205_schematic.pdf
# https://www.codeembedded.com/blog/fpga_zero_to_hero_vol_5/
# https://docs.amd.com/r/en-US/ug1165-zynq-embedded-design-tutorial/Booting-Linux-in-JTAG-Mode

# Create interface ports
set DDR [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:ddrx_rtl:1.0 DDR ]
set FIXED_IO [ create_bd_intf_port -mode Master -vlnv xilinx.com:display_processing_system7:fixedio_rtl:1.0 FIXED_IO ]
set MDIO_ETHERNET_0_0 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:mdio_rtl:1.0 MDIO_ETHERNET_0_0 ]
#set GPIO_0_0 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:gpio_rtl:1.0 GPIO_0_0 ]
#set UART_0_0 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:uart_rtl:1.0 UART_0_0 ]

# Create ports
set ENET0_GMII_RXD_0 [ create_bd_port -dir I -from 3 -to 0 ENET0_GMII_RXD_0 ]
set ENET0_GMII_RX_CLK_0 [ create_bd_port -dir I -type clk ENET0_GMII_RX_CLK_0 ]
set ENET0_GMII_RX_DV_0 [ create_bd_port -dir I ENET0_GMII_RX_DV_0 ]
set ENET0_GMII_TXD_0 [ create_bd_port -dir O -from 3 -to 0 ENET0_GMII_TXD_0 ]
set ENET0_GMII_TX_CLK_0 [ create_bd_port -dir I -type clk ENET0_GMII_TX_CLK_0 ]
set ENET0_GMII_TX_EN_0 [ create_bd_port -dir O -from 0 -to 0 ENET0_GMII_TX_EN_0 ]

# Create instance: processing_system7_0, and set properties
set processing_system7_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0 ]
set_property -dict [ list \
CONFIG.PCW_UART1_PERIPHERAL_ENABLE {1} \
CONFIG.PCW_UART1_UART1_IO {MIO 24 .. 25} \
CONFIG.PCW_SD0_PERIPHERAL_ENABLE {1} \
CONFIG.PCW_SD0_SD0_IO {MIO 40 .. 45} \
CONFIG.PCW_NAND_PERIPHERAL_ENABLE {1} \
CONFIG.PCW_NAND_GRP_D8_ENABLE {0} \
CONFIG.PCW_NAND_CYCLES_T_AR {15} \
CONFIG.PCW_NAND_CYCLES_T_CLR {15} \
CONFIG.PCW_NAND_CYCLES_T_RC {30} \
CONFIG.PCW_NAND_CYCLES_T_REA {5} \
CONFIG.PCW_NAND_CYCLES_T_RR {25} \
CONFIG.PCW_NAND_CYCLES_T_WC {30} \
CONFIG.PCW_NAND_CYCLES_T_WP {15} \
CONFIG.PCW_NAND_NAND_IO {MIO 0 2.. 14} \
CONFIG.PCW_ENET0_PERIPHERAL_ENABLE {1} \
CONFIG.PCW_ENET0_ENET0_IO {EMIO} \
CONFIG.PCW_ENET0_GRP_MDIO_ENABLE {1} \
CONFIG.PCW_ENET0_PERIPHERAL_FREQMHZ {100 Mbps} \
CONFIG.PCW_GPIO_MIO_GPIO_ENABLE {1} \
CONFIG.PCW_GPIO_MIO_GPIO_IO {MIO} \
CONFIG.PCW_ENET_RESET_ENABLE {0} \
CONFIG.PCW_USB_RESET_ENABLE {0} \
CONFIG.PCW_I2C_RESET_ENABLE {0} \
CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH {16 Bit} \
CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41K128M16 JT-125} \
] $processing_system7_0

# Create instance: xlconcat_1, and set properties
set xlconcat_1 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 xlconcat_1 ]
set_property -dict [ list \
CONFIG.IN0_WIDTH {4} \
CONFIG.IN1_WIDTH {4} \
] $xlconcat_1

# Create instance: xlconstant_0, and set properties
set xlconstant_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 xlconstant_0 ]
set_property -dict [ list \
CONFIG.CONST_VAL {0} \
CONFIG.CONST_WIDTH {4} \
] $xlconstant_0

# Create instance: xlslice_0, and set properties
set xlslice_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 xlslice_0 ]
set_property -dict [ list \
CONFIG.DIN_FROM {3} \
CONFIG.DIN_TO {0} \
CONFIG.DIN_WIDTH {8} \
CONFIG.DOUT_WIDTH {4} \
] $xlslice_0

# Create interface connections
connect_bd_intf_net -intf_net processing_system7_0_DDR [get_bd_intf_ports DDR] [get_bd_intf_pins processing_system7_0/DDR]
connect_bd_intf_net -intf_net processing_system7_0_FIXED_IO [get_bd_intf_ports FIXED_IO] [get_bd_intf_pins processing_system7_0/FIXED_IO]
connect_bd_intf_net -intf_net processing_system7_0_MDIO_ETHERNET_0 [get_bd_intf_ports MDIO_ETHERNET_0_0] [get_bd_intf_pins processing_system7_0/MDIO_ETHERNET_0]
#connect_bd_intf_net -intf_net processing_system7_0_GPIO_0 [get_bd_intf_ports GPIO_0_0] [get_bd_intf_pins processing_system7_0/GPIO_0]
#connect_bd_intf_net -intf_net processing_system7_0_UART_0 [get_bd_intf_ports UART_0_0] [get_bd_intf_pins processing_system7_0/UART_0]

# Create port connections
connect_bd_net -net ENET0_GMII_RX_CLK_0_1 [get_bd_ports ENET0_GMII_RX_CLK_0] [get_bd_pins processing_system7_0/ENET0_GMII_RX_CLK]
connect_bd_net -net ENET0_GMII_RX_DV_0_1 [get_bd_ports ENET0_GMII_RX_DV_0] [get_bd_pins processing_system7_0/ENET0_GMII_RX_DV]
connect_bd_net -net ENET0_GMII_TX_CLK_0_1 [get_bd_ports ENET0_GMII_TX_CLK_0] [get_bd_pins processing_system7_0/ENET0_GMII_TX_CLK]
connect_bd_net -net In0_0_1 [get_bd_ports ENET0_GMII_RXD_0] [get_bd_pins xlconcat_1/In0]
connect_bd_net -net processing_system7_0_ENET0_GMII_TXD [get_bd_pins processing_system7_0/ENET0_GMII_TXD] [get_bd_pins xlslice_0/Din]
connect_bd_net -net processing_system7_0_ENET0_GMII_TX_EN [get_bd_ports ENET0_GMII_TX_EN_0] [get_bd_pins processing_system7_0/ENET0_GMII_TX_EN]
# connect_bd_net -net processing_system7_0_FCLK_CLK0 [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins processing_system7_0/M_AXI_GP0_ACLK]
# connect_bd_net -net processing_system7_0_FCLK_CLK0 [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins processing_system7_0/S_AXI_GP0_ACLK]

connect_bd_net -net xlconcat_1_dout [get_bd_pins processing_system7_0/ENET0_GMII_RXD] [get_bd_pins xlconcat_1/dout]
connect_bd_net -net xlconstant_0_dout [get_bd_pins xlconcat_1/In1] [get_bd_pins xlconstant_0/dout]
connect_bd_net -net xlslice_0_Dout [get_bd_ports ENET0_GMII_TXD_0] [get_bd_pins xlslice_0/Dout]

