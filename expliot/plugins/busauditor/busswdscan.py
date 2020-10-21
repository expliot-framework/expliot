"""Support for Zigbee Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget, LOGNO


# pylint: disable=bare-except
class BusAuditorSwdScan(Test):
    """
    Test selected channels for SWD communication protocol.

    Output Format:
    [{
        "devices": 
        [
            {
                "swd_id": "0x2ba01477",
                "pins": {
                    "swclk": 0,
                    "swdio": 1
                }
            }
            #...
        ]
    }]
    """

    def __init__(self):
        super().__init__(
            name="swdscan",
            summary="Displays swd scan information",
            descr="This plugin scans and display SWD pins of target hardware.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=["https://en.wikipedia.org/wiki/JTAG#Serial_Wire_Debug"],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
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
            default=4,
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
    def display_swd_scan_result(result_dict):
        """
        Displays SWD idcode scan result.
        
        Args:
            result_dict (dict): Dict of SWD idcode scan information
        Returns:
           Nothing
        Raises:
            Nothing
        """

        TLog.success("SWD port scan result:")
        
        count = 1
        devices = result_dict["devices"]
        for dev in devices:
            TLog.success("Device: {}".format(count))
            TLog.success("\t{:<8}: {}".format("ID code", dev["swd_id"]))

            pins = dev["pins"]
            TLog.success("\t{:<8}: {}".format("SW CLK", pins["swclk"]))
            TLog.success("\t{:<8}: {}".format("SW DIO", pins["swdio"]))
            count = count + 1
            TLog.generic(" ")

    def execute(self):
        """Execute the test."""

        TLog.generic("Start Pin ({}), End Pin ({})".format(self.args.start, self.args.end))
        TLog.generic("Target Voltage ({})".format(self.args.volts))

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.swd_scan(self.args.start,
                                    self.args.end,
                                    self.args.volts
                                    )
            if resp:
                found = True
                #self.output_handler(**resp)

                self.output_handler(logkwargs=LOGNO, **resp)
                self.display_swd_scan_result(resp)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.stop()

            if found is False:
                TLog.fail("Couldn't find swd pins")
