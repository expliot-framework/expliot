"""Support for Zigbee Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget, LOGNO


# pylint: disable=bare-except
class BusAuditorJtagIdCodeScan(Test):
    """
    Test selected channels for JTAG communication protocol.

    Output Format:
    [{
        "devices":
        [
            {
                "jtag_id": "0x4ba00477",
                "pins": {
                    "trst": 4,
                    "tck": 0,
                    "tms": 1,
                    "tdo": 3,
                    "tdi": 2
                }
            }, {
                "jtag_id": "0x06431041",
                "pins": {
                    "trst": 4,
                    "tck": 0,
                    "tms": 1,
                    "tdo": 3,
                    "tdi": 2
                }
            }
            #...
        ]
    }]
    """

    def __init__(self):
        super().__init__(
            name="jtagscan",
            summary="Displays jtag scan information",
            descr="This plugin scans and display jtag pins of target hardware.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=["https://en.wikipedia.org/wiki/JTAG"],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
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
            default=0,
            help="First pin to start the scan. If "
            "not specified, it will start the scan from pin 0",
        )

        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=15,
            help="Last pin. If "
            "not specified, it will scan until pin 15",
        )

        self.argparser.add_argument(
            "-v",
            "--volts",
            type=str,
            default="3.3",
            help="voltage out. If not specified, volts will be 3.3",
        )

    @staticmethod
    def display_jtag_scan_result(result_dict):
        """
        Displays JTAG idcode scan result.

        Args:
            result_dict (dict): Dict of JTAG idcode scan information
        Returns:
           Nothing
        Raises:
            Nothing
        """

        TLog.success("JTAG port scan result:")

        count = 1
        devices = result_dict["devices"]
        for dev in devices:
            TLog.success("Device: {}".format(count))

            TLog.success("\t{:<8}: {}".format("ID Code", dev["jtag_id"]))

            pins = dev["pins"]
            TLog.success("\t{:<8}: {}".format("TCK", pins["tck"]))
            TLog.success("\t{:<8}: {}".format("TMS", pins["tms"]))
            TLog.success("\t{:<8}: {}".format("TDO", pins["tdo"]))
            TLog.success("\t{:<8}: {}".format("TDI", pins["tdi"]))

            if "trst" in pins:
                TLog.generic("\t{:<8}: {}".format("TRST", pins["trst"]))
            count = count + 1

            TLog.generic(" ")

    def execute(self):
        """Execute the test."""

        TLog.generic("Start Pin ({}), End Pin ({})".format(self.args.start, self.args.end))
        TLog.generic("Target Voltage ({})".format(self.args.volts))

        if self.args.include_trst:
            TLog.generic("TRST pin included in scan")
        else:
            TLog.generic("TRST pin excluded from scan")

        TLog.generic(" ")

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.jtag_scan(self.args.start,
                                     self.args.end,
                                     self.args.volts,
                                     self.args.include_trst
                                     )
            if resp:
                found = True
                # self.output_handler(**resp)

                self.output_handler(logkwargs=LOGNO, **resp)
                self.display_jtag_scan_result(resp)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.stop()

            if found is False:
                TLog.fail("Couldn't find jtag pins")
