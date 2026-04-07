#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

# compile and install dynamic-loader
# sudo halcompile --install riocore/files/rio.c

### fpga (board0) ###
# sudo halcompile --install "$DIRNAME/riocomp-board0.c"

linuxcnc "$DIRNAME/rio.ini" $@
