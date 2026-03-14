#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

### fpga (board0) ###
sudo halcompile --install "$DIRNAME/riocomp-board0.c"

sudo mkdir -p /usr/share/qtvcp/panels/rio-gui/
sudo mkdir -p /usr/share/qtvcp/panels/rio-gui/
sudo cp -a "$DIRNAME/rio-gui_handler.py" /usr/share/qtvcp/panels/rio-gui/
sudo cp -a "$DIRNAME/rio-gui.ui" /usr/share/qtvcp/panels/rio-gui/
linuxcnc "$DIRNAME/rio.ini" $@
