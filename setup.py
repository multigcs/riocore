#!/usr/bin/env python3
#
#

import os
import glob
from setuptools import setup
from riocore.VERSION import VERSION


scripts = []
package_data = {
    "riocore": [
        "files/*",
        "boards/*",
        "modules/*",
        "configs/*/*",
    ],
}
packages = ["riocore"]

for script in glob.glob("bin/*"):
    if not "gui" in script:
        scripts.append(script)

for folder in ("riocore/plugins/*", "riocore/generator/*", "riocore/generator/pins/*", "riocore/generator/toolchains/*", "riocore/interfaces/*"):
    packages.append(folder.replace("/*", "").replace("/", "."))
    for module in glob.glob(folder):
        if "__" not in module and not module.endswith(".py"):
            module_name = module.replace("/", ".")
            packages.append(module_name)
            package_data[module_name] = ["*.c", "*.v"]

setup(
    name="riocore",
    version=VERSION,
    author="Oliver Dippel",
    author_email="o.dippel@gmx.de",
    packages=packages,
    package_data=package_data,
    scripts=scripts,
    url="https://github.com/multigcs/LinuxCNC-RIO/",
    license="LICENSE",
    description="riocore",
    long_description=open("README.md").read(),
    install_requires=[],
    include_package_data=True,
)

