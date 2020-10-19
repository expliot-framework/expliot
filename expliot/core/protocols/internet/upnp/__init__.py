"""Wrapper for UPNP Protocol"""
from upnpy.ssdp.SSDPRequest import SSDPRequest
from upnpy.ssdp.SSDPDevice import SSDPDevice
from expliot.core.discovery import Discovery

DEFAULT_UPNP_TIMEOUT = 2
DISCOVER_ALL = "ssdp:all"


def device_dict(self):
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
        "friendly_name": self.friendly_name,
        "type": self.type_,
        "base_url": self.base_url,
        "response": self.response,
        "description": self.description,
        "services": [srv.service_dict() for srv in self.get_services()]
    }
    return details


setattr(SSDPDevice, "device_dict", device_dict)


def service_dict(self):
    """

    """
    details = {
        "name": self.service,
        "type": self.type_,
        "version": self.version,
        "id": self.id,
        "description": self.description,
        "scpd_url": self.scpd_url,
        "control_url": self.control_url,
        "event_sub_url": self.event_sub_url,
        "base_url": self.base_url,
        "actions": [act.action_dict() for act in self.get_actions()],
        "state_variables": list(self.state_variables.keys())
    }
    return details


setattr(SSDPDevice.Service, "service_dict", service_dict)


def action_dict(self):
    """

    """
    details = {
        "name": self.name,
        "arguments": [arg.argument_dict() for arg in self.arguments]
    }
    return details


setattr(SSDPDevice.Service.Action, "action_dict", action_dict)


def state_variable_dict(self):
    """

    """
    details = {
        "name": self.name,
        "data_type": self.data_type,
        "allowed_value_list": self.allowed_value_list
    }
    return details


setattr(SSDPDevice.Service.StateVariable, "state_variable_dict", state_variable_dict)

def argument_dict(self):
    """

    """
    details = {
        "name": self.name,
        "direction": self.direction,
        "return_value": self.return_value,
        "related_state_variable": self.related_state_variable,
        # "arguments": [arg.argument_dict() for arg in self.arguments]
    }
    return details


setattr(SSDPDevice.Service.Action.Argument, "argument_dict", argument_dict)


class UpnpDiscovery(Discovery):
    """Discovery for UPNP devices on a network."""

    # pylint: disable=super-init-not-called
    def __init__(self, timeout=DEFAULT_UPNP_TIMEOUT, st=DISCOVER_ALL):
        self.timeout = timeout
        self.st = st
        self._devices = []

    def scan(self):
        ssdp = SSDPRequest()
        # devs = ssdp.m_search(discover_delay=self.timeout, st=DISCOVER_ALL)
        devs = ssdp.m_search(discover_delay=self.timeout, st=self.st)
        for dev in devs:
            self._devices.append(dev.device_dict())
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
