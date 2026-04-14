#!/usr/bin/env python3
#
# pll tool to find best match for the target frequency
# calculations based on: https://github.com/juj/gowin_fpga_code_generators/blob/main/pll_calculator.html
# limits from: http://cdn.gowinsemi.com.cn/DS117E.pdf, http://cdn.gowinsemi.com.cn/DS861E.pdf
#

import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-freq-mhz", help="PLL Input Frequency", type=float, default=27)
parser.add_argument("-o", "--output-freq-mhz", help="PLL Output Frequency", type=float, default=108)
parser.add_argument("-d", "--device", help="Device", type=str, default="GW1NR-9 C6/I5")
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
    "GW1NR-1 C6/I5": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 900,
        "clkout_min": 3.125,
        "clkout_max": 450,
    },
    "GW1NR-1 C5/I4": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 320,
        "vco_min": 320,
        "vco_max": 720,
        "clkout_min": 2.5,
        "clkout_max": 360,
    },
    "GW1NR-2 C7/I6": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 800,
        "clkout_min": 3.125,
        "clkout_max": 750,
    },
    "GW1NR-2 C6/I5": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 800,
        "clkout_min": 3.125,
        "clkout_max": 750,
    },
    "GW1NR-2 C5/I4": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 320,
        "vco_min": 320,
        "vco_max": 640,
        "clkout_min": 2.5,
        "clkout_max": 640,
    },
    "GW1NR-4 C6/I5": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 1000,
        "clkout_min": 3.125,
        "clkout_max": 500,
    },
    "GW1NR-4 C5/I4": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 320,
        "vco_min": 320,
        "vco_max": 800,
        "clkout_min": 2.5,
        "clkout_max": 400,
    },
    "GW1NSR-4(C) C7/I6": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 1200,
        "clkout_min": 3.125,
        "clkout_max": 600,
    },
    "GW1NSR-4(C) C6/I5": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 1200,
        "clkout_min": 3.125,
        "clkout_max": 600,
    },
    "GW1NSR-4(C) C5/I4": {
        "comment": "Untested",
        "pll_name": "PLLVR",
        "pfd_min": 3,
        "pfd_max": 320,
        "vco_min": 320,
        "vco_max": 960,
        "clkout_min": 2.5,
        "clkout_max": 480,
    },
    "GW1NR-9 C7/I6": {
        "comment": "Untested",
        "pll_name": "rPLL",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 1200,
        "clkout_min": 3.125,
        "clkout_max": 600,
    },
    "GW1NR-9 C6/I5": {
        "comment": "tested on TangNano9K Board",
        "pll_name": "rPLL",
        "pfd_min": 3,
        "pfd_max": 400,
        "vco_min": 400,
        "vco_max": 1200,
        "clkout_min": 3.125,
        "clkout_max": 600,
    },
    "GW1NR-9 C6/I4": {
        "comment": "Untested",
        "pll_name": "rPLL",
        "pfd_min": 3,
        "pfd_max": 320,
        "vco_min": 3200,
        "vco_max": 960,
        "clkout_min": 2.5,
        "clkout_max": 480,
    },
    "GW5A-25A C1/I0": {
        "comment": "not working yet",
        "pll_name": "PLLA",
        "pfd_min": 19,
        "pfd_max": 81.25,
        "vco_min": 650,
        "vco_max": 1300,
        "clkout_min": 19,
        "clkout_max": 800,
    },
}

if args.list_devices:
    for device in device_limits:
        print(f"{device} - {device_limits[device]['comment']}")
    sys.exit(0)

if args.device not in device_limits:
    print(f"ERROR: device '{args.device}' not found")
    sys.exit(1)

limits = device_limits[args.device]
setup = {}

FCLKIN = args.input_freq_mhz
min_diff = FCLKIN

IDIV_SEL_MIN = 0
if limits["pll_name"] == "PLLA":
    IDIV_SEL = 1
    FBDIV_SEL = 1
    MDIV = 1
    for MDIV in range(1, 128):
        for ODIV_SEL in range(1, 128):
            # PFD = FCLKIN / (IDIV_SEL + 1)
            # if not (limits["pfd_min"] < PFD < limits["pfd_max"]):
            #    continue

            VCO = (FCLKIN / IDIV_SEL) * FBDIV_SEL * MDIV
            if not (limits["vco_min"] < VCO < limits["vco_max"]):
                continue

            CLKOUT = VCO / ODIV_SEL
            if not (limits["clkout_min"] < CLKOUT < limits["clkout_max"]):
                continue

            diff = abs(args.output_freq_mhz - CLKOUT)
            if diff < min_diff:
                min_diff = diff
                setup = {
                    "IDIV_SEL": IDIV_SEL,
                    "FBDIV_SEL": FBDIV_SEL,
                    "ODIV_SEL": ODIV_SEL,
                    "MDIV": MDIV,
                    "CLKOUT": CLKOUT,
                    "VCO": VCO,
                    "ERROR": diff,
                }
else:
    for IDIV_SEL in range(64):
        for FBDIV_SEL in range(64):
            for ODIV_SEL in [2, 4, 8, 16, 32, 48, 64, 80, 96, 112, 128]:
                PFD = FCLKIN / (IDIV_SEL + 1)
                if not (limits["pfd_min"] < PFD < limits["pfd_max"]):
                    continue
                CLKOUT = FCLKIN * (FBDIV_SEL + 1) / (IDIV_SEL + 1)
                if not (limits["clkout_min"] < CLKOUT < limits["clkout_max"]):
                    continue
                VCO = (FCLKIN * (FBDIV_SEL + 1) * ODIV_SEL) / (IDIV_SEL + 1)
                if not (limits["vco_min"] < VCO < limits["vco_max"]):
                    continue
                diff = abs(args.output_freq_mhz - CLKOUT)
                if diff < min_diff:
                    min_diff = diff
                    setup = {
                        "IDIV_SEL": IDIV_SEL,
                        "FBDIV_SEL": FBDIV_SEL,
                        "ODIV_SEL": ODIV_SEL,
                        "PFD": PFD,
                        "CLKOUT": CLKOUT,
                        "VCO": VCO,
                        "ERROR": diff,
                    }

if setup:
    if limits["pll_name"] == "PLLA":
        pll_v = f"""/**
 * PLL configuration
 *
 * This Verilog module was generated automatically
 * using the gowin-pll tool.
 * Use at your own risk.
 *
 * Target-Device:                {args.device}
 * Given input frequency:        {args.input_freq_mhz:0.3f} MHz
 * Requested output frequency:   {args.output_freq_mhz:0.3f} MHz
 * Achieved output frequency:    {setup["CLKOUT"]:0.3f} MHz
 */

module {args.module_name}(
        input  clock_in,
        output clock_out,
        output locked
    );
    wire clkout1_o;
    wire clkout2_o;
    wire clkout3_o;
    wire clkout4_o;
    wire clkout5_o;
    wire clkout6_o;
    wire clkfbout_o;
    wire [7:0] mdrdo_o;
    wire gw_gnd;
    assign gw_gnd = 1'b0;

    PLLA PLLA_inst (
        .LOCK(locked),
        .CLKOUT0(clock_out),
        .CLKOUT1(clkout1_o),
        .CLKOUT2(clkout2_o),
        .CLKOUT3(clkout3_o),
        .CLKOUT4(clkout4_o),
        .CLKOUT5(clkout5_o),
        .CLKOUT6(clkout6_o),
        .CLKFBOUT(clkfbout_o),
        .MDRDO(mdrdo_o),
        .CLKIN(clock_in),
        .CLKFB(gw_gnd),
        .RESET(gw_gnd),
        .PLLPWD(gw_gnd),
        .RESET_I(gw_gnd),
        .RESET_O(gw_gnd),
        .PSSEL({{gw_gnd,gw_gnd,gw_gnd}}),
        .PSDIR(gw_gnd),
        .PSPULSE(gw_gnd),
        .SSCPOL(gw_gnd),
        .SSCON(gw_gnd),
        .SSCMDSEL({{gw_gnd,gw_gnd,gw_gnd,gw_gnd,gw_gnd,gw_gnd,gw_gnd}}),
        .SSCMDSEL_FRAC({{gw_gnd,gw_gnd,gw_gnd}}),
        .MDCLK(gw_gnd),
        .MDOPC({{gw_gnd,gw_gnd}}),
        .MDAINC(gw_gnd),
        .MDWDI({{gw_gnd,gw_gnd,gw_gnd,gw_gnd,gw_gnd,gw_gnd,gw_gnd,gw_gnd}})
    );
    defparam PLLA_inst.FCLKIN = "{FCLKIN}";
    defparam PLLA_inst.IDIV_SEL = {setup["IDIV_SEL"]};
    defparam PLLA_inst.FBDIV_SEL = {setup["FBDIV_SEL"]};
    defparam PLLA_inst.CLKFB_SEL = "INTERNAL";
    defparam PLLA_inst.MDIV_SEL = {setup["MDIV"]};
    defparam PLLA_inst.MDIV_FRAC_SEL = 0;
    defparam PLLA_inst.ODIV0_SEL = {setup["ODIV_SEL"]};
    defparam PLLA_inst.ODIV0_FRAC_SEL = 0;
    defparam PLLA_inst.ODIV1_SEL = 8;
    defparam PLLA_inst.ODIV2_SEL = 8;
    defparam PLLA_inst.ODIV3_SEL = 8;
    defparam PLLA_inst.ODIV4_SEL = 8;
    defparam PLLA_inst.ODIV5_SEL = 8;
    defparam PLLA_inst.ODIV6_SEL = 8;
    defparam PLLA_inst.CLKOUT0_EN = "TRUE";
    defparam PLLA_inst.CLKOUT1_EN = "FALSE";
    defparam PLLA_inst.CLKOUT2_EN = "FALSE";
    defparam PLLA_inst.CLKOUT3_EN = "FALSE";
    defparam PLLA_inst.CLKOUT4_EN = "FALSE";
    defparam PLLA_inst.CLKOUT5_EN = "FALSE";
    defparam PLLA_inst.CLKOUT6_EN = "FALSE";
    defparam PLLA_inst.CLKOUT0_DT_DIR = 1'b1;
    defparam PLLA_inst.CLKOUT1_DT_DIR = 1'b1;
    defparam PLLA_inst.CLKOUT2_DT_DIR = 1'b1;
    defparam PLLA_inst.CLKOUT3_DT_DIR = 1'b1;
    defparam PLLA_inst.CLK0_IN_SEL = 1'b0;
    defparam PLLA_inst.CLK0_OUT_SEL = 1'b0;
    defparam PLLA_inst.CLK1_IN_SEL = 1'b0;
    defparam PLLA_inst.CLK1_OUT_SEL = 1'b0;
    defparam PLLA_inst.CLK2_IN_SEL = 1'b0;
    defparam PLLA_inst.CLK2_OUT_SEL = 1'b0;
    defparam PLLA_inst.CLK3_IN_SEL = 1'b0;
    defparam PLLA_inst.CLK3_OUT_SEL = 1'b0;
    defparam PLLA_inst.CLK4_IN_SEL = 2'b00;
    defparam PLLA_inst.CLK4_OUT_SEL = 1'b0;
    defparam PLLA_inst.CLK5_IN_SEL = 1'b0;
    defparam PLLA_inst.CLK5_OUT_SEL = 1'b0;
    defparam PLLA_inst.CLK6_IN_SEL = 1'b0;
    defparam PLLA_inst.CLK6_OUT_SEL = 1'b0;
    defparam PLLA_inst.CLKOUT0_PE_COARSE = 0;
    defparam PLLA_inst.CLKOUT0_PE_FINE = 0;
    defparam PLLA_inst.CLKOUT1_PE_COARSE = 0;
    defparam PLLA_inst.CLKOUT1_PE_FINE = 0;
    defparam PLLA_inst.CLKOUT2_PE_COARSE = 0;
    defparam PLLA_inst.CLKOUT2_PE_FINE = 0;
    defparam PLLA_inst.CLKOUT3_PE_COARSE = 0;
    defparam PLLA_inst.CLKOUT3_PE_FINE = 0;
    defparam PLLA_inst.CLKOUT4_PE_COARSE = 0;
    defparam PLLA_inst.CLKOUT4_PE_FINE = 0;
    defparam PLLA_inst.CLKOUT5_PE_COARSE = 0;
    defparam PLLA_inst.CLKOUT5_PE_FINE = 0;
    defparam PLLA_inst.CLKOUT6_PE_COARSE = 0;
    defparam PLLA_inst.CLKOUT6_PE_FINE = 0;
    defparam PLLA_inst.DE0_EN = "FALSE";
    defparam PLLA_inst.DE1_EN = "FALSE";
    defparam PLLA_inst.DE2_EN = "FALSE";
    defparam PLLA_inst.DE3_EN = "FALSE";
    defparam PLLA_inst.DE4_EN = "FALSE";
    defparam PLLA_inst.DE5_EN = "FALSE";
    defparam PLLA_inst.DE6_EN = "FALSE";
    defparam PLLA_inst.DYN_DPA_EN = "FALSE";
    defparam PLLA_inst.DYN_PE0_SEL = "FALSE";
    defparam PLLA_inst.DYN_PE1_SEL = "FALSE";
    defparam PLLA_inst.DYN_PE2_SEL = "FALSE";
    defparam PLLA_inst.DYN_PE3_SEL = "FALSE";
    defparam PLLA_inst.DYN_PE4_SEL = "FALSE";
    defparam PLLA_inst.DYN_PE5_SEL = "FALSE";
    defparam PLLA_inst.DYN_PE6_SEL = "FALSE";
    defparam PLLA_inst.RESET_I_EN = "FALSE";
    defparam PLLA_inst.RESET_O_EN = "FALSE";
    defparam PLLA_inst.ICP_SEL = 6'bXXXXXX;
    defparam PLLA_inst.LPF_RES = 3'bXXX;
    defparam PLLA_inst.LPF_CAP = 2'b00;
    defparam PLLA_inst.SSC_EN = "FALSE";
    defparam PLLA_inst.CLKOUT0_DT_STEP = 0;
    defparam PLLA_inst.CLKOUT1_DT_STEP = 0;
    defparam PLLA_inst.CLKOUT2_DT_STEP = 0;
    defparam PLLA_inst.CLKOUT3_DT_STEP = 0;

endmodule
"""
    else:
        extra_options = ""
        if limits["pll_name"] == "PLLVR":
            extra_options = ".VREN(1'b1),"
        pll_v = f"""/**
 * PLL configuration
 *
 * This Verilog module was generated automatically
 * using the gowin-pll tool.
 * Use at your own risk.
 *
 * Target-Device:                {args.device}
 * Given input frequency:        {args.input_freq_mhz:0.3f} MHz
 * Requested output frequency:   {args.output_freq_mhz:0.3f} MHz
 * Achieved output frequency:    {setup["CLKOUT"]:0.3f} MHz
 */

module {args.module_name}(
        input  clock_in,
        output clock_out,
        output locked
    );

    {limits["pll_name"]} #(
        .FCLKIN("{args.input_freq_mhz}"),
        .IDIV_SEL({setup["IDIV_SEL"]}), // -> PFD = {setup["PFD"]} MHz (range: {limits["pfd_min"]}-{limits["pfd_max"]} MHz)
        .FBDIV_SEL({setup["FBDIV_SEL"]}), // -> CLKOUT = {setup["CLKOUT"]} MHz (range: {limits["vco_min"]}-{limits["clkout_max"]} MHz)
        .ODIV_SEL({setup["ODIV_SEL"]}) // -> VCO = {setup["VCO"]} MHz (range: {limits["clkout_max"]}-{limits["vco_max"]} MHz)
    ) pll (.CLKOUTP(), .CLKOUTD(), .CLKOUTD3(), .RESET(1'b0), .RESET_P(1'b0), .CLKFB(1'b0), .FBDSEL(6'b0), .IDSEL(6'b0), .ODSEL(6'b0), .PSDA(4'b0), .DUTYDA(4'b0), .FDLY(4'b0), {extra_options}
        .CLKIN(clock_in), // {args.input_freq_mhz} MHz
        .CLKOUT(clock_out), // {setup["CLKOUT"]} MHz
        .LOCK(locked)
    );

endmodule

"""
    if args.filename:
        print(f" * Given input frequency:        {args.input_freq_mhz:0.3f} MHz")
        print(f" * Requested output frequency:   {args.output_freq_mhz:0.3f} MHz")
        print(f" * Achieved output frequency:    {setup['CLKOUT']:0.3f} MHz")
        open(args.filename, "w").write(pll_v)
    else:
        print(pll_v)
