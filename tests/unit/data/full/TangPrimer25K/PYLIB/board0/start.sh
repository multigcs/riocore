#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

echo "compile package:"
(cd "$DIRNAME" && make clean all)

echo "running rioclient:"
# LD_LIBRARY_PATH=$DIRNAME $DIRNAME/rioclient $@
$DIRNAME/testgui.py $@

