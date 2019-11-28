"""Support for Zigbee protocol plugins."""

from expliot.core.interfaces.zbauditor import ZbAuditor


class ZigbeeNetworkScan:
    """Scan Zigbee network for available device."""

    def __init__(self):
        """Get instance of Zigbee auditor."""
        self.__zbauditor = ZbAuditor()

    def get_device_info(self):
        """Return device basic information"""
        return self.__zbauditor.get_interface_info()

    def scan(self, mask=0x07FFF800):
        """Scan network for channel mask and return result as dictionary."""
        # start_time = time.time()
        result = self.__zbauditor.scan_zb_network(mask)
        # end_time = time.time()
        return result
