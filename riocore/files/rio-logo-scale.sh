#!/bin/sh
#
#

for size in 48x48 96x96 128x128 256x256 640x480 800x600
do
    echo $size
    test -e riocore/files/rio-logo-$size.png || convert -scale $size riocore/files/rio-logo.svg riocore/files/rio-logo-$size.png
done


