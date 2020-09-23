"""Wrapper for UPNP Protocol"""
from upnpy.ssdp.SSDPRequest import SSDPRequest
from upnpy.ssdp.SSDPDevice import SSDPDevice
from expliot.core.discovery import Discovery

DEFAULT_UPNP_TIMEOUT = 2
DISCOVER_ALL = "ssdp:all"


def device_details(self):
    """
    Get the details of the Device in a dict.

    Args:
        None
    Returns:
        dict: Dictionary containing the device details. Dict
        keys are:
            1. host
            2. port
            3. description
            4. friendly_name
            5. type
            6. base_url
    """
    details = {
        "host": self.host,
        "port": self.port,
        "response": self.response,
        "description": self.description,
        "friendly_name": self.friendly_name,
        "type": self.type_,
        "base_url": self.base_url,
        "services": self.services
    }
    return details


setattr(SSDPDevice, "device_details", device_details)


class UpnpDiscovery(Discovery):
    """Discovery for UPNP devices on a network."""

    # pylint: disable=super-init-not-called
    def __init__(self, timeout=DEFAULT_UPNP_TIMEOUT):
        self.timeout = timeout
        self._devices = []

    def scan(self):
        ssdp = SSDPRequest()
        # devs = ssdp.m_search(discover_delay=self.timeout, st=DISCOVER_ALL)
        devs = ssdp.m_search(discover_delay=self.timeout, st="upnp:rootdevice")
        for dev in devs:
            self._devices.append(dev.details())
            print("Found dev({})".format(dev))

    def devices(self):
        """
         Returns the UPNP devices found in the network.

         Args:
             Nothing
         Returns:
             list: List of devices found
         """

        return self._devices
