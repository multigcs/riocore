#!/usr/bin/env python3
#
#

import glob
import os
import pytest
import riocore
import os.path
import shutil


@pytest.mark.parametrize(
    "config, target, protocol",
    (
        (
            "config1.json",
            "Tangoboard",
            "SPI",
        ),
    ),
)
def test_generator(config, target, protocol):
    if os.path.exists("tests/unit/output"):
        shutil.rmtree("tests/unit/output")
    project = riocore.Project(f"tests/unit/data/{config}", "tests/unit/output")
    project.generator(True)

    if not os.path.exists(f"tests/unit/output/{target}/LinuxCNC/rio.hal"):
        assert False

    if protocol == "SPI":
        riocomp_c = open(f"tests/unit/output/{target}/LinuxCNC/riocomp.c", "r").read()
        if "spi_trx(txBuffer, rxBuffer, BUFFER_SIZE);" not in riocomp_c:
            assert False
        rio_v = open(f"tests/unit/output/{target}/Gateware/rio.v", "r").read()
        if "spi #(" not in rio_v:
            assert False


@pytest.mark.parametrize(
    "config, target, protocol, ip, home_sequence, ini_values",
    (
        (
            "config-ini1.json",
            "TangIni1",
            "UDP",
            "192.168.20.194",
            [-1, -2, -3, -4],
            {
                "DEFAULT_LINEAR_VELOCITY": "60.0",
                "MAX_LINEAR_VELOCITY": "60.0",
                "INCREMENTS": "5mm 1mm .5mm .1mm .05mm .01mm",
                "JOINTS": "4",
                "KINEMATICS": "trivkins coordinates=XYYZ kinstype=B",
                "COORDINATES": "X YY Z",
                "DEFAULT_LINEAR_VELOCITY": "5.0",
                "MAX_LINEAR_VELOCITY": "60.0",
            },
        ),
    ),
)
def test_generator_ini(config, target, protocol, ip, home_sequence, ini_values):
    if os.path.exists("tests/unit/output"):
        shutil.rmtree("tests/unit/output")
    project = riocore.Project(f"tests/unit/data/{config}", "tests/unit/output")
    project.generator(True)

    if not os.path.exists(f"tests/unit/output/{target}/LinuxCNC/rio.hal"):
        assert False

    if protocol == "UDP":
        riocomp_c = open(f"tests/unit/output/{target}/LinuxCNC/riocomp.c", "r").read()
        if f'#define UDP_IP "{ip}"' not in riocomp_c:
            assert False
        if "udp_trx(txBuffer, rxBuffer, BUFFER_SIZE);" not in riocomp_c:
            assert False
        rio_v = open(f"tests/unit/output/{target}/Gateware/rio.v", "r").read()
        if "w5500 #(" not in rio_v:
            assert False
        ip_split = ip.split(".")
        if f".IP_ADDR({{8'd{ip_split[0]}, 8'd{ip_split[1]}, 8'd{ip_split[2]}, 8'd{ip_split[3]}}})," not in rio_v:
            assert False

    ini = open(f"tests/unit/output/{target}/LinuxCNC/rio.ini", "r").read()
    for line in ini.split("\n"):
        if "HOME_SEQUENCE" in line:
            nh = home_sequence.pop(0)
            if int(line.split()[-1]) != nh:
                assert False

    for key, value in ini_values.items():
        print("key, value", key, value)
        found = False
        for line in ini.split("\n"):
            if f"{key} = {value}" in line:
                found = True
                break
        if not found:
            assert False


def test_generade_all():
    for config in glob.glob("riocore/configs/*/config.json"):
        print("###################")
        print(config)
        print("###################")
        # clean output directory
        if os.path.exists("tests/unit/output"):
            shutil.rmtree("tests/unit/output")

        # load project
        project = riocore.Project(config, "tests/unit/output")

        # force pll generator
        project.config["osc"] = 12000000
        project.config["osc_clock"] = 12000000
        project.config["speed"] = 24000000

        # generate
        project.generator(False)
        print("")

        if not os.path.exists(f"tests/unit/output/{project.config['name']}/Gateware/rio.v"):
            assert False

        if not os.path.exists(f"tests/unit/output/{project.config['name']}/LinuxCNC/rio.hal"):
            assert False

        if not os.path.exists(f"tests/unit/output/{project.config['name']}/LinuxCNC/rio.ini"):
            assert False
