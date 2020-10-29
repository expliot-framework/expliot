"""Support for Bus Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.busauditor import (
    I2C_REFERENCE, DEFAFULT_START, DEFAFULT_END,
    DEFAULT_VOLTS, VOLTAGE_RANGE
)


# pylint: disable=bare-except
class BaI2cScan(Test):
    """
    Test selected channels for I2C communication protocol.

    Output Format:
    [
        {
        'i2c_addr': '0x48',
        'pins': {
            'scl': 8,
            'sda': 9
        }
        }, {
            'i2c_addr': '0x50',
            'pins': {
                'scl': 8,
                'sda': 9
            }
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="i2cscan",
            summary="I2C bus scan",
            descr="This plugin scans i2c devices and i2c pins (SCL, SDA) on "
            "the target hardware. You need to connect Bus Auditor channels "
            "(pins) to the suspected pinouts on the target pcb board. "
            "Bus Auditor pins must be connected in a sequential range and "
            "specified by the start and end pin arguments."
            "If you are seeing permission issues, kindly add a udev rule for "
            "your user for the Bus Auditor device.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[I2C_REFERENCE],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )

        self.argparser.add_argument(
            "-s",
            "--start",
            type=int,
            default=DEFAFULT_START,
            help="First Bus Auditor channel for the scan. If not specified, "
            "it will start the scan from channel '{}'".format(DEFAFULT_START),
        )

        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=DEFAFULT_END,
            help="Last Bus Auditor channel for the scan. If not specified, "
            "it will scan until channel '{}'".format(DEFAFULT_END),
        )

        self.argparser.add_argument(
            "-v",
            "--volts",
            type=str,
            default=DEFAULT_VOLTS,
            help="Target voltage out. "
            "Supported target volts are '{}', '{}', and '{}' If not specified, "
            "target voltage will be '{}' volts".format(
                VOLTAGE_RANGE[0],
                VOLTAGE_RANGE[1],
                VOLTAGE_RANGE[2],
                DEFAULT_VOLTS
            ),
        )

    def execute(self):
        """Execute the test."""

        # Start channel cannot be less than zero or greater than 15
        if self.args.start < DEFAFULT_START or self.args.start > DEFAFULT_END:
            self.result.setstatus(
                passed=False,
                reason="Invalid start channel."
            )
            return

        # End channel cannot be less than zero or greater than 15
        if self.args.end < DEFAFULT_START or self.args.end > DEFAFULT_END:
            self.result.setstatus(
                passed=False,
                reason="Invalid end channel."
            )
            return

        # Start and End channel cannot be same
        if self.args.start == self.args.end:
            self.result.setstatus(
                passed=False,
                reason="Same start and end channel."
            )
            return

        # Start > End channel
        if self.args.start > self.args.end:
            self.result.setstatus(
                passed=False,
                reason="Start channel greater than end channel."
            )
            return

        if self.args.volts not in VOLTAGE_RANGE:
            self.result.setstatus(
                passed=False,
                reason="Unsupported target voltage."
            )
            return

        TLog.generic(
            "Start Pin '{}', End Pin '{}'".format(
                self.args.start, self.args.end
            )
        )
        TLog.generic("Target Voltage '{}'".format(self.args.volts))
        TLog.generic("")

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.i2c_scan(
                self.args.start,
                self.args.end,
                self.args.volts
            )
            if resp:
                found = True
                TLog.success("I2C Devices:")
                for dev in resp:
                    self.output_handler(**dev)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.close()

            if found is False:
                TLog.fail("Couldn't find i2c pins")
