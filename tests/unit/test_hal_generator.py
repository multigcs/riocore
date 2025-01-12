#!/usr/bin/env python3
#
#

import pytest

from riocore.generator.hal import hal_generator


def test_generator():
    expected_hal = """
#################################################################################
# logic and calc components
#################################################################################
loadrt logic names=func.and_0.1,func.and_2.1,func.or_3.1,func.and_6.1,func.or_7.1,func.and_7.2,func.or_8.1,func.or_10.1 personality=0x102,0x102,0x204,0x102,0x203,0x103,0x202,0x202
addf func.and_0.1 servo-thread
addf func.and_2.1 servo-thread
addf func.or_3.1 servo-thread
addf func.and_6.1 servo-thread
addf func.or_7.1 servo-thread
addf func.and_7.2 servo-thread
addf func.or_8.1 servo-thread
addf func.or_10.1 servo-thread

loadrt not names=func.not_pio_input1,func.not_pio_input2,func.not_oio_bit9
addf func.not_pio_input1 servo-thread
addf func.not_pio_input2 servo-thread
addf func.not_oio_bit9 servo-thread

loadrt sum2 names=func.sum2_4.1,func.sum2_9.1
addf func.sum2_4.1 servo-thread
addf func.sum2_9.1 servo-thread

loadrt mult2 names=func.mult2_5.1,func.mult2_5.2
addf func.mult2_5.1 servo-thread
addf func.mult2_5.2 servo-thread

loadrt div2 names=func.div2_5.3
addf func.div2_5.3 servo-thread

#################################################################################
# !rio.input1 --> hal.output2
#################################################################################
net sig_rio_input1-not             <= rio.input1-not
net sig_rio_input1-not             => hal.output2

#################################################################################
# rio.input1 --> hal.output1
#################################################################################
net sig_rio_input1                 <= rio.input1
net sig_rio_input1                 => hal.output1

#################################################################################
# rio.input1 and !rio.input2 --> hal.output3
#################################################################################
net sig_rio_input2-not             <= rio.input2-not
net sig_rio_input1                 => func.and_0.1.in-00
net sig_rio_input2-not             => func.and_0.1.in-01
net func_and_0_1_and               <= func.and_0.1.and
net func_and_0_1_and               => hal.output3

#################################################################################
# !pio.input1 --> hal.pio_output2
#################################################################################
net sig_pio_input1                 <= pio.input1
net sig_pio_input1                 => func.not_pio_input1.in
net func_not_pio_input1_out        <= func.not_pio_input1.out
net func_not_pio_input1_out        => hal.pio_output2

#################################################################################
# pio.input1 --> hal.pio_output1
#################################################################################
net sig_pio_input1                 => hal.pio_output1

#################################################################################
# pio.input1 and !pio.input2 --> hal.pio_output3
#################################################################################
net sig_pio_input2                 <= pio.input2
net sig_pio_input1                 => func.and_2.1.in-00
net func_not_pio_input2_out        => func.and_2.1.in-01
net func_and_2_1_and               <= func.and_2.1.and
net sig_pio_input2                 => func.not_pio_input2.in
net func_not_pio_input2_out        <= func.not_pio_input2.out
net func_and_2_1_and               => hal.pio_output3

#################################################################################
# rio.input2 or pyvcp.input3 OR |rio.input2 OR rio.input3 --> hal.or_out
#################################################################################
net sig_rio_input2                 <= rio.input2
# net sig_pyvcp_input3               <= pyvcp.input3 (in postgui)
net sig_rio_input3                 <= rio.input3
net sig_rio_input2                 => func.or_3.1.in-00
net sig_pyvcp_input3               => func.or_3.1.in-01
net sig_rio_input2                 => func.or_3.1.in-02
net sig_rio_input3                 => func.or_3.1.in-03
net func_or_3_1_or                 <= func.or_3.1.or
net func_or_3_1_or                 => hal.or_out

#################################################################################
# rio.s32_1 + rio.s32_2 + rio.s32_3 OR rio.s32_1 - rio.s32_2 --> hal.out-sint
#################################################################################
net sig_rio_s32_1                  <= rio.s32_1
net sig_rio_s32_2                  <= rio.s32_2
net sig_rio_s32_3                  <= rio.s32_3
net sig_rio_s32_1                  => func.sum2_4.1.in0
net sig_rio_s32_2                  => func.sum2_4.1.in1
net sig_rio_s32_3                  => func.sum2_4.1.in2
net sig_rio_s32_1                  => func.sum2_4.1.in3
net sig_rio_s32_2                  => func.sum2_4.1.in4
net func_sum2_4_1_out              <= func.sum2_4.1.out
net func_sum2_4_1_out              => hal.out-sint

#################################################################################
# (rio.float_1 * rio.float_2) / (rio.float_3 * rio.float_4) --> hal.out-float
#################################################################################
net sig_rio_float_1                <= rio.float_1
net sig_rio_float_2                <= rio.float_2
net sig_rio_float_3                <= rio.float_3
net sig_rio_float_4                <= rio.float_4
net sig_rio_float_1                => func.mult2_5.1.in0
net sig_rio_float_2                => func.mult2_5.1.in1
net func_mult2_5_1_out             <= func.mult2_5.1.out
net sig_rio_float_3                => func.mult2_5.2.in0
net sig_rio_float_4                => func.mult2_5.2.in1
net func_mult2_5_2_out             <= func.mult2_5.2.out
net func_mult2_5_1_out             => func.div2_5.3.in0
net func_mult2_5_2_out             => func.div2_5.3.in1
net func_div2_5_3_out              <= func.div2_5.3.out
net func_div2_5_3_out              => hal.out-float

#################################################################################
# &rio.input4 AND rio.input5 --> pyvcp.and_out
#################################################################################
net sig_rio_input4                 <= rio.input4
net sig_rio_input5                 <= rio.input5
net sig_rio_input4                 => func.and_6.1.in-00
net sig_rio_input5                 => func.and_6.1.in-01
net func_and_6_1_and               <= func.and_6.1.and
# net func_and_6_1_and               => pyvcp.and_out (in postgui)

#################################################################################
# &rio.input8 AND (sig:existing or rio.input5 or rio.input6) and rio.input7 --> pyvcp.complex_out
#################################################################################
net sig_rio_input6                 <= rio.input6
net sig_rio_input8                 <= rio.input8
net sig_rio_input7                 <= rio.input7
net existing                       => func.or_7.1.in-00
net sig_rio_input5                 => func.or_7.1.in-01
net sig_rio_input6                 => func.or_7.1.in-02
net func_or_7_1_or                 <= func.or_7.1.or
net sig_rio_input8                 => func.and_7.2.in-00
net func_or_7_1_or                 => func.and_7.2.in-01
net sig_rio_input7                 => func.and_7.2.in-02
net my_complex_out                 <= func.and_7.2.and
# net my_complex_out                 => pyvcp.complex_out (in postgui)

#################################################################################
# (rio.input5 or rio.input6) --> rio.orout1
#################################################################################
net sig_rio_input5                 => func.or_8.1.in-00
net sig_rio_input6                 => func.or_8.1.in-01
net func_or_8_1_or                 <= func.or_8.1.or
net func_or_8_1_or                 => rio.orout1

#################################################################################
# (rio.input5 or rio.input6) --> rio.orout2
#################################################################################
net func_or_8_1_or                 => rio.orout2

#################################################################################
# rio.float + 10 --> rio.fout
#################################################################################
net sig_rio_float                  <= rio.float
net sig_rio_float                  => func.sum2_9.1.in0
net func_sum2_9_1_out              <= func.sum2_9.1.out
net func_sum2_9_1_out              => rio.fout

#################################################################################
# rio.bit or 0 --> rio.bitor0
#################################################################################
net sig_rio_bit                    <= rio.bit
net sig_rio_bit                    => func.or_10.1.in-00
net func_or_10_1_or                <= func.or_10.1.or
net func_or_10_1_or                => rio.bitor0

#################################################################################
# oio.bit9 --> pio.multi1
#################################################################################
net multitarget                    <= oio.bit9
net multitarget                    => pio.multi1

#################################################################################
# !oio.bit9 --> pio.multi2
#################################################################################
net multitarget                    => func.not_oio_bit9.in
net multitarget_not                <= func.not_oio_bit9.out
net multitarget_not                => pio.multi2

#################################################################################
# setp
#################################################################################
# setp pyvcp.outval                     123    (in postgui)
setp rio.outval                       123
# setp rio.orout1                       0      (already linked to func_or_8_1_or)
# setp rio.s32_1                        100    (already linked to sig_rio_s32_1)
setp func.sum2_9.1.in1                10
setp func.or_10.1.in-01               0

#################################################################################
# preformated
#################################################################################
"""

    expected_postgui = """
#################################################################################
# networks
#################################################################################
net sig_pyvcp_input3               <= pyvcp.input3
net func_and_6_1_and               => pyvcp.and_out
net my_complex_out                 => pyvcp.complex_out

#################################################################################
# setp
#################################################################################
setp pyvcp.outval                     123
"""

    halg = hal_generator()

    halg.net_add("!rio.input1", "hal.output2")
    halg.net_add("rio.input1", "hal.output1")
    halg.net_add("rio.input1 and !rio.input2", "hal.output3")

    halg.net_add("!pio.input1", "hal.pio_output2")
    halg.net_add("pio.input1", "hal.pio_output1")
    halg.net_add("pio.input1 and !pio.input2", "hal.pio_output3")

    halg.net_add("rio.input2 or pyvcp.input3", "hal.or_out")
    halg.net_add("rio.s32_1 + rio.s32_2 + rio.s32_3", "hal.out-sint")
    halg.net_add("(rio.float_1 * rio.float_2) / (rio.float_3 * rio.float_4)", "hal.out-float")
    halg.net_add("rio.s32_1 - rio.s32_2", "hal.out-sint")

    halg.net_add("|rio.input2", "hal.or_out")
    halg.net_add("rio.input3", "hal.or_out")

    halg.net_add("&rio.input4", "pyvcp.and_out")
    halg.net_add("rio.input5", "pyvcp.and_out")

    halg.net_add("&rio.input8", "pyvcp.complex_out")
    halg.net_add("(sig:existing or rio.input5 or rio.input6) and rio.input7", "pyvcp.complex_out", "my_complex_out")

    halg.net_add("(rio.input5 or rio.input6)", "rio.orout1")
    halg.net_add("(rio.input5 or rio.input6)", "rio.orout2")

    halg.setp_add("pyvcp.outval", "123")
    halg.setp_add("rio.outval", "123")
    halg.setp_add("rio.orout1", "0")
    halg.setp_add("rio.s32_1", "100")

    halg.net_add("rio.float + 10", "rio.fout")
    halg.net_add("rio.bit or 0", "rio.bitor0")

    halg.net_add("oio.bit9", "pio.multi1, !pio.multi2", "multitarget")

    (hal_data, postgui_data) = halg.net_write()
    # print("---------------------------------")
    # print("\n".join(hal_data))
    # print("---------------------------------")
    # print("\n".join(postgui_data))
    # print("---------------------------------")

    assert "\n".join(hal_data).strip() == expected_hal.strip()
    assert "\n".join(postgui_data).strip() == expected_postgui.strip()
