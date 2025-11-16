
create_clock -name sysclk_in -period "12.0 MHz" [get_ports sysclk_in]
derive_pll_clocks
derive_clock_uncertainty
