"""Support for writing data over i2c."""
from time import time

from expliot.core.protocols.hardware.i2c import I2cEepromManager
from expliot.core.interfaces.ftdi import DEFAULT_FTDI_URL
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.i2c import DEFAULT_ADDR, SLAVE_ADDR


# pylint: disable=bare-except
class I2cEepromWrite(Test):
    """
    Write test for data to i2c.

    Output Format:

    [
        {
            chip_size=32768, # Size of the chip in bytes
        },
        {
            "bytes_written": 1000,
            "time_taken_secs": 1.67
        }
    ]

    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="writeeeprom",
            summary="I2C EEPROM Writer",
            descr="This plugin writes data to an I2C EEPROM chip. It needs an "
            "FTDI interface to write data to the target EEPROM chip. You "
            "can buy an FTDI device online. If you are interested we have "
            "an FTDI based product - 'EXPLIoT Nano' which you can order online "
            "from www.expliot.io This plugin uses pyi2cflash package which in "
            "turn uses pyftdi python driver for ftdi chips. For more details "
            "on supported I2C EEPROM chips, check the readme at "
            "https://github.com/eblot/pyi2cflash Thank you Emmanuel Blot for "
            "pyi2cflash. You may want to run it as root in case you  get a USB "
            "error related to langid.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://github.com/eblot/pyspiflash"],
            category=TCategory(TCategory.I2C, TCategory.HW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--addr",
            default=DEFAULT_ADDR,
            type=int,
            help="Specify the start address where data is to be written. "
                 "Default is {}".format(DEFAULT_ADDR),
        )
        self.argparser.add_argument(
            "-u",
            "--url",
            default=DEFAULT_FTDI_URL,
            help="URL of the connected FTDI device. Default is {}. "
            "For more details on the URL scheme check "
            "https://eblot.github.io/pyftdi/urlscheme.html".format(DEFAULT_FTDI_URL),
        )
        self.argparser.add_argument(
            "-c",
            "--chip",
            required=True,
            help="Specify the chip. Supported chips are 24AA32A, 24AA64, 24AA128, "
            "24AA256, 24AA512",
        )
        self.argparser.add_argument(
            "-d",
            "--data",
            help="Specify the data to write, as hex stream, without the 0x prefix",
        )
        self.argparser.add_argument(
            "-r",
            "--rfile",
            help="Specify the file path from where data is to be read. This takes "
            "precedence over --data option i.e if both options are specified "
            "--data would be ignored",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Writing data to i2c eeprom at address({}) using device({})".format(
                self.args.addr, self.args.url
            )
        )
        device = None
        try:
            start_address = self.args.addr
            if self.args.rfile:
                TLog.trydo("Reading data from the file ({})".format(self.args.rfile))
                input_file = open(self.args.rfile, "r+b")
                data = input_file.read()
                input_file.close()
            elif self.args.data:
                data = bytes.fromhex(self.args.data)
            else:
                raise AttributeError("Specify either --data or --rfile (but not both)")

            device = I2cEepromManager.get_flash_device(
                self.args.url, self.args.chip, address=SLAVE_ADDR
            )
            self.output_handler(chip_size=len(device))

            length_data = len(data)
            TLog.trydo(
                "Writing {} byte(s) at start address {}".format(
                    length_data, start_address
                )
            )
            if self.args.addr + length_data > len(device):
                raise IndexError("Length is out of range of the chip size")
            start_time = time()
            device.write(start_address, data)
            end_time = time()
            self.output_handler(bytes_written=length_data,
                                time_taken_secs=round(end_time - start_time, 2))
        except:  # noqa: E722
            self.result.exception()
        finally:
            I2cEepromManager.close(device)
