"""Support for discovery on the local network with mDNS."""
from collections import namedtuple
import ipaddress
import time

from zeroconf import ServiceBrowser, Zeroconf

from expliot.core.discovery import Discovery
from expliot.core.discovery.mdns.constants import MDNS_SERVICE_TYPES


DEFAULT_MDNS_TIMEOUT = 1.0

DeviceDetails = namedtuple(
    "DeviceDetails",
    ["name", "type", "address", "port", "weight", "priority", "server", "properties"],
)


class MdnsListener:
    """Listener for the detection of zero-configuration devices."""

    def __init__(self):
        """Initialize the listener."""
        self.data = []

    def remove_service(self, zeroconf, service_type, name):
        """
        Callback to remove a service from the Listener.
        No action if a device is disappearing.

        Args:
            zeroconf(Zeroconf): The Zeroconf Object that has the scanning data.
            service_type(str): The device service type to be removed.
            name(str): The device name to be removed.
        Returns:
            Nothing
        """
        pass

    def add_service(self, zeroconf, service_type, name):
        """
        Callback to add the service found, in the listener.

        Args:
            zeroconf(Zeroconf): The Zeroconf Object that has the scanning data.
            service_type(str): The device service type.
            name(str): The device name.
        Returns:
            Nothing
        """
        info = zeroconf.get_service_info(service_type, name)
        if info is not None:
            self.data.append(info)

    def get_data(self):
        """
        Return all collected announcements.

        Returns (list):
            List of the found devices.
        """
        return self.data


class MdnsDiscovery(Discovery):
    """Discover local mDNS devices."""

    # pylint: disable=super-init-not-called
    def __init__(self, service_type, scan_timeout=1):
        """
        Initialize the mDNS discovery.

        Args:
            service_type(str): Type of service, from the supported ones, to search for.
            scan_timeout(float): Timeout in seconds for each scan(). It is basically
                                 sleep() time
        Returns:
            Nothing
        """
        self._service_type = MDNS_SERVICE_TYPES[service_type]
        self.device_list = []
        self.scan_timeout = scan_timeout

    @property
    def devices(self):
        """
        Return the found devices.

        Returns (list):
            List of devices found
        """
        return self.device_list

    def scan(self):
        """Scan the network for devices."""

        zeroconf = Zeroconf()
        listener = MdnsListener()
        ServiceBrowser(zeroconf, self._service_type, listener)
        time.sleep(self.scan_timeout)
        for info in listener.get_data():
            data = {
                "name": info.name,
                "type": info.type,
                "address": str(ipaddress.IPv4Address(info.addresses[0])),
                "port": info.port,
                "weight": info.weight,
                "priority": info.priority,
                "server": info.server,
                "properties": info.properties,
            }
            self.device_list.append(DeviceDetails(**data))
        zeroconf.close()
