"""Support for detecting the baud rate of a device."""
import string

from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.hardware.serial import Serial
from expliot.core.tests.test import TCategory, Test, TLog, \
    TTarget, LOGNO
from expliot.plugins.serial import (
    DEV_PORT,
    DEFAULT_BYTES,
    READ_TIMEOUT,
)


# pylint: disable=bare-except
class BaudScan(Test):
    """
    Test the available baud rate of a device.

    Output Format:
    [
        {
            "baud": 9600,
            "ascii_percent": 70.0,
            "received_data": "\xf00bar\x01",
            "ascii_data": "0bar",
            "status": "Data received", # or "No data received" if nothing is received
            "exception": None, # or "Error message" in case an exception occurred during
                               # serial communication, in which case the other information
                               # may be empty or incomplete
        },
        # ... More than one entry based on no. of baud rates scanned.

    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="baudscan",
            summary="Baud rate scanner for serial connection",
            descr="This test helps in identifying the correct baud rate of the "
            "serial connection to a UART port on the hardware. It enumerates "
            "over a list of baud rates and analyzes the date read over a serial "
            "connection for ascii to identify the correct baud  rate. You need "
            "to connect the UART port of the device using a USBTTL connector "
            "(Expliot Nano supports UART too) to your machine running expliot. "
            "This test is inspired by devttys0's baudrate.py and the percent idea "
            "taken from IoTSecFuzz tool. Thank you devttys0 and IoTSecFuzz Team!",
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
            help="A comma separated list of baud rates that you want to scan. If "
            "not specified, it will scan for default baud rates (1200, 2400, "
            "4800, 9600, 19200, 38400, 57600 and 115200).",
        )
        self.argparser.add_argument(
            "-p",
            "--port",
            default=DEV_PORT,
            help="The device port on the system. Default is {}".format(DEV_PORT),
        )
        self.argparser.add_argument(
            "-c",
            "--count",
            type=int,
            default=DEFAULT_BYTES,
            help="Total count of bytes to read per baud rate. Default is {}".format(
                DEFAULT_BYTES
            ),
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            type=float,
            default=READ_TIMEOUT,
            help="Read timeout, in secs, for each baud rate test. Default is {}".format(
                READ_TIMEOUT
            ),
        )
        self.argparser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Show verbose output i.e. data read from the device",
        )

    def check_baud(self, baud):
        """
        Scan a serial connection for ASCII data with a given baud rate.

        :param baud: The baud rate to use for the serial connection
        :return: Percentage of ASCII characters present in the received data
        """
        sock = None
        output = {"baud": baud,
                  "ascii_percent": -1,
                  "received_data": None,
                  "ascii_data": None,
                  "status": None,
                  "exception": None}
        TLog.trydo("Checking baud rate: {}".format(baud))
        try:
            sock = Serial(self.args.port, baud, timeout=self.args.timeout)
            output["received_data"] = sock.read(self.args.count)
            sock.flush()
            output["ascii_data"] = "".join(
                [chr(entry) for entry in output["received_data"] if chr(entry) in string.printable]
            )
            received_length = len(output["received_data"])
            ascii_length = len(output["ascii_data"])
            if received_length == 0:
                output["status"] = "No data received"
                TLog.fail("\t{}".format(output["status"]))
            else:
                output["status"] = "Data received"
                output["ascii_percent"] = round(ascii_length / received_length * 100, 2)
                if self.args.verbose:
                    TLog.success("\tdata: {}, ASCII: {}".format(
                        output["received_data"],
                        output["ascii_data"])
                    )
                TLog.success(
                    "\tASCII ratio: {}/{}, {} %".format(
                        ascii_length, received_length, output["ascii_percent"]
                    )
                )
        except:  # noqa: E722
            output["exception"] = sysexcinfo()
            TLog.fail("\tError: {}".format(output["exception"]))
        finally:
            if sock:
                sock.close()
            self.output_handler(logkwargs=LOGNO, **output)
        return output["ascii_percent"]

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Connecting to the the serial port ({}) timeout ({})".format(
                self.args.port, self.args.timeout
            )
        )
        TLog.generic("Scanning for baud rates: {}".format(self.args.bauds))
        reason = "No good baud rate found"
        best = {"baud_rate": 0, "percentage_ascii": 0}
        try:
            for baud in self.args.bauds.split(","):
                percentage_ascii = self.check_baud(int(baud))
                if percentage_ascii == 100:
                    TLog.success("Found correct baud rate: {}".format(baud))
                    return
                if percentage_ascii > best["percentage_ascii"]:
                    best["percentage_ascii"] = percentage_ascii
                    best["baud_rate"] = int(baud)
            if best["percentage_ascii"] > 90:
                TLog.success(
                    "Found good baud rate {} with {}% ASCII data".format(
                        best["baud_rate"], best["percentage_ascii"]
                    )
                )
                return

            TLog.generic(
                "Baud rate {} has max. ASCII percentage of {} %".format(
                    best["baud_rate"], best["percentage_ascii"]
                )
            )
        except:  # noqa: E722
            reason = "Exception caught: {}".format(sysexcinfo())
        self.result.setstatus(passed=False, reason=reason)
