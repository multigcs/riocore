#!/bin/bash
#
# installer script for LinuxCNC-RIO
#

if ! lsb_release -c | grep -s -q "bookworm"
then
	echo "ONLY FOR DEBIAN BOOKWORK"
	exit 1
fi


PWD="`pwd`"
SYSTEM="arm64"
SYSTEM2="arm64"
if test "`uname -m`" = "x86_64"
then
	SYSTEM="x64"
	SYSTEM2="amd64"
fi

TARGETDIR=~
if test "$1" != "" && test -d "$1"
then
	TARGETDIR="$1"
fi

TEMPFILE="`mktemp /tmp/rioXXXXXX.tmp`"
TC_ICESTORM=""
TC_GOWIN=""

doexit() {
	rm -rf ${TEMPFILE} ${TEMPFILE}2
	exit $1
}

cd $TARGETDIR || doexit 1

echo "whiptail --checklist \"what do you want to install ?\\n Target-Directory: $TARGETDIR/riocore\" 20 72 12 \\" > ${TEMPFILE}2
echo "	apt \"install rio dependencies\" ON \\" >> ${TEMPFILE}2
if ! test -d riocore && ! test -e /usr/src/riocore
then
	echo "	rio \"git clone riocore\" ON \\" >> ${TEMPFILE}2
else
	echo "	rio \"git clone riocore\" OFF \\" >> ${TEMPFILE}2
fi
if ! which linuxcnc >/dev/null
then
	echo "	linuxcnc \"install rio component loader \" OFF \\" >> ${TEMPFILE}2
	echo "	halcompile \"install rio component loader \" OFF \\" >> ${TEMPFILE}2
else
	if ! test -e /usr/lib/linuxcnc/modules/rio.so
	then
		echo "	halcompile \"install rio component loader \" ON \\" >> ${TEMPFILE}2
	else
		echo "	halcompile \"install rio component loader \" OFF \\" >> ${TEMPFILE}2
	fi
fi
if ! test -d riocore/toolchains/oss-cad-suite && ! which nextpnr-himbaechel >/dev/null
then
	echo "	icestorm \"install OSS-Cad-Suite\" ON \\" >> ${TEMPFILE}2
else
	echo "	icestorm \"install OSS-Cad-Suite\" OFF \\" >> ${TEMPFILE}2
fi
if test "$SYSTEM" = "x64"
then
	if ! test -d riocore/toolchains/gowin/IDE && ! which gw_ide >/dev/null
	then
		echo "	gowin \"install Gowin Toolchain\" ON \\" >> ${TEMPFILE}2
	else
		echo "	gowin \"install Gowin Toolchain\" OFF \\" >> ${TEMPFILE}2
	fi
fi
echo "	autologin \"autologin/no screensaver\" ON \\" >> ${TEMPFILE}2
echo "	probe_basic \"install Probe-Basic GUI\" OFF \\" >> ${TEMPFILE}2
echo "	2> $TEMPFILE" >> ${TEMPFILE}2


if ! bash ${TEMPFILE}2
then
	rm -rf $TEMPFILE
	doexit 0
fi

if grep -s -q '"apt"' in $TEMPFILE
then
	if test "$SYSTEM" = "x64"
	then
		# removing unwanted package on amd/intel systems
		sudo dpkg --purge raspi-firmware || true
	fi
	echo "installing dependencies"
	sudo apt-get update || doexit 1
	sudo apt-get -y install git python3 python3-pip python3-yaml python3-graphviz python3-pyqtgraph python3-pyqt5 python3-pyqt5.qtsvg python3-lxml || doexit 1
fi

if grep -s -q '"rio"' in $TEMPFILE
then
	if ! test -d riocore
	then
		echo "installing riocore"
		git clone https://github.com/multigcs/riocore.git || doexit 1
	else
		echo "riocore already installed"
	fi
fi

if grep -s -q '"halcompile"' in $TEMPFILE
then
	if test -d riocore
	then
		echo "installing rio halcomponent loader"
		sudo halcompile --install riocore/riocore/files/rio.c
	else
		echo "halcompile: no riocore found"
	fi
fi

if grep -s -q '"icestorm"' in $TEMPFILE
then
	if ! test -d riocore/toolchains/oss-cad-suite
	then
		echo "installing icestorm"
		(
			mkdir -p riocore/toolchains/
			cd riocore/toolchains || doexit 1
			wget "https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-09-10/oss-cad-suite-linux-$SYSTEM-20240910.tgz" || doexit 1
			tar xzvpf oss-cad-suite-linux-$SYSTEM-20240910.tgz || doexit 1
			rm -rf oss-cad-suite-linux-$SYSTEM-20240910.tgz
		)
	else
		echo "icestorm already installed"
	fi
	TC_ICESTORM="$PWD/riocore/toolchains/oss-cad-suite"
fi

if grep -s -q '"gowin"' in $TEMPFILE
then
	if ! test -d riocore/toolchains/gowin/IDE
	then
		echo "installing gowin"
		(
			mkdir -p riocore/toolchains/gowin
			cd riocore/toolchains/gowin || doexit 1
			wget "https://cdn.gowinsemi.com.cn/Gowin_V1.9.10.03_Education_linux.tar.gz" || doexit 1
			tar xzvpf Gowin_V1.9.10.03_Education_linux.tar.gz || doexit 1
			rm -rf Gowin_V1.9.10.03_Education_linux.tar.gz
		)
	else
		echo "gowin already installed"
	fi
	TC_GOWIN="$PWD/riocore/toolchains/gowin/IDE"
fi

if test -e riocore/riocore && test "$TC_ICESTORM$TC_GOWIN" != ""
then
	echo "adding toolchains to riocore/riocore/toolchains.json"
	for TC in $TC_ICESTORM $TC_GOWIN
	do
		echo "    $TC"
	done
	cat <<EOF > riocore/riocore/toolchains.json 
{
    "icestorm": "$TC_ICESTORM",
    "gowin": "$TC_GOWIN",
    "diamond": "",
    "vivado": "",
    "quartus": "",
    "ise": ""
}
EOF
fi

if grep -s -q '"autologin"' in $TEMPFILE
then

	if dpkg -l | grep -s -q "ii  xscreensaver"
	then
		sudo apt-get remove -y xscreensaver
		sudo apt-get remove -y xscreensaver-data
	fi

	if ! grep -s -q "autologin-user" /usr/share/lightdm/lightdm.conf.d/01_debian.conf
	then
		cat <<EOF | sudo tee -a /usr/share/lightdm/lightdm.conf.d/01_debian.conf

[SeatDefaults]
autologin-user=$USER
autologin-user-timeout=0

EOF
	fi
	if ! test -e /usr/local/bin/startup.sh
	then
		cat <<EOF | sudo tee /usr/local/bin/startup.sh
#!/bin/bash
#
#

xset -dpms
xset s off
xset s noblank

EOF
		sudo chmod 755 /usr/local/bin/startup.sh

		mkdir -p ~/.config/autostart/
		cat <<EOF > ~/.config/autostart/startup.desktop
[Desktop Entry]
Name=startup.sh
Exec=startup.sh
EOF

	fi

	mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml/
	cat <<EOF > ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml 
<?xml version="1.0" encoding="UTF-8"?>

<channel name="xfce4-power-manager" version="1.0">
  <property name="xfce4-power-manager" type="empty">
    <property name="power-button-action" type="empty"/>
    <property name="show-tray-icon" type="bool" value="false"/>
    <property name="dpms-enabled" type="bool" value="false"/>
    <property name="dpms-on-ac-sleep" type="uint" value="22"/>
    <property name="blank-on-ac" type="int" value="21"/>
    <property name="dpms-on-ac-off" type="uint" value="29"/>
    <property name="lock-screen-suspend-hibernate" type="bool" value="false"/>
    <property name="logind-handle-lid-switch" type="bool" value="false"/>
  </property>
</channel>
EOF

fi

if grep -s -q '"probe_basic"' in $TEMPFILE
then
	if whiptail --menu "installing ProbeBasic" 20 60 12 stable "Stable" develop "Develop" 2> ${TEMPFILE}2
	then
		PB_BRANCH=`cat ${TEMPFILE}2`
		BASE_URL="https://repository.qtpyvcp.com/apt/pool/main/$PB_BRANCH"
		LAST_HIYAPYCO=`wget -q -O- $BASE_URL/ | grep "python3-hiyapyco_" | grep "${SYSTEM2}\|all" | tail -n1 | head -n1 | cut -d'"' -f2`
		LAST_PROBEBASIC=`wget -q -O- $BASE_URL/ | grep "python3-probe-basic_" | grep "${SYSTEM2}\|all" | tail -n1 | head -n1 | cut -d'"' -f2`
		LAST_QTPYVCP=`wget -q -O- $BASE_URL/ | grep "python3-qtpyvcp_" | grep "${SYSTEM2}\|all" | tail -n1 | head -n1 | cut -d'"' -f2`
		rm -f "./$LAST_HIYAPYCO" "./$LAST_PROBEBASIC" "./$LAST_QTPYVCP"
		if ! wget "$BASE_URL/$LAST_HIYAPYCO"
		then
			echo "probe_basic: ERROR getting python3-hiyapyco: $BASE_URL/$LAST_HIYAPYCO"
			rm -f "./$LAST_HIYAPYCO"
		fi
		if ! wget "$BASE_URL/$LAST_PROBEBASIC"
		then
			echo "probe_basic: ERROR getting python3-probe-basic: $BASE_URL/$LAST_PROBEBASIC"
			rm -f "./$LAST_PROBEBASIC"
		fi
		if ! wget "$BASE_URL/$LAST_QTPYVCP"
		then
			echo "probe_basic: ERROR getting python3-qtpyvcp: $BASE_URL/$LAST_QTPYVCP"
			rm -f "./$LAST_QTPYVCP"
		fi
		if test -e $LAST_HIYAPYCO && test -e $LAST_QTPYVCP && test -e $LAST_PROBEBASIC
		then
			sudo apt install -y debhelper-compat dh-python python4-setuptools python3-yaml python3-pyqt5.qtmultimedia python3-pyqt5.qtquick qml-module-qtquick-controls libqt5multimedia5-plugins python3-dev python3-docopt python3-qtpy python3-pyudev python3-psutil python3-markupsafe python3-vtk9 python3-pyqtgraph python3-simpleeval python3-jinja2 python3-deepdiff python3-sqlalchemy qttools5-dev-tools python3-serial python3-distro
			sudo dpkg -i $LAST_HIYAPYCO $LAST_QTPYVCP $LAST_PROBEBASIC || sudo apt-get install -y -f
		fi
	fi
fi


cd $TARGETDIR/riocore/
echo ""
echo "####################################################################"
echo ""
echo "# command examples:"
echo ""
echo "  cd $TARGETDIR/riocore/"
echo ""
echo "  # create new setup:"
echo "    bin/rio-setup riocore/configs/Tangbob/config.json"
echo ""
echo "  # generate, build and flash the Tangbob config"
echo "    bin/rio-generator -b -f riocore/configs/Tangbob/config.json"
echo ""
if ! which linuxcnc >/dev/null
then
	echo "  # generate and start linuxcnc for the Tangbob config"
	echo "    bin/rio-generator -s riocore/configs/Tangbob/config.json"
	echo ""
fi
echo "####################################################################"
echo ""

