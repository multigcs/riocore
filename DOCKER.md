[LinuxCNC-RIO](https://github.com/multigcs/LinuxCNC-RIO)

<h3 align="center">LinuxCNC-RIO Docker Container</h3>

<div align="center">

  [![License](https://img.shields.io/badge/license-GPL2-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Realtime-IO for LinuxCNC<br></p>

## Table of Contents
- [About](#about)
- [Prerequisites](#prerequisites)
- [Build and Run](#run)
- [FAQ](#faq)

## About <a name = "about"></a>

Docker allows you to contain all of the dependencies required to install and run riocore in one container, removing the complexity of differing setups and configurations of the host linux machine. This container will run the riocore gui, and should allow you to flash most fpga's that work similarly to the TangNano boards, and work with the oss-cad-suite (ie. work with the icestorm toolchain).

The directory that you have cloned riocore into will be mounted in /workspace, allowing you to save your config and output there to be usable like normal outside of the container.

The docker image will persist, making it fast and easy to rerun the gui for that period of time when you are rapidly iterating your config. You can always remove it if you need to reclaim the space:
`docker rmi riocore`

NOTE: this is only tested with a TangNano9k using the TangNano9k-icestorm board config on an Ubuntu 24.04 host.

## Prerequisites <a name = "prerequisites"></a>

You require 2 things:
- A linux system. You probably already have this, since you're working with linuxcnc
- Docker. Most distributions of linux including those for the Raspberry Pi distribute Docker through their package manager.

Note: More information in the [FAQ](#faq).  

## Build and Run <a name = "run"></a>

Get the codebase:

via git:
```
git clone https://github.com/multigcs/riocore.git
cd riocore
```

or download and extract the zip from the green "Code" button at https://github.com/multigcs/riocore

build and run the conainer
``` 
make docker-run
```

if you already have a config file and wish to load it, you can do so in the first screen of the gui, or by passing it on the command line:
```
make docker-run CONFIG=./config.json
```


This will start riocore-setup as normal. Your riocore directory is mounted at /workspace/ so if you have already created a config, you can use the Load Existing Config button to load it from there. You can also save configs to that in later steps, and any generated and compiled output will be in /workspace/Output and you'll see it appear in your riocore directory outside of the container as well.

NOTE: any files created by the container will be owned by root, so if that's a hassle, you may chown/chgrp it back to your user (mine is named cnc in this example, replace it with your user.):
```
cd /path/to/riocore/repo
sudo chown -R cnc:cnc ./
```

Once you are done flashing the FPGA you need to complie the LinuxCNC module. This only needs to happen once. 
```
sudo halcompile --install riocore/files/rio.c
```

Then you can start LinuxCNC with your new .ini file:
```
linuxcnc Output/BOARD_NAME/LinuxCNC/rio.ini
```

## FAQ <a name = "faq"></a>

- How to install Docker?  Ubuntu/debian: `sudo apt-get -y install docker.io`
- I get permission errors when I start `make docker-run`. I tried `sudo make docker-run` and it won't start either.

	Your Linux user need to have the rights to run docker. Add your user to the docker group, give access to docker and restart your system.

```bash
sudo usermod -aG docker $USER
sudo chown root:docker /var/run/docker.sock
sudo chown -R root:docker /var/run/docker
sudo reboot
````
- Do I need to keep docker once I am done with flashing the FPGA?
No, you only need to be running docker while you're working with the riocore ui or generator, you may disable it when you're done to save resources if you prefer.
- I want to use a different toolchain for the Tang Nano 9k? To use the icestorm toolchain use `make docker-run` to use also the Gowin toolchain use `make docker-run-gowin`. 
