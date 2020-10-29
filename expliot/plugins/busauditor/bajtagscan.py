"""Support for Bus Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.busauditor import (
    JTAG_REFERENCE, DEFAFULT_START, DEFAFULT_END,
    DEFAULT_VOLTS, VOLTAGE_RANGE
)


# pylint: disable=bare-except
class BaJtagScan(Test):
    """
    Test selected channels for JTAG communication protocol.

    Output Format:
    # TRST is optional, dependes if it is included by user in jtag scan
    [
        {
            'jtag_id': '0x4ba00477',
            'pins': {
                'trst': 4,      # 'TRST' pin included in jtag scan
                'tck': 0,
                'tms': 1,
                'tdo': 3,
                'tdi': 2
            }
        }, {
            'jtag_id': '0x06431041',
            'pins': {
                'trst': 4,      # 'TRST' pin included in jtag scan
                'tck': 0,
                'tms': 1,
                'tdo': 3,
                'tdi': 2
            }
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="jtagscan",
            summary="JTAG port scan",
            descr="This plugin scans JTAG port for JTAG device id, JTAG pins "
            "(TMS, TCK, TDO, TDI and TRST) on the target hardware. "
            "TRST pin scan is optional and depends upon target HW, if TRST pin "
            "is active on target HW, then it must be include in scan. "
            "You need to connect Bus Auditor channels (pins) to the suspected "
            "pinouts on the target pcb board. "
            "Bus Auditor pins must be connected in a sequential range and "
            "specified by the start and end pin arguments. "
            "If you are seeing permission issues, kindly add a udev rule for "
            "your user for the Bus Auditor device.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[JTAG_REFERENCE],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-i",
            "--include_trst",
            action="store_true",
            help="Include TRST pin in scan",
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

        count = 1
        for _ in range(self.args.start, self.args.end):
            count += 1

        if self.args.include_trst:
            if count < 5:
                self.result.setstatus(
                    passed=False,
                    reason="Minimum 5 pins required for jtag scan."
                )
                return
        else:
            if count < 4:
                self.result.setstatus(
                    passed=False,
                    reason="Minimum 4 pins required for jtag scan."
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

        if self.args.include_trst:
            TLog.generic("TRST pin included in scan")
        else:
            TLog.generic("TRST pin excluded from scan")

        TLog.generic("")

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.jtag_scan(
                self.args.start,
                self.args.end,
                self.args.volts,
                self.args.include_trst
            )
            if resp:
                found = True
                TLog.success("JTAG Devices:")
                for dev in resp:
                    self.output_handler(**dev)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.close()

            if found is False:
                TLog.fail("Couldn't find jtag pins")
