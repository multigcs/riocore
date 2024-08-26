#!/usr/bin/env python3


import glob
import os

from setuptools import setup, find_packages

from riocore.VERSION import VERSION

package_data = {
    "riocore": [
        "files/*",
        "boards/*",
        "boards/*/*",
        "modules/*",
        "configs/*/*",
    ],
}
#packages = ["riocore"]

for folder in ("riocore/plugins/*", "riocore/generator/*", "riocore/generator/pins/*", "riocore/generator/toolchains/*", "riocore/interfaces/*"):
    #packages.append(folder.replace("/*", "").replace("/", "."))
    for module in glob.glob(folder):
        if "__" not in module and not module.endswith(".py"):
            module_name = module.replace("/", ".")
            #packages.append(module_name)
            package_data[module_name] = ["*.c", "*.v", "*.png", "*.md"]

setup(
    name="riocore",
    version=VERSION,
    author="Oliver Dippel",
    author_email="o.dippel@gmx.de",
    packages=find_packages(),
    package_data=package_data,
    url="https://github.com/multigcs/riocore/",
    license="LICENSE",
    description="riocore",
    long_description=open("README.md").read(),
    entry_points={
        'gui_scripts': [
            'rio-setup=riocore.apps.rio_setup:main',
            'rio-test=riocore.apps.rio_test:main',
        ],
        'console_scripts': [
            'rio-generator=riocore.apps.rio_generator:main',
            'rio-plugininfo=riocore.apps.rio_plugininfo:main',
        ],
    },
    install_requires=["PyQt5>=5.15", "graphviz>=0.20", "pyqtgraph>=0.13.3"],
    include_package_data=True,
)
