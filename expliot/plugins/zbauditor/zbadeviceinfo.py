"""Support for Zigbee Auditor Device Information."""
from expliot.core.interfaces.zbauditor import ZbAuditor
from expliot.core.tests.test import TCategory, Test, TLog, \
    TTarget, LOGNO


# pylint: disable=bare-except
class ZbAuditorDevInfo(Test):
    """Zigbee Auditor Device information Plugin."""

    def __init__(self):
        super().__init__(
            name="devinfo",
            summary="Displays Zigbee Auditor device information",
            descr="This plugin displays information about Zigbee Auditor.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=["Reference: Zigbee Auditor user manual"],
            category=TCategory(TCategory.ZB_AUDITOR, TCategory.RD, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )

    @staticmethod
    def display_device_info(info_dict):
        """Displays Device information"""

        if info_dict:
            TLog.success("Zigbee Auditor Details:")
            TLog.success("{:<17}: {}".format("Device Name", info_dict["device_name"]))
            TLog.success("{:<17}: {}".format("FW Revision", info_dict["fw_revision"]))
            TLog.generic("")

            if "services" in info_dict:
                services = info_dict["services"]

                TLog.generic("Services:")
                for _, (serivce, value) in enumerate(services.items()):
                    TLog.success("\t {:<23}: {}".format(serivce, value))

            TLog.generic("")

    def execute(self):
        """Execute the test."""

        try:
            auditor = ZbAuditor()
            dev_info_dict = auditor.get_interface_info()
            self.output_handler(logkwargs=LOGNO, **dev_info_dict)
            self.display_device_info(dev_info_dict)
        except:  # noqa: E722
            self.result.exception()
            return
