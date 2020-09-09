"""Support for writing data to SPI."""
from time import time

from expliot.core.protocols.hardware.spi import SpiFlashManager
from expliot.core.interfaces.ftdi import DEFAULT_FTDI_URL
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.spi import DEFAULT_ADDR


# pylint: disable=bare-except
class SPIFlashWrite(Test):
    """
    Test for writing data to SPI.

    Output Format:
    [
        {
            "chip": "Foobar XY12 8 MB",
            "size": 8388608, # in bytes
            "frequency": 30000000 # in Hz
        },
        {
            "bytes_backedup_page_aligned": 32768,
            "from_address": 0,
            "time_taken_secs": 0.03
        },
        {
            "bytes_erased": 32768,
            "from_address": 0,
            "time_taken_secs": 0.03
        },
        {
            "bytes_written": 32768,
            "from_address": 0,
            "time_taken_secs": 0.03
        };
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="writeflash",
            summary="SPI Flash Writer",
            descr="This plugin writes data to a serial flash chip that "
                  "implements SPI protocol. It needs an FTDI interface to "
                  "write data to the target flash chip. You can buy  an FTDI "
                  "device online. If you are interested we have an FTDI based "
                  "product -  'Expliot Nano' which you can order online from "
                  "www.expliot.io. This plugin uses pyspiflash package which "
                  "in turn uses pyftdi python driver for FTDI chips. For more "
                  "details on supported flash chips, check the readme at  "
                  "https://github.com/eblot/pyspiflash. Thank you Emmanuel "
                  "Blot for pyspiflash. You may want to run it as root in "
                  "case you get a USB error related to langid.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://github.com/eblot/pyspiflash"],
            category=TCategory(TCategory.SPI, TCategory.HW, TCategory.ANALYSIS),
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
            "-f",
            "--freq",
            type=int,
            help="Specify a frequency in Hz(example: 1000000 for 1 MHz). "
                 "If not, specified, default frequency of the device is "
                 "used. You may want to decrease the  frequency if you "
                 "keep seeing FtdiError:UsbError.",
        )
        self.argparser.add_argument(
            "-d",
            "--data",
            help="Specify the data to write, as hex stream, without "
                 "the 0x prefix",
        )

        self.argparser.add_argument(
            "-r",
            "--rfile",
            help="Specify the file path from where data is to be read. "
                 "This takes precedence over --data option i.e if both "
                 "options are specified --data would be ignored",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Writing data to SPI flash at address({}) using device ({})".format(
                self.args.addr, self.args.url
            )
        )
        device = None
        try:
            start_address = self.args.addr
            if self.args.rfile:
                TLog.trydo("Reading data from the file ({})".format(self.args.rfile))
                local_file = open(self.args.rfile, "r+b")
                data = local_file.read()
                local_file.close()
            elif self.args.data:
                data = bytes.fromhex(self.args.data)
            else:
                raise AttributeError("Specify either --data or --rfile (but not both)")

            device = SpiFlashManager.get_flash_device(
                self.args.url, freq=self.args.freq
            )
            self.output_handler(chip=device, size=len(device),
                                frequency=int(device.spi_frequency))
            data_length = len(data)
            end_address = start_address + data_length - 1
            TLog.trydo(
                "Writing {} byte(s) at start address {}".format(
                    data_length, start_address
                )
            )
            if self.args.addr + data_length > len(device):
                raise IndexError("Length is out of range of the chip size")
            # We can't write on any arbitrary address for an arbitrary length
            # unless it is aligned to the page size
            # Get erase page size, start/end enclosing page addresses and length
            esz = device.get_erase_size()
            spaddr = start_address - start_address % esz
            epaddr = end_address + esz - (end_address % esz) - 1
            pln = epaddr - spaddr + 1
            TLog.trydo(
                "Page aligned start address({}) end address({}) length({})".format(
                    spaddr, epaddr, pln
                )
            )
            # Backup the data from chip
            start_time = time()
            tmpdata = device.read(spaddr, pln)
            end_time = time()
            self.output_handler(bytes_backedup_page_aligned=pln, from_address=spaddr,
                                time_taken_secs=round(end_time - start_time, 2))

            # commenting below line as pyspiflash 0.6.3 read() returns bytes instead
            # of ByteArray (array) sept 2020
            # tmpdata = tmpdata.tobytes()
            # We can only write on erased data
            # Now erase the enclosing pages (of the start and end addresses)
            device.unlock()
            start_time = time()
            device.erase(spaddr, pln)
            end_time = time()
            self.output_handler(bytes_erased=pln, from_address=spaddr,
                                time_taken_secs=round(end_time - start_time, 2))
            # Now overwrite with the updated data i.e. backed up data containing the changes
            wdata = (
                tmpdata[0 : start_address % esz]
                + data
                + tmpdata[start_address % esz + data_length :]
            )
            start_time = time()
            device.write(spaddr, wdata)
            end_time = time()
            self.output_handler(bytes_written=pln, from_address=spaddr,
                                time_taken_secs=round(end_time - start_time, 2))
        except:  # noqa: E722
            self.result.exception()
        finally:
            SpiFlashManager.close(device)
