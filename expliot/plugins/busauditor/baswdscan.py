"""Support for Bus Auditor Device Information."""
from math import factorial
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.busauditor import (
    SWD_REFERENCE, DEFAFULT_START, DEFAFULT_END,
    DEFAULT_VOLTS, VOLTAGE_RANGE, CHANNEL_MIN, CHANNEL_MAX
)


# pylint: disable=bare-except
class BaSwdScan(Test):
    """
    Test selected channels for SWD communication protocol.

    Output Format:
    [
        {
            "swd_idcode": "0x2ba01477",
            "pins": {
                        "swclk": 0,
                        "swdio": 1
                    }
        },
        # ... May be zero or more entries.
        # If zero SWD devices found the above dict will not be present
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="swdscan",
            summary="SWD port scan",
            descr="This plugin scans SWD port and SWD pins (SW_CLK, SW_DIO) "
            "on the target hardware. You need to connect Bus Auditor channels "
            "(pins) to the suspected pinouts on the target pcb board. "
            "Bus Auditor pins must be connected in a sequential range and "
            "specified by the start and end pin arguments."
            "If you are seeing permission issues, kindly add a udev rule for "
            "your user for the Bus Auditor device.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[SWD_REFERENCE],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-s",
            "--start",
            type=int,
            default=DEFAFULT_START,
            help="First Bus Auditor channel for the scan. If not specified, "
            "it will start the scan from channel ({})".format(DEFAFULT_START),
        )

        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=DEFAFULT_END,
            help="Last Bus Auditor channel for the scan. If not specified, "
            "it will scan until channel ({})".format(DEFAFULT_END),
        )

        self.argparser.add_argument(
            "-v",
            "--volts",
            type=str,
            default=DEFAULT_VOLTS,
            help="Target voltage out. "
            "Supported target volts are ({}), ({}), and ({}) If not specified, "
            "target voltage will be ({}) volts".format(
                VOLTAGE_RANGE[0],
                VOLTAGE_RANGE[1],
                VOLTAGE_RANGE[2],
                DEFAULT_VOLTS
            ),
        )

    def execute(self):
        """Execute the test."""

        # Start channel cannot be less than zero or greater than 15
        if self.args.start < CHANNEL_MIN or self.args.start > CHANNEL_MAX:
            self.result.setstatus(
                passed=False,
                reason="Invalid start channel."
            )
            return

        # End channel cannot be less than zero or greater than 15
        if self.args.end < CHANNEL_MIN or self.args.end > CHANNEL_MAX:
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
            "Start Pin ({}), End Pin ({})".format(
                self.args.start, self.args.end
            )
        )
        TLog.generic("Target Voltage ({})".format(self.args.volts))

        # compute possible permutations
        ch_count = len(range(self.args.start, self.args.end + 1))
        possible_permutations = int(
            factorial(ch_count) / factorial(ch_count - 2)
        )

        TLog.generic(
            "Possible permutations to be tested: ({})".format(
                possible_permutations
            )
        )

        TLog.generic("")

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.swd_scan(
                self.args.start,
                self.args.end,
                self.args.volts
            )
            if resp:
                found = True
                TLog.success("SWD Devices:")
                for dev in resp:
                    self.output_handler(**dev)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.close()

            if found is False:
                TLog.fail("Couldn't find swd pins")
