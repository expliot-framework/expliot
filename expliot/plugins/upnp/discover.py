"""Support for UPNP discovery."""
from expliot.core.common import recurse_list_dict
from expliot.core.tests.test import TCategory, Test, TLog, TTarget, LOGNO
from expliot.core.protocols.internet.upnp import (
    UpnpDiscovery,
    DEFAULT_UPNP_TIMEOUT,
)
from expliot.plugins.upnp import UPNP_REFERENCE


class Discover(Test):
    """
    Discover devices with support for UPNP.

    Output Format:
    [
        {
            "host": "192.168.12.11",
            "port": 1900,
            "friendly_name": "WFADevice",
            "type": "urn:schemas-wifialliance-org:device:WFADevice:1",
            "base_url": "http://192.168.12.11:1900",
            "response": "HTTP/1.1 200 OK...",
            "description": "<?xml...",
            "services":
            [
                {
                    "name": "urn:schemas-wifialliance-org:service:WFAWLANConfig:1",
                    "type": "WLANConfig",
                    "version": 1,
                    "id": "urn:wifialliance-org:serviceId:WLANConfig1",
                    "description": "<?xml...",
                    "scpd_url": "http://192.168.12.11:1900/wlanconfig.xml",
                    "control_url": "/controls?WLANConfig",
                    "event_sub_url": "/events?WLANConfig",
                    "base_url": "http://192.168.12.11:1900",
                    "actions":
                    [
                        {
                            "name": "ModAPSettings",
                            "arguments":
                            [
                                {
                                    "name": "NewAPSettings",
                                    "direction": "in",
                                    "return_value": None,
                                    "related_state_variable": "APSettings",
                                }, # Zero or more arguments
                            ]
                        }, # Zero or more actions
                    ],
                    "state_variables":
                    [
                        "WLANEventType",
                        "APSettings",
                        "Message",
                    ] # Zero or more state variables
                }, # Zero or more services
            ]
        }, # Zero or more device entries
        {
            "total_devices_discovered": 2
        }
    ]
    """

    def __init__(self):
        """Initialize the UPNP discovery."""

        super().__init__(
            name="discover",
            summary="Discover devices with support for UPNP.",
            descr="This plugin tries to detect devices in the local network "
                  "which support UPNP (Universal Plug aNd Play.",
            author="Aseem Jakhar",
            email="aseem@expliot.io",
            ref=[UPNP_REFERENCE],
            category=TCategory(TCategory.UPNP, TCategory.SW, TCategory.DISCOVERY),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Show verbose output (response and xml)"
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            default=DEFAULT_UPNP_TIMEOUT,
            type=int,
            help="Timeout in seconds for each device type. "
                 "Default is {} seconds".format(DEFAULT_UPNP_TIMEOUT)
        )

    def execute(self):
        """Execute the UPNP discovery."""

        TLog.generic("Search local network for UPNP enabled devices")
        scanner = UpnpDiscovery(timeout=self.args.timeout)
        scanner.scan()
        count = 0

        for dev in scanner.devices():
            count += 1
            TLog.generic("")
            TLog.success("Device {}:".format(count))
            self.output_handler(logkwargs=LOGNO, **dev)
            recurse_list_dict(dev, self.log_callback, None)
        self.output_handler(total_devices_discovered=count)

    def log_callback(self, cbdata, robj, rlevel, key=None, value=None):
        """
        Callback for recursive iteration of dict. It logs everything
        except for response data and description(xml) unless the
        user runs the plugin in verbose mode.

        Args:
            Check recurse_list_dict() documentation for argument details
        Returns:
            Nothing
        """
        spaces = "  " * rlevel
        if key in ("description", "response") and (not self.args.verbose):
            return
        if robj.__class__ == dict and \
                (value.__class__ == dict or value.__class__ == list):
            TLog.success("{}{}:".format(spaces, key))
        else:
            if key:
                TLog.success("{}{}: {}".format(spaces, key, value))
            else:
                TLog.success("{}{}".format(spaces, value))
