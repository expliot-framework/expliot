"""Support for Zigbee Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget, LOGNO


# pylint: disable=bare-except
class BusAuditorI2CScan(Test):
    """
    Test selected channels for I2C communication protocol.
    
    Output Format:
    [{
        "devices": 
        [
            {
                "i2c_addr": "0x48",
                "pins": {
                    "scl": 5,
                    "sda": 6
                }
            }, {
                "i2c_addr": "0x50",
                "pins": {
                    "scl": 5,
                    "sda": 6
                }
            }
            #...
        ]
    }]
    """

    def __init__(self):
        super().__init__(
            name="i2cscan",
            summary="Displays i2c scan information",
            descr="This plugin scans and display i2c pins of target hardware.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[
                "https://en.wikipedia.org/wiki/I%C2%B2C"
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
            default=8,
            help="First pin to start the scan. If "
            "not specified, it will start the scan from pin 0",
        )
        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=12,
            help="Last pin. If "
            "not specified, it will scan until pin 15",
        )

    @staticmethod
    def display_i2c_scan_result(result_dict):
        """
        Displays I2C idcode scan result.
        
        Args:
            result_dict (dict): Dict of I2C scan information
        Returns:
           Nothing
        Raises:
            Nothing
        """

        TLog.success("I2C port scan result:")
        
        indx = 1
        devices = result_dict["devices"]
        for dev in devices:
            TLog.success("Device {}:".format(indx))
            TLog.success("\t{:<8}: {}".format("I2C Address", dev["i2c_addr"]))

            pins = dev["pins"]
            TLog.success("\t{:<8}: {}".format("SCL", pins["scl"]))
            TLog.success("\t{:<8}: {}".format("SDA", pins["sda"]))
            indx = indx + 1
            TLog.generic(" ")


    def execute(self):
        """Execute the test."""

        TLog.generic("Start Pin ({}), End Pin ({})".format(self.args.start, self.args.end))
        TLog.generic("Target Voltage ({})".format(self.args.volts))

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.i2c_scan(self.args.start,
                                    self.args.end,
                                    self.args.volts
                                    )
            if resp:
                found = True
                # self.output_handler(**resp)

                self.output_handler(logkwargs=LOGNO, **resp)
                self.display_i2c_scan_result(resp)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.stop()

            if found is False:
                TLog.fail("Couldn't find i2c pins")
