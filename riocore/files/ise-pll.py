#!/usr/bin/env python3
#
# pll tool to find best match for the target frequency
#

import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-freq-mhz", help="PLL Input Frequency", type=float, default=50)
parser.add_argument("-o", "--output-freq-mhz", help="PLL Output Frequency", type=float, default=100)
parser.add_argument("-d", "--device", help="Device", type=str, default="spartan6")
parser.add_argument(
    "-f",
    "--filename",
    help="Save PLL configuration as Verilog to file",
    type=str,
    default=None,
)
parser.add_argument(
    "-m",
    "--module-name",
    help="Specify different Verilog module name than the default 'pll'",
    type=str,
    default="pll",
)
parser.add_argument("-l", "--list-devices", help="list device", action="store_true")

args = parser.parse_args()

device_limits = {
    "spartan6": {
        "vco_min": 400,
        "vco_max": 1000,
        "clkout_min": 10,
        "clkout_max": 450,
    },
}

if args.device not in device_limits:
    print(f"ERROR: device '{args.device}' not found")
    sys.exit(1)

limits = device_limits[args.device]
setup = {}

FCLKIN = args.input_freq_mhz
min_diff = FCLKIN

if args.output_freq_mhz < limits["clkout_min"]:
    print(f"output_freq is to low: {args.output_freq_mhz} < {limits['clkout_min']}")
    exit(1)
if args.output_freq_mhz > limits["clkout_max"]:
    print(f"output_freq is to hight: {args.output_freq_mhz} > {limits['clkout_max']}")
    exit(1)

CLKIN_PERIOD = 1000 / args.input_freq_mhz

for CLKFBOUT_MULT in range(2, 64 + 1):
    for CLKOUT0_DIVIDE in range(1, 128 + 1):
        VCO = args.input_freq_mhz * CLKFBOUT_MULT
        if limits["vco_min"] > VCO:
            continue
        if limits["vco_max"] < VCO:
            continue

        CLKOUT = VCO / CLKOUT0_DIVIDE

        diff = abs(args.output_freq_mhz - CLKOUT)
        if diff < min_diff:
            print(diff)
            min_diff = diff
            setup = {
                "CLKFBOUT_MULT": CLKFBOUT_MULT,
                "CLKOUT0_DIVIDE": CLKOUT0_DIVIDE,
                "CLKOUT": CLKOUT,
                "VCO": VCO,
                "ERROR": diff,
            }

if setup:
    pll_v = f"""/**
 * PLL configuration
 *
 * This Verilog module was generated automatically
 * using the ise-pll tool.
 * Use at your own risk.
 *
 * Target-Device:                {args.device}
 * Given input frequency:        {args.input_freq_mhz:0.3f} MHz
 * Requested output frequency:   {args.output_freq_mhz:0.3f} MHz
 * Achieved output frequency:    {setup["CLKOUT"]:0.3f} MHz
 */

module {args.module_name} (
        input  clock_in, // {args.input_freq_mhz} MHz
        output clock_out, // {setup["CLKOUT"]} MHz
        reg locked = 1
    );

    wire clkref_buffered_w;
    wire clkfbout_w;
    wire pll_clkout0_w;
    wire pll_clkout0_buffered_w;

    // Input buffering
    assign clkref_buffered_w = clock_in;

    // Clocking primitive
    PLL_BASE
    #(
        .BANDWIDTH          ("OPTIMIZED"),
        .CLK_FEEDBACK       ("CLKFBOUT"),
        .COMPENSATION       ("INTERNAL"),
        .DIVCLK_DIVIDE      (1),
        .CLKFBOUT_MULT      ({setup["CLKFBOUT_MULT"]}),
        .CLKFBOUT_PHASE     (0.000),
        .CLKOUT0_DIVIDE     ({setup["CLKOUT0_DIVIDE"]}),
        .CLKOUT0_PHASE      (0.0),
        .CLKOUT0_DUTY_CYCLE (0.500),
        .CLKIN_PERIOD       ({CLKIN_PERIOD:0.3f}),
        .REF_JITTER         (0.010)
    )
    pll_base_inst
    (
        .CLKFBOUT(clkfbout_w),
        .CLKOUT0(pll_clkout0_w),
        .CLKOUT1(),
        .CLKOUT2(),
        .CLKOUT3(),
        .CLKOUT4(),
        .CLKOUT5(),
        .RST(1'b0),
        .CLKFBIN(clkfbout_w),
        .CLKIN(clkref_buffered_w)
    );

    //-----------------------------------------------------------------
    // CLK_OUT0
    //-----------------------------------------------------------------
    BUFG clkout0_buf
    (
        .I(pll_clkout0_w),
        .O(pll_clkout0_buffered_w)
    );

    assign clock_out = pll_clkout0_buffered_w;


endmodule

"""
    if args.filename:
        print(f" * Given input frequency:        {args.input_freq_mhz:0.3f} MHz")
        print(f" * Requested output frequency:   {args.output_freq_mhz:0.3f} MHz")
        print(f" * Achieved output frequency:    {setup['CLKOUT']:0.3f} MHz")
        open(args.filename, "w").write(pll_v)
    else:
        print(pll_v)
