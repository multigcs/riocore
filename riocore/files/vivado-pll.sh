#!/bin/bash
#
# this is a placeholder script, can only geneerate 100Mhz->125Mhz+25Mhz clock for Arty7-35t board

DEVICE="$1"
IN_MHZ="$2"
OUT_MHZ="$3"
FILE="$4" # PLL.v

if test "$FILE" = ""
then
    echo "USAGE $0 DEVICE IN OUT FILE" >&2
    echo "" >&2
    echo "    DEVICE : example: ---" >&2
    echo "    IN     : input freq in MHz" >&2
    echo "    OUT    : output freq in MHz" >&2
    echo "    FILE   : output file (example: PLL.v)" >&2
    echo "" >&2
    exit 1
fi

BASENAME=`basename $FILE .v`

echo "generating $FILE.."

cat <<EOF  > "$FILE"

module pll (
        input  clock_in,
        output clock_out,
        output clock25_out,
        output reset,
        output locked
    );

    wire clk_ibufg;
    wire clk_mmcm_out;
    wire clk_int;
    wire rst_int;

    wire locked;
    wire mmcm_clkfb;

    IBUFG clk_ibufg_inst(
        .I(clock_in),
        .O(clk_ibufg)
    );

    wire clk_25mhz_mmcm_out;

    MMCME2_BASE #(
        .BANDWIDTH("OPTIMIZED"),
        .CLKOUT0_DIVIDE_F(8),
        .CLKOUT0_DUTY_CYCLE(0.5),
        .CLKOUT0_PHASE(0),
        .CLKOUT1_DIVIDE(40),
        .CLKOUT1_DUTY_CYCLE(0.5),
        .CLKOUT1_PHASE(0),
        .CLKOUT2_DIVIDE(1),
        .CLKOUT2_DUTY_CYCLE(0.5),
        .CLKOUT2_PHASE(0),
        .CLKOUT3_DIVIDE(1),
        .CLKOUT3_DUTY_CYCLE(0.5),
        .CLKOUT3_PHASE(0),
        .CLKOUT4_DIVIDE(1),
        .CLKOUT4_DUTY_CYCLE(0.5),
        .CLKOUT4_PHASE(0),
        .CLKOUT5_DIVIDE(1),
        .CLKOUT5_DUTY_CYCLE(0.5),
        .CLKOUT5_PHASE(0),
        .CLKOUT6_DIVIDE(1),
        .CLKOUT6_DUTY_CYCLE(0.5),
        .CLKOUT6_PHASE(0),
        .CLKFBOUT_MULT_F(10),
        .CLKFBOUT_PHASE(0),
        .DIVCLK_DIVIDE(1),
        .REF_JITTER1(0.010),
        .CLKIN1_PERIOD(10.0),
        .STARTUP_WAIT("FALSE"),
        .CLKOUT4_CASCADE("FALSE")
    ) clk_mmcm_inst (
        .CLKIN1(clk_ibufg),
        .CLKFBIN(mmcm_clkfb),
        .RST(0),
        .PWRDWN(1'b0),
        .CLKOUT0(clk_mmcm_out),
        .CLKOUT0B(),
        .CLKOUT1(clk_25mhz_mmcm_out),
        .CLKOUT1B(),
        .CLKOUT2(),
        .CLKOUT2B(),
        .CLKOUT3(),
        .CLKOUT3B(),
        .CLKOUT4(),
        .CLKOUT5(),
        .CLKOUT6(),
        .CLKFBOUT(mmcm_clkfb),
        .CLKFBOUTB(),
        .LOCKED(locked)
    );

    BUFG clk_bufg_inst (
        .I(clk_mmcm_out),
        .O(clock_out)
    );

    BUFG clk_25mhz_bufg_inst (
        .I(clk_25mhz_mmcm_out),
        .O(clock25_out)
    );

    sync_reset #(
        .N(4)
    ) sync_reset_inst (
        .clk(clock_out),
        .rst(~locked),
        .out(reset)
    );

endmodule

EOF

echo "..done"
echo "OUTPUT FREQ: 125Mhz / 25Mhz"
