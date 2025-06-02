#!/bin/sh
#
#

for size in 48x48 96x96 128x128 256x256 640x480 800x600
do
    echo $size
    test -e doc/images/rio-logo-$size.png || convert -scale $size doc/images/rio-logo.svg doc/images/rio-logo-$size.png
done


