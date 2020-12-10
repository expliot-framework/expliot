"""Support for Bus Auditor Device Information."""
from math import factorial
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget, LOGNO
from expliot.plugins.busauditor import (
    UART_REFERENCE, DEFAFULT_START, DEFAFULT_END,
    DEFAULT_VOLTS, VOLTAGE_RANGE, CHANNEL_MIN, CHANNEL_MAX
)


# pylint: disable=bare-except
class BaUartScan(Test):
    """
    Test selected channels for UART communication protocol.

    Output Format:
    [
        {
            "baud": 115200,
            "pins": [
                        {
                            "tx": 6,
                            "rx": 5
                        },
                        # ... more than one possible pin combinations
                    ]
        },
        # ... May be zero or more entries.
        # If zero UART port found the above dict will not be present
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="uartscan",
            summary="UART port scan",
            descr="This plugin scans UART port, UART pins (Tx, Rx) and "
            " Baudrate on the target hardware. You need to connect Bus "
            "Auditor channels (pins) to the suspected pinouts on the target "
            "pcb board. Bus Auditor pins must be connected in a sequential "
            "range and specified by the start and end pin arguments. "
            "When Rx pin is not active on target, and more than two pins are "
            "selected for scan, this will give you possible Rx and Tx pins "
            "combinations. If you are seeing permission issues, kindly add a "
            "udev rule for your user for the Bus Auditor device.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[UART_REFERENCE],
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

    @staticmethod
    def display_uart_scan_result(result_list):
        """Displays uart scan result.

        Args:
            result_dict (dict): Dict of UART port scan result
        Returns:
           Nothing
        Raises:
            Nothing
        """

        TLog.success("UART port scan result:")

        for ports in result_list:
            TLog.success(
                "{:<8}: {}".format(
                    "BaudRate", ports["baud"]
                )
            )

            pins = ports["pins"]

            TLog.success("UART pins:")
            if len(pins) == 1:
                TLog.success(
                    "\tTx pin: {}, Rx pin: {}".format(
                        pins[0]["tx"], pins[0]["rx"]
                    )
                )
            else:
                TLog.success("\tPossible pin combinations:")

                for index, pin in enumerate(pins):
                    TLog.success(
                        "\t{}. Tx pin: {}, Rx pin: {}".format(
                            index + 1, pin["tx"], pin["rx"]
                        )
                    )

            TLog.generic("")

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

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.uart_scan(
                self.args.start,
                self.args.end,
                self.args.volts
            )
            if resp:
                found = True
                for dev in resp:
                    self.output_handler(logkwargs=LOGNO, **dev)

                self.display_uart_scan_result(resp)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.close()

            if found is False:
                TLog.fail("Couldn't find uart pins")
