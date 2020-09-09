#!/usr/bin/env python3
"""Setup script for EXPLIoT."""
import os

from setuptools import find_packages, setup

import expliot.constants as expliot_const

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="expliot",
    version=expliot_const.__version__,
    url="https://expliot.io",
    license="AGPLv3+",
    author="Aseem Jakhar",
    author_email="aseemjakhar@gmail.com",
    description="Expliot - IoT security testing and exploitation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={"console_scripts": ["expliot=expliot.expliot:EfCli.main"]},
    install_requires=[
        "AWSIoTPythonSDK>=1.4.8,<2",
        "bluepy>=1.3.0,<2",
        "cmd2>=1.1.0,<2",
        "coapthon3>=1.0.1,<2",
        "cryptography>=3.0,<4",
        "paho-mqtt>=1.5.0,<2",
        "pyi2cflash>=0.2.2,<1",
        "pymodbus>=2.3.0,<3",
        "pynetdicom>=1.5.1,<2",
        "pyparsing>=2.4.7,<3",
        "pyserial>=3.4,<4",
        "pyspiflash>=0.6.3,<1",
        "python-can>=3.3.3,<4",
        "xmltodict>=0.12.0,<1",
        "zeroconf>=0.27.1,<1",
    ],
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Security",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Testing",
    ],
    keywords="IoT IIot security hacking expliot exploit framework",
)
