"""Support for Zigbee Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget, LOGNO


# pylint: disable=bare-except
class BusAuditorUartScan(Test):
    """
    Test selected channels for UART communication protocol.

    Output Format:
    [{
        "uart_port":
        [
            {
                "baud": 115200,
                "pins": [
                    {
                        "tx": 9,
                        "rx": 8
                    },
                    #...
                ]
            },
            #...
        ]
    }]
    """

    def __init__(self):
        super().__init__(
            name="uartscan",
            summary="Displays uart scan information",
            descr="This plugin scans and display UART pins of target hardware.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[
                "https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter"
            ],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )

        self.argparser.add_argument(
            "-v",
            "--volts",
            type=str,
            default="3.3",
            help="voltage out. If not specified, volts will be 3.3",
        )

        self.argparser.add_argument(
            "-s",
            "--start",
            type=int,
            default=0,
            help="First pin to start the scan. If "
            "not specified, it will start the scan from pin 0",
        )

        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=1,
            help="Last pin. If "
            "not specified, it will scan until pin 15",
        )

    @staticmethod
    def display_uart_scan_result(result_dict):
        """Displays uart scan result.

        Args:
            result_dict (dict): Dict of UART port scan result
        Returns:
           Nothing
        Raises:
            Nothing
        """

        TLog.success("UART port scan result:")

        uart_port = result_dict["uart_port"]

        for ports in uart_port:
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

            TLog.generic(" ")

    def execute(self):
        """Execute the test."""

        TLog.generic(
            "Start Pin ({}), End Pin ({})".format(
                self.args.start, self.args.end
            )
        )

        TLog.generic(
            "Target Voltage ({})".format(
                self.args.volts
            )
        )

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.uart_scan(self.args.start,
                                     self.args.end,
                                     self.args.volts
                                     )
            if resp:
                found = True
                # self.output_handler(**resp)

                self.output_handler(logkwargs=LOGNO, **resp)
                self.display_uart_scan_result(resp)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.stop()

            if found is False:
                TLog.fail("Couldn't find uart pins")
