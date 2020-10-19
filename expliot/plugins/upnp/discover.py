"""Support for UPNP discovery."""
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.core.protocols.internet.upnp import (
    UpnpDiscovery,
    DEFAULT_UPNP_TIMEOUT,
)
from expliot.plugins.upnp import UPNP_REFERENCE


class Discover(Test):
    """Discover devices with support for UPNP."""

    def __init__(self):
        """
        Initialize the UPNP discovery.

        Output Format:
        [
            {
            }
        ]
        """

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
            "-v", "--verbose", action="store_true", help="Show verbose output"
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            default=DEFAULT_UPNP_TIMEOUT,
            type=int,
            help="Timeout in seconds for each device type. "
                 "Default is {} seconds.".format(DEFAULT_UPNP_TIMEOUT)
        )

    def execute(self):
        """Execute the UPNP discovery."""

        TLog.generic("Search local network for UPNP enabled devices")
        scanner = UpnpDiscovery(timeout=self.args.timeout)
        scanner.scan()
        count = 0

        for dev in scanner.devices():
            count += 1
            TLog.success("Device {}:".format(count))
            self.output_handler(**dev)
        self.output_handler(total_devices_discovered=count)

        #    print("Found dev.__class__({}) dev({})".format(dev.__class__, dev))
        # if self.args.device:
        #     if self.args.device not in service_names:
        #         self.result.setstatus(passed=False, reason="Unknown device type specified")
        #         return
        #     service_names = [self.args.device]
        # cnt = 0
        # for name in service_names:
        #     if self.args.verbose:
        #         TLog.trydo("Looking for {} devices".format(name))
        #     details = MdnsDiscovery(name, scan_timeout=self.args.timeout)
        #     details.scan()
        #     for device in details.devices:
        #         cnt += 1
        #         self.output_handler(device_number=cnt,
        #                             name=device.name,
        #                             address=device.address,
        #                             port=device.port,
        #                             server=device.server,
        #                             type=device.type,
        #                             priority=device.priority,
        #                             weight=device.weight,
        #                             properties=device.properties)
        # self.output_handler(total_devices_discovered=cnt)

#    def print_details(self, dev):
#        for k, v in dev:
#            if k == "description" or k == :

