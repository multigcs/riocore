#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

### fpga (board0) ###
sudo halcompile --install "$DIRNAME/riocomp-board0.c"

linuxcnc "$DIRNAME/rio.ini" $@
