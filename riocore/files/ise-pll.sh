#!/bin/bash
#
# this is a placeholder script, can only geneerate 50Mhz->100Mhz clock for Spartan6 board

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
        .CLKFBOUT_MULT      (4),
        .CLKFBOUT_PHASE     (0.000),
        .CLKOUT0_DIVIDE     (2),
        .CLKOUT0_PHASE      (0.0),
        .CLKOUT0_DUTY_CYCLE (0.500),
        .CLKIN_PERIOD       (10.0),
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

EOF

echo "..done"
echo "OUTPUT FREQ: 100Mhz"
