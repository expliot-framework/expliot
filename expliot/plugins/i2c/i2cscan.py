"""Support for scanning the I2C bus."""
from logging import ERROR, getLogger

from pyftdi.i2c import I2cController, I2cNackError

from expliot.core.tests.test import TCategory, Test, TLog, TTarget


# pylint: disable=bare-except
class I2cScan(Test):
    """Scan the I2C bus for connected units."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="scan",
            summary="I2C Scanner",
            descr="""This plugin scans the I2C bus and displays all the address connected to the bus.""",
            author="Arun Magesh",
            email="arun.m@payatu.com",
            ref=["https://github.com/eblot/pyftdi"],
            category=TCategory(TCategory.I2C, TCategory.HW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-u",
            "--url",
            default="ftdi:///1",
            help="""URL of the connected FTDI device. Default is ftdi:///1.
            For more details on the URL scheme check https://eblot.github.io/pyftdi/urlscheme.html""",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic("Scanning for I2C devices...")
        passed = 0
        fail = 0
        try:
            i2c = I2cController()
            getLogger("pyftdi.i2c").setLevel(ERROR)
            try:
                i2c.set_retry_count(1)
                i2c.configure(self.args.url)
                for address in range(i2c.HIGHEST_I2C_ADDRESS + 1):
                    port = i2c.get_port(address)
                    try:
                        port.read(0)
                        TLog.success("Address found: {} ".format(hex(address)))
                        passed = passed + 1
                    except I2cNackError:
                        fail = fail + 1
            finally:
                i2c.terminate()
            TLog.success(
                "Done. Found {} and not found {}".format(str(passed), str(fail))
            )
        except:  # noqa: E722
            self.result.exception()
