"""Support for zero-configuration networking discovery."""
from expliot.core.protocols.internet.mdns import MDNS_SERVICE_TYPES
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.mdns import MDNS_REFERENCE
from expliot.core.protocols.internet.mdns import MdnsDiscovery, DEFAULT_MDNS_TIMEOUT


class Discover(Test):
    """Discover devices with support for mDNS."""

    def __init__(self):
        """
        Initialize the mDNS discovery.

        Output Format:
        There are two different types of outputs
        1. Information of devices discovered
        [
            {
                "device_number": 1,
                "name": "Foobar name",
                "address": "192.168.1.1",
                "port": 2002,
                "server": "Foobar",
                "type": "Foobar",
                "priority: 2,
                "weight": 1,
                "properties": {
                                "fookey": "foovalue",
                                 # ... May be zero or more key value.
                              },
                # For more details please check class ServiceInfo in zeroconf
                # https://github.com/jstasiak/python-zeroconf/blob/master/zeroconf/__init__.py
            },
            # ... May be zero or more devices. If zero devices found the above dict will not
            # be present
            {
                "total_devices_discovered": 7
            }
        ]

        2. List of supported devices for discovery (--list argument)
        [
            {
                "supported_device_types": [
                                            'aidroid',
                                            'aiplay',
                                            'ssh',
                                            'workstation',
                                            # ... and more
                                          ]
            }
        ]
        """

        super().__init__(
            name="discover",
            summary="Discover devices with support for mDNS.",
            descr="This plugin tries to detect devices in the local network "
                  "which are supporting mDNS. That mechanisms is called zero-"
                  "configuration networking and also known as Bonjour.",
            author="Fabian Affolter",
            email="fabian@affolter-engineering.ch",
            ref=[MDNS_REFERENCE],
            category=TCategory(TCategory.MDNS, TCategory.SW, TCategory.DISCOVERY),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-v", "--verbose", action="store_true", help="Show verbose output"
        )
        self.argparser.add_argument(
            "-l", "--list", action="store_true", help="Show supported device types"
        )
        self.argparser.add_argument(
            "-d", "--device", help="Search for the specified device type only"
        )
        self.argparser.add_argument(
            "-t", "--timeout", default=DEFAULT_MDNS_TIMEOUT,
            type=float, help="Timeout in seconds for each device type. "
            "Default is {} seconds.".format(DEFAULT_MDNS_TIMEOUT)
        )

    def execute(self):
        """Execute the mDNS discovery."""

        service_names = list(MDNS_SERVICE_TYPES)
        if self.args.list:
            self.output_handler(supported_device_types=service_names)
            return
        TLog.generic("Search local network for mDNS enabled devices")

        if self.args.device:
            if self.args.device not in service_names:
                self.result.setstatus(passed=False, reason="Unknown device type specified")
                return
            service_names = [self.args.device]
        cnt = 0
        for name in service_names:
            if self.args.verbose:
                TLog.trydo("Looking for {} devices".format(name))
            details = MdnsDiscovery(name, scan_timeout=self.args.timeout)
            details.scan()
            for device in details.devices():
                cnt += 1
                self.output_handler(device_number=cnt,
                                    name=device.name,
                                    address=device.address,
                                    port=device.port,
                                    server=device.server,
                                    type=device.type,
                                    priority=device.priority,
                                    weight=device.weight,
                                    properties=device.properties)
        self.output_handler(total_devices_discovered=cnt)
