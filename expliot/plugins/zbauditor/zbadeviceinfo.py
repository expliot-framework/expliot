"""Support for Zigbee Auditor Device Information."""
from expliot.core.interfaces.zbauditor import ZbAuditor
from expliot.core.tests.test import TCategory, Test, TTarget


# pylint: disable=bare-except
class ZbAuditorDevInfo(Test):
    """
    Zigbee Auditor Device information Plugin.

    Output Format:
    [
        {
            'device_name': 'ZigBee Auditor',
            'fw_revision': '1.0.3',
            'serial_number': 'E761FB48B6E4',
            'services': {
                'read_revision': True,
                'read_services': True,
                'channel_selection': True,
                'radio on_off': True,
                '802.15.4_sniffer': True,
                '802.15.4_injection': True,
                '802.15.4_network_scan': True,
                '2.4_ghz': True
            }
        }
    ]
    """

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
        )

    def execute(self):
        """Execute the test."""

        try:
            auditor = ZbAuditor()
            dev_info_dict = auditor.get_interface_info()
            self.output_handler(**dev_info_dict)
        except:  # noqa: E722
            self.result.exception()
            return
