#!/bin/sh
#
# Mesa7c81 flashtool for rio gateware
#

if ! test -e /sys/class/gpio/
then
    echo "ERROR: only runs on raspberry pi"
    exit 1
fi

BOOTMODE_PIN="25"

echo $BOOTMODE_PIN > /sys/class/gpio/export 2>/dev/null
echo out > /sys/class/gpio/gpio$BOOTMODE_PIN/direction
echo 1 > /sys/class/gpio/gpio$BOOTMODE_PIN/value
sleep .3
if flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=7000 -w $1
then
    echo ""
    echo "----------------------------------------------------"
    echo "done"
    echo "----------------------------------------------------"
    echo ""
	echo 0 > /sys/class/gpio/gpio$BOOTMODE_PIN/value
	exit 0
else
	echo "retry.."
	sleep 1
	if flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed=7000 -w $1
	then
        echo ""
        echo "----------------------------------------------------"
        echo "done"
        echo "----------------------------------------------------"
        echo ""
		echo 0 > /sys/class/gpio/gpio$BOOTMODE_PIN/value
		exit 0
	fi
fi
echo ""
echo "----------------------------------------------------"
echo " ERROR writing flash !"
echo " holding Gateware in flashmode to prevent a reload"
echo " please check and retry or execute:"
echo " # echo 0 > /sys/class/gpio/gpio$BOOTMODE_PIN/value"
echo " to reload"
echo "----------------------------------------------------"
echo ""
exit 1




