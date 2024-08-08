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


if ! test -e /sys/class/gpio/
then
    echo "ERROR: only runs on raspberry pi"
    exit 1
fi

BITFILE=$1
if test "$BITFILE" = ""
then
    echo "$0 BITFILE [SIZE]"
    exit 1
fi
if ! test -e "$BITFILE"
then
	echo "ERROR: bitfile not found: $BITFILE"
	exit 1
fi

SPIDEV="/dev/spidev0.1"
SPISPEED="20000"
SPISEL_FLASH="1"
SPISELPIN_FLASH="7"
RESETPIN="25"
FLASHSIZE="$2"

echo "bitfile: $BITFILE ..."
echo "  reload drivers / set FPGA into reset mode"
if test -e /sys/class/gpio/gpio$SPISELPIN_FLASH
then
    echo $SPISELPIN_FLASH > /sys/class/gpio/unexport
fi
sudo rmmod spidev 2>/dev/null
sudo rmmod spi_bcm2835 2>/dev/null
sudo modprobe spi_bcm2835 2>/dev/null
sudo modprobe spidev 2>/dev/null

if ! test -e /sys/class/gpio/gpio$RESETPIN
then
    echo $RESETPIN > /sys/class/gpio/export
fi
echo out > /sys/class/gpio/gpio$RESETPIN/direction
sleep .2

if test "$FLASHSIZE" = ""
then
	BITSIZE=`du -b $BITFILE| awk '{print $1}'`
	FLASHSIZE=`flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED --flash-size | tail -n1 | grep "^[1-9]"`
	if test "$FLASHSIZE" -lt "$BITSIZE"
	then
		echo "   ERROR: bitfile is to big for the flash: $FLASHSIZE > $BITSIZE"
		exit 1
	fi 
fi

echo "  fill bitfile with zeros to reach flashsize: $FLASHSIZE"
if ! dd if=/dev/zero of=/tmp/_flash.bin  bs=$FLASHSIZE count=1 2> /dev/null
then
	echo "   ERROR: dd can not read/write: dd if=/dev/zero of=/tmp/_flash.bin  bs=$FLASHSIZE count=1"
	exit 1
fi
if ! dd if=$BITFILE conv=notrunc of=/tmp/_flash.bin 2> /dev/null
then
	echo "   ERROR: dd can not read/write: dd if=$BITFILE conv=notrunc of=/tmp/_flash.bin"
	exit 1
fi

echo "  write to flash"
if ! flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED -w /tmp/_flash.bin > /tmp/_flash.log
then
	echo "   ERROR: flashrom: `cat /tmp/_flash.log`"
	echo "   retry.."
	if ! flashrom -p linux_spi:dev=$SPIDEV,spispeed=$SPISPEED -w /tmp/_flash.bin > /tmp/_flash.log
	then
		echo "   ERROR: flashrom: `cat /tmp/_flash.log`"
	fi
fi

echo "  unload drivers / reset FPGA"
sudo rmmod spidev
sudo rmmod spi_bcm2835
echo $SPISELPIN_FLASH > /sys/class/gpio/export
sleep 1
echo in > /sys/class/gpio/gpio$SPISELPIN_FLASH/direction
echo in > /sys/class/gpio/gpio$RESETPIN/direction

sleep 1
echo out > /sys/class/gpio/gpio$SPISELPIN_FLASH/direction
echo 1 > /sys/class/gpio/gpio$SPISELPIN_FLASH/value

echo "...done"
