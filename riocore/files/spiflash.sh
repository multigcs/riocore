#!/bin/bash
#
# write Flash from raspberry over SPI
# please use the latest flashrom from: https://github.com/flashrom/flashrom.git
#
#


# if ! test -e /usr/src/flashrom
# then
#    (cd /usr/src && git clone https://github.com/flashrom/flashrom.git && cd flashrom && make)
# fi


BITFILE=$1
if test "$BITFILE" = ""
then
    echo "$0 BITFILE"
    exit 1
fi

SPIDEV="/dev/spidev0.1"
SPISPEED="20000"
SPISEL_FLASH="1"
SPISELPIN_FLASH="7"
RESETPIN="25"
FLASHSIZE="8M"

if test -e /sys/class/gpio/gpio$SPISELPIN_FLASH
then
    echo $SPISELPIN_FLASH > /sys/class/gpio/unexport
fi

sudo rmmod spidev 2>/dev/null
sudo rmmod spi_bcm2835 2>/dev/null
sudo modprobe spi_bcm2835 2>/dev/null
sudo modprobe spidev 2>/dev/null

echo $RESETPIN > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio$RESETPIN/direction
sleep .5

dd if=/dev/zero of=/tmp/_flash.bin  bs=$FLASHSIZE count=1
dd if=$BITFILE conv=notrunc of=/tmp/_flash.bin

flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED -w /tmp/_flash.bin || \
flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED -w /tmp/_flash.bin


sudo rmmod spidev
sudo rmmod spi_bcm2835
echo $SPISELPIN_FLASH > /sys/class/gpio/export
sleep 1
echo in > /sys/class/gpio/gpio$SPISELPIN_FLASH/direction
echo in > /sys/class/gpio/gpio$RESETPIN/direction

sleep 1
echo out > /sys/class/gpio/gpio$SPISELPIN_FLASH/direction
echo 1 > /sys/class/gpio/gpio$SPISELPIN_FLASH/value


