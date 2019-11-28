"""Wrapper for ZbAuditor interface."""
from expliot.core.interfaces.zbauditor.nrf52840 import NRF52840


class ZbAuditor:
    """Zigbee Auditor Class."""

    def __init__(self):
        """Get NRF52840 driver instance."""
        self.driver = None

        # Read NRF52840 driver
        self.driver = NRF52840()

    def get_interface_info(self):
        """Return Device information in dictionary format.

        :return: Dictionary of Device Name, FW Revision, Services
        """
        if self.driver is not None:
            name = self.driver.get_device_name()
            fw_rev = self.driver.get_device_fw_rev_str()
            services = self.driver.get_supported_services()
            dev_info = dict()
            dev_info["device_name"] = name
            dev_info["fw_revision"] = fw_rev
            dev_info["services"] = services
            return dev_info

    def set_channel(self, channel, page=0):
        """Validate and Set Channel to Device."""
        self.driver.device_set_channel(channel, page)

    def get_channel(self):
        """Return Channel from Device."""
        pass

    def get_radio_on_flag(self):
        """Return status of radio_on flag."""
        return self.driver.get_radio_on_flag()

    def set_radio_on_flag(self, flag):
        """Set radio_on flag."""
        self.driver.set_radio_on_flag(flag)

    def get_sniffer_on_flag(self):
        """Return status of sniffer_on flag."""
        self.driver.get_sniffer_on_flag()

    def set_sniffer_on_flag(self, flag):
        """Set sniffer_on flag."""
        self.driver.set_sniffer_on_flag(flag)

    def radio_on(self):
        """Turn on device radio."""
        self.driver.device_radio_on()

    def sniffer_on(self, channel, page=0):
        """Turn on device sniffer service."""

        self.driver.device_sniffer_on(channel, page)

    def packet_read(self, timeout=100):
        """Read data from device."""

        return self.driver.device_read(timeout)

    def radio_off(self):
        """Turn off device radio."""

        self.driver.device_radio_off()

    def sniffer_off(self):
        """Turn off device sniffer service."""
        self.driver.device_sniffer_off()

    def inject_packet(self, packet):
        """Inject packet to Device."""

        self.driver.device_inject_packet(packet)

    def scan_zb_network(self, mask):
        """Set Device in network scan mode.

        Additionally it return network scan result as dictionary.
        """
        return self.driver.device_scan_zigbee_network(mask)

    def get_rxcount(self):
        """Return packet receive count from driver.

        :return: rx count
        """
        return self.driver.rxcount

    def get_txcount(self):
        """Return packet transmit count from driver.

        :return: tx count
        """
        return self.driver.txcount

    def __del__(self):
        """Close the driver."""
        if self.driver:
            self.driver.close()
