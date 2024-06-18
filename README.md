LinuxCNC-RIO - rewrite

in progress but ready for testing

---


# 

<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/6wj0hh6.jpg" alt="LinuxCNC-RIO"></a>
</p>

<h3 align="center">LinuxCNC-RIO</h3>

<div align="center">

  [![License](https://img.shields.io/badge/license-GPL2-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Few lines describing your project.
    <br> 
</p>

## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [TODO](../TODO.md)

## 🧐 About <a name = "about"></a>

LinuxCNC-RIO is a code generator for using FPGA boards as real-time IO for LinuxCNC.

Furthermore, the complete configuration and hal is generated.
a json configuration file serves as the basis


## 🏁 Getting Started <a name = "getting_started"></a>

installing via git:
```
git clone https://github.com/multigcs/riocore.git
git clone https://github.com/multigcs/riogui.git
cd riocore
```

make sure that the toolchain matching your fpga is in the path:
```
export PATH=$PATH:/opt/oss-cad-suite/bin/
export PATH=$PATH:/opt/gowin/IDE/bin/
```

than copy a config file that is near to your setup:
```
cp riocore/configs/Tangoboard/config-spi.json my_config.json
```

## 🎈 Usage <a name="usage"></a>
Add notes about how to use the system.

you can edit your configuration file by hand (text-editor) or using the setup tool (rio-setup):
```
PYTHONPATH=. ../riogui/bin/rio-setup my_config.json
```

![basic setup](./doc/images/basic_setup.png)


after setup, you can save your configuration and generate the output-files in the setup-tool via buttons:

* Generate : generates the output-files and write it into the './Output/' folder
* Compile: compiles the Bitfile for your FPGA
* Flash: writes the new bitfile onto the FPGA

you can also do this things on your console:

generate:
```
PYTHONPATH=. bin/rio-generator my_config.json
```
```
loading: my_config.json
loading board setup: TangNano9K
writing gateware to: Output/Tangoboard/Gateware
!!! gateware changed: needs to be build and flash |||
loading toolchain gowin
writing linuxcnc files to: Output/Tangoboard/LinuxCNC
```
compile:
```
(
cd Output/BOARD_NAME/Gateware/
make clean all
)
```

flash:
```
(
cd Output/BOARD_NAME/Gateware/
make load
)
```

You can find all the LinuxCNC related files in 'Output/BOARD_NAME/LinuxCNC/',

to start LinuxCNC, you have to install the new component first:
```
halcompile --install Output/BOARD_NAME/LinuxCNC/rio.c
```

then you can start LinuxCNC with your new .ini file:
```
linuxcnc Output/BOARD_NAME/LinuxCNC/rio.ini
```



### Prerequisites
you need the toolchain for your FPGA or in some cases the https://github.com/YosysHQ/oss-cad-suite-build


