#!/bin/sh
#
# Mesa7c81 flashtool for rio gateware
#

if ! test -e /sys/class/gpio/
then
    echo "ERROR: only runs on raspberry pi"
    exit 1
fi

echo 25 > /sys/class/gpio/export 2>/dev/null
echo out > /sys/class/gpio/gpio25/direction
echo 1 > /sys/class/gpio/gpio25/value
if flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=7000 -w $1
then
	echo 0 > /sys/class/gpio/gpio25/value
	exit 0
else
	echo "retry.."
	sleep 1
	if flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=7000 -w $1
	then
		echo 0 > /sys/class/gpio/gpio25/value
		exit 0
	fi
fi
echo ""
echo "----------------------------------------------------"
echo " ERROR writing flash !"
echo " holding Gateware in flashmode to prevent a reload"
echo " please check and retry or"
echo "----------------------------------------------------"
echo ""
exit 1




