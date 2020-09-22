"""Wrapper for UPNP Protocol"""
from upnpy.ssdp import SSDPRequest, SSDPDevice

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
