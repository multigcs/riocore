#!/bin/bash
#
#

DEVICE="$1" # "MAX 10"
IN_MHZ="$2" # 50
OUT_MHZ="$3" # 100
FILE="$4" # PLL.v

if test "$FILE" = ""
then
    echo "USAGE $0 DEVICE IN OUT FILE" >&2
    echo "" >&2
    echo "    DEVICE : example: MAX 10" >&2
    echo "    IN     : input freq in MHz" >&2
    echo "    OUT    : output freq in MHz" >&2
    echo "    FILE   : output file (example: PLL.v)" >&2
    echo "" >&2
    exit 1
fi

BASENAME=`basename $FILE .v`

echo "generating $FILE.."

cat <<EOF  > "$FILE"
// megafunction wizard: %ALTPLL%
// GENERATION: STANDARD
// VERSION: WM1.0
// MODULE: altpll 

// ============================================================
// CNX file retrieval info
// ============================================================
// Retrieval info: PRIVATE: INCLK0_FREQ_EDIT STRING "$IN_MHZ"
// Retrieval info: PRIVATE: INCLK0_FREQ_UNIT_COMBO STRING "MHz"

// Retrieval info: PRIVATE: OUTPUT_FREQ0 STRING "$OUT_MHZ"
// Retrieval info: PRIVATE: OUTPUT_FREQ_MODE0 STRING "1"
// Retrieval info: PRIVATE: OUTPUT_FREQ_UNIT0 STRING "MHz"

// Retrieval info: PRIVATE: INTENDED_DEVICE_FAMILY STRING "$DEVICE"
// Retrieval info: PRIVATE: PLL_ADVANCED_PARAM_CHECK STRING "1"
// Retrieval info: PRIVATE: PLL_ARESET_CHECK STRING "0"
// Retrieval info: PRIVATE: PLL_AUTOPLL_CHECK NUMERIC "1"
// Retrieval info: PRIVATE: PLL_ENHPLL_CHECK NUMERIC "0"
// Retrieval info: PRIVATE: PLL_FASTPLL_CHECK NUMERIC "0"
// Retrieval info: PRIVATE: PLL_FBMIMIC_CHECK STRING "0"
// Retrieval info: PRIVATE: PLL_LVDS_PLL_CHECK NUMERIC "0"
// Retrieval info: PRIVATE: PLL_PFDENA_CHECK STRING "0"
// Retrieval info: PRIVATE: PLL_TARGET_HARCOPY_CHECK NUMERIC "0"
// Retrieval info: PRIVATE: PRIMARY_CLK_COMBO STRING "inclk0"
// Retrieval info: PRIVATE: LOCKED_OUTPUT_CHECK STRING "1"

// Retrieval info: GEN_FILE: TYPE_NORMAL $BASENAME.v TRUE
// Retrieval info: GEN_FILE: TYPE_NORMAL $BASENAME.ppf FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL $BASENAME.inc FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL $BASENAME.cmp FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL $BASENAME.bsf FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL $BASENAME_inst.v FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL $BASENAME_bb.v FALSE
EOF

qmegawiz -silent $FILE
echo "..done"

OUTPUT=`grep EFF_OUTPUT_FREQ_VALUE0 "$FILE" | cut -d'"' -f2`
echo "OUTPUT FREQ: $OUTPUT"


