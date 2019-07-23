#
#
# expliot - Internet Of Things Security Testing and Exploitation Framework
# 
# Copyright (C) 2018  Aseem Jakhar
#
# Email:   aseemjakhar@gmail.com
# Twitter: @aseemjakhar
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import os
from setuptools import setup, find_packages

from expliot import Expliot

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="expliot",
    version=Expliot.version(),
    url="https://expliot.io",
    license="AGPLv3+",
    author="Aseem Jakhar",
    author_email="aseemjakhar@gmail.com",
    description="Expliot - IoT security testing and exploitation framework",
    long_description=long_description,
    packages=find_packages(),
    scripts=["bin/expliot"],
    install_requires=["cmd2>=0.9.13", "paho-mqtt>=1.3.1", "coapthon3>=1.0.1", "bluepy>=1.1.4", "pyserial>=3.4",
                      "pyparsing>=2.2.0", "pycrypto>=2.6.1", "pymodbus>=1.5.2", "python-can>=2.1.0",
                      "pyspiflash>=0.5.2", "pyi2cflash>=0.1.1", "pynetdicom>=1.2.0"],
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English"
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Security",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Testing",
    ],
    keywords="IoT IIot security hacking expliot exploit framework",
)
