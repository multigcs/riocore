#!/bin/sh
#
#

for size in 48x48 96x96 128x128 640x480 800x600
do
    echo $size
    convert -scale $size riocore/files/rio-logo.svg riocore/files/rio-logo-$size.png
done


