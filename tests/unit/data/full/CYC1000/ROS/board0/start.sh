#!/bin/sh

set -e
set -x

DIRNAME=`dirname "$0"`

echo "compile package:"
(cd "$DIRNAME" && catkin_make)

echo "running rosbridge:"
$DIRNAME/devel/lib/riobridge/rosbridge

