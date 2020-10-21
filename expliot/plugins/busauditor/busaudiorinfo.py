"""Support for Zigbee Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget, LOGNO


# pylint: disable=bare-except
class BusAuditorDevInfo(Test):
    """
    BusAuditor Device information Plugin.

    Output Format:
    [{
        "device_name": "Payatu BusAuditor",
        "fw_revision": "1.0.0"
        "serial_number": "348435533437"
        "hw_revision": "1.0"
        "services": {
                        "Read Revision":True,
                        "Read Services":True,
                        "JTAG Scan":True,
                        "SWD Scan":True,
                        "UART Scan":True,
                        "I2C Scan":True
                    }
    }]
    """

    def __init__(self):
        super().__init__(
            name="devinfo",
            summary="Displays BusAuditor device information",
            descr="This plugin displays information about BusAuditor.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=["Reference: BusAuditor user manual"],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )

    @staticmethod
    def display_device_info(info_dict):
        """
        Displays Device information.

        Args:
            info_dict (dict): Dict of Device information
        Returns:
           Nothing
        Raises:
            Nothing
        """

        if info_dict:
            TLog.success("BusAuditor Details:")
            TLog.success(
                "Device Name:\t{}".format(
                    info_dict["device_name"]
                )
            )
            TLog.success(
                "Serial Number:\t{}".format(
                    info_dict["serial_number"]
                )
            )
            TLog.success(
                "FW Revision:\t{}".format(
                    info_dict["fw_revision"]
                )
            )
            TLog.success(
                "HW Revision:\t{}".format(
                    info_dict["hw_revision"]
                )
            )
            TLog.generic(" ")

            if "services" in info_dict:
                services = info_dict["services"]

                TLog.success("Services:")
                for _, (serivce, value) in enumerate(services.items()):
                    TLog.success(
                        "\t{}:\t{}".format(
                            serivce, value
                        )
                    )

            TLog.generic("")

    def execute(self):
        """Execute the test."""

        auditor = None

        try:
            auditor = BusAuditor()
            dev_info_dict = auditor.get_interface_info()

            # self.output_handler(**dev_info_dict)
            self.output_handler(logkwargs=LOGNO, **dev_info_dict)
            self.display_device_info(dev_info_dict)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.stop()
