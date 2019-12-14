"""Support for discovery on the local network with mDNS."""
from collections import namedtuple
import ipaddress
import time

from zeroconf import ServiceBrowser, Zeroconf

from expliot.core.discovery import Discovery
from expliot.core.discovery.mdns.constants import MDNS_SERVICE_TYPES

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
        """No action if a device is disappearing."""
        pass

    def add_service(self, zeroconf, service_type, name):
        """Report the service found."""
        info = zeroconf.get_service_info(service_type, name)
        if info is not None:
            self.data.append(info)

    def get_data(self):
        """Return all collected announcements."""
        return self.data


class MdnsDiscovery(Discovery):
    """Discover local mDNS devices."""

    # pylint: disable=super-init-not-called
    def __init__(self, service_type):
        """Initialize the mDNS discovery."""
        self._service_type = MDNS_SERVICE_TYPES[service_type]
        self.device_list = []

    @property
    def devices(self):
        """Return the found devices."""
        return self.device_list

    def scan(self):
        """Scan the network for devices."""
        zeroconf = Zeroconf()
        listener = MdnsListener()
        ServiceBrowser(zeroconf, self._service_type, listener)
        time.sleep(1)
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
