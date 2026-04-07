#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

linuxcnc "$DIRNAME/rio.ini" $@
