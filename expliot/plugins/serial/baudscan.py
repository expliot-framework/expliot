"""Support for detecting the baud rate of a device."""
import string

from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.hardware.serial import Serial
from expliot.core.tests.test import TCategory, Test, TLog, TTarget


class BaudScan(Test):
    """Test the available baud rate of a device."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="baudscan",
            summary="Baud rate scanner for serial connection",
            descr="This test helps in identifying the correct baud rate of the serial connection to a UART port on the hardware. It enumerates over a list of baud rates and analyzes the date read over a serial connection for ascii to identify the correct baud  rate. You need to connect the UART port of the device using a USBTTL connector (Expliot Nano supports UART too) to your machine running expliot. This test is inspired by devttys0's baudrate.py and the percent idea taken from IoTSecFuzz tool. Thank you devttys0 and IoTSecFuzz Team!",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[
                "https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter"
            ],
            category=TCategory(TCategory.UART, TCategory.HW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-b",
            "--bauds",
            default="1200,2400,4800,9600,19200,38400,57600,115200",
            help="A comma separated list of baud rates that you want to scan. If not specified, it will scan for default baud rates (1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200).",
        )
        self.argparser.add_argument(
            "-p",
            "--port",
            default="/dev/ttyUSB0",
            required=True,
            help="The device port on the system. Default is /dev/ttyUSB0",
        )
        self.argparser.add_argument(
            "-c",
            "--count",
            type=int,
            default=30,
            help="Total count of bytes to read per baud rate. Default is 30",
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            type=float,
            default=3,
            help="Read timeout, in secs, for each baud rate test. Default is 3",
        )
        self.argparser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Show verbose output i.e. data read from the device",
        )

    def check_baud(self, baud):
        """
        Scan a serial connection for ascii data with a given baud rate.

        :param baud: The baud rate to use for the serial connection
        :return: Percentage of ascii characters present in the received data
        """
        sock = None
        pc = -1
        TLog.success("(baud={})".format(baud))
        try:
            sock = Serial(self.args.port, baud, timeout=self.args.timeout)
            rcv = sock.read(self.args.count)
            sock.flush()
            asci = "".join([chr(c) for c in rcv if chr(c) in string.printable])
            rlen = len(rcv)
            alen = len(asci)
            if rlen == 0:
                TLog.fail("  No data received")
            else:
                pc = alen / rlen * 100
                if self.args.verbose:
                    TLog.success("  (data={})(ascii={})".format(rcv, asci))
                TLog.success("  (ascii ratio={}/{} {}%)".format(alen, rlen, pc))
        except:  # noqa: E722
            TLog.fail("  (error={})".format(sysexcinfo()))
        finally:
            if sock:
                sock.close()
        return pc

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Connecting to the the serial port ({}) timeout ({})".format(
                self.args.port, self.args.timeout
            )
        )
        TLog.generic("Scanning for baud rates: {}".format(self.args.bauds))
        rsn = "No good baud rate found"
        best = {"b": 0, "pc": 0}
        try:
            for b in self.args.bauds.split(","):
                pc = self.check_baud(int(b))
                if pc == 100:
                    TLog.success("Found correct baud rate - {}".format(b))
                    return
                if pc > best["pc"]:
                    best["pc"] = pc
                    best["b"] = int(b)
            if best["pc"] > 90:
                TLog.success(
                    "Found good baud rate - {} with {}% ascii data".format(
                        best["b"], best["pc"]
                    )
                )
                return
            else:
                TLog.generic(
                    "Baud rate - {} has max ascii percentage - {}%".format(
                        best["b"], best["pc"]
                    )
                )
        except:  # noqa: E722
            rsn = "Exception caught: {}".format(sysexcinfo())
        self.result.setstatus(passed=False, reason=rsn)
