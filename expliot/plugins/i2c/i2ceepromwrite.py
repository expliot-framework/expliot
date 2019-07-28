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

from time import time
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.protocols.hardware.i2c import I2cEepromManager


class I2cEepromWrite(Test):
    def __init__(self):
        super().__init__(
            name="writeeeprom",
            summary="I2C EEPROM Writer",
            descr="""This plugin writes data to an I2C EEPROM chip. It needs an FTDI interface to
                                       write data to the target EEPROM chip. You can buy an FTDI device online. If you
                                       are interested we have an FTDI based product - 'Expliot Nano' which you can
                                       order online from www.expliot.io This plugin uses pyi2cflash package which in
                                       turn uses pyftdi python driver for ftdi chips. For more details on supported
                                       I2C EEPROM chips, check the readme at https://github.com/eblot/pyi2cflash Thank
                                       you Emmanuel Blot for pyi2cflash. You may want to run it as root in case you
                                       get a USB error related to langid""",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://github.com/eblot/pyspiflash"],
            category=TCategory(TCategory.I2C, TCategory.HW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--addr",
            default=0,
            type=int,
            help="""Specify the start address where data is to be written. Default is 0""",
        )
        self.argparser.add_argument(
            "-u",
            "--url",
            default="ftdi:///1",
            help="""URL of the connected FTDI device. Default is "ftdi:///1". For more details
                                            on the URL scheme check https://eblot.github.io/pyftdi/urlscheme.html""",
        )
        self.argparser.add_argument(
            "-c",
            "--chip",
            required=True,
            help="""Specify the chip. Supported chips are 24AA32A, 24AA64, 24AA128, 24AA256,
                                            24AA512""",
        )
        self.argparser.add_argument(
            "-d",
            "--data",
            help="Specify the data to write, as hex stream, without the 0x prefix",
        )
        self.argparser.add_argument(
            "-r",
            "--rfile",
            help="""Specify the file path from where data is to be read. This
                                                             takes precedence over --data option i.e if both options
                                                             are specified --data would be ignored""",
        )
        self.slaveaddr = 0x50

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Writing data to i2c eeprom at address({}) using device({})".format(
                self.args.addr, self.args.url
            )
        )
        d = None
        f = None
        try:
            stime = None
            etime = None
            data = None
            saddr = self.args.addr
            if self.args.rfile:
                TLog.trydo("Reading data from the file ({})".format(self.args.rfile))
                f = open(self.args.rfile, "r+b")
                data = f.read()
                f.close()
            elif self.args.data:
                data = bytes.fromhex(self.args.data)
            else:
                raise AttributeError("Specify either --data or --rfile (but not both)")

            d = I2cEepromManager.get_flash_device(
                self.args.url, self.args.chip, address=self.slaveaddr
            )
            TLog.success("(chip size={} bytes)".format(len(d)))

            ln = len(data)
            TLog.trydo("Writing {} byte(s) at start address {}".format(ln, saddr))
            if self.args.addr + ln > len(d):
                raise IndexError("Length is out of range of the chip size")
            stime = time()
            d.write(saddr, data)
            etime = time()
            TLog.success(
                "wrote {} byte(s) of data from address {}. Time taken {} secs".format(
                    len(data), saddr, round(etime - stime, 2)
                )
            )
        except:  # noqa: E722
            self.result.exception()
        finally:
            I2cEepromManager.close(d)
