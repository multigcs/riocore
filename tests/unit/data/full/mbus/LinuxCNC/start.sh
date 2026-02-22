#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

### fpga (fpga0) ###
sudo halcompile --install "$DIRNAME/riocomp-fpga0.c"

linuxcnc "$DIRNAME/rio.ini" $@
