#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

# compile and install dynamic-loader
# sudo halcompile --install riocore/files/rio.c

### fpga (fpga0) ###
# sudo halcompile --install "$DIRNAME/riocomp-fpga0.c"

linuxcnc "$DIRNAME/rio.ini" $@
