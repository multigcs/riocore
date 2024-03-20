#!/usr/bin/env python3
#
#

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
        rio_c = open(f"tests/unit/output/{target}/LinuxCNC/rio.c", "r").read()
        if "spi_trx(txBuffer, rxBuffer, BUFFER_SIZE);" not in rio_c:
            assert False
        rio_v = open(f"tests/unit/output/{target}/Gateware/rio.v", "r").read()
        if "spi #(" not in rio_v:
            assert False
