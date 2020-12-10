"""Support for Bus Auditor Device Information."""
from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TTarget
from expliot.plugins.busauditor import BUSAUDITOR_REFERENCE


# pylint: disable=bare-except
class BaDevInfo(Test):
    """
    BusAuditor Device information Plugin.

    Output Format:
    [
        {
            "device_name": "BusAuditor",
            "serial_number": "348435533437",
            "fw_revision": "0.0.53",
            "hw_revision": "0.1",
            "services": {
                            "read_revision": True,
                            "read_services": True,
                            "jtag_port_scan": True,
                            "swd_port_scan": True,
                            "uart_port_scan": True,
                            "i2c_bus_scan": True
                        }
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="devinfo",
            summary="BusAuditor device information",
            descr="This plugin displays information about BusAuditor device.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[BUSAUDITOR_REFERENCE],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

    def execute(self):
        """Execute the test."""

        auditor = None

        try:
            auditor = BusAuditor()
            dev_info_dict = auditor.get_interface_info()

            self.output_handler(**dev_info_dict)

        except:  # noqa: E722
            self.result.exception()

        finally:
            if auditor:
                auditor.close()
