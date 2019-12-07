"""Support for IEEE802.15.4 Protocol Plugins"""

import time
import struct
from expliot.core.common.pcaphelper import PcapDumper, PcapDumpReader, PcapFrame
from expliot.core.common.timer import Timer
from expliot.core.interfaces.zbauditor import ZbAuditor


class Dot154Radio:
    """Radio Class for IEEE 802.15.4 Protocol."""

    def __init__(self):
        """Get Zb Auditor instance."""

        self.__zbauditor = None

        self.__zbauditor = ZbAuditor()

    def get_device_info(self):
        """Returns basic information of Radio attached."""

        return self.__zbauditor.get_interface_info()

    def radio_on(self):
        """Turn ON Radio."""

        self.__zbauditor.radio_on()

    def set_channel(self, channel, page=0):
        """Set Channel and Page."""

        self.__zbauditor.set_channel(channel, page)

    def sniffer_on(self, channel, page=0):
        """Turn ON Sniffer.

        :param channel: zigbee channel
        :param page: zigbee frequecy page
        """

        self.__zbauditor.sniffer_on(channel, page)

    def read_raw_packet(self):
        """Read single packet from radio driver.

        :return: dict with packet as element
        """

        packet = self.__zbauditor.packet_read()
        if packet is not None:
            return packet["packet"]
        return None

    def sniffer_off(self):
        """Turn OFF Sniffer."""

        self.__zbauditor.sniffer_off()

    def radio_off(self):
        """Turn OFF Radio."""

        self.__zbauditor.radio_off()

    def inject_raw_packet(self, packet):
        """Send raw packet to radio driver."""

        self.__zbauditor.inject_packet(packet)

    def get_received_packets(self):
        """Returns total number of packet received."""

        return self.__zbauditor.get_rxcount()

    def get_transmitted_packets(self):
        """returns total number of packet transmitted."""

        return self.__zbauditor.get_txcount()

    def __del__(self):
        if self.__zbauditor:
            self.radio_off()
