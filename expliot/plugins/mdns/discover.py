"""Support for zero-configuration networking discovery."""
from expliot.core.discovery.mdns.constants import MDNS_SERVICE_TYPES
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.mdns import MDNS_REFERENCE
from expliot.core.discovery.mdns import MdnsDiscovery, DEFAULT_MDNS_TIMEOUT


class Discovery(Test):
    """Discover devices with support for mDNS."""

    def __init__(self):
        """Initialize the mDNS discovery."""

        super().__init__(
            name="discover",
            summary="Discover devices with support for mDNS.",
            descr="This plugin tries to detect devices in the local network "
                  "which are supporting mDNS. That mechanisms is called zero-"
                  "configuration networking and also known as Bonjour.",
            author="Fabian Affolter",
            email="fabian@affolter-engineering.ch",
            ref=[MDNS_REFERENCE],
            category=TCategory(TCategory.MDNS, TCategory.SW, TCategory.RECON),
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
            TLog.trydo("Supported Device types")
            for name in service_names:
                TLog.success("{}".format(name))
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
            for device in details.devices:
                cnt += 1
                TLog.success("Device {}".format(cnt))
                TLog.success("  (name={})".format(device.name))
                TLog.success("  (address={})".format(device.address))
                TLog.success("  (port={})".format(device.port))
                TLog.success("  (server={})".format(device.server))
                TLog.success("  (type={})".format(device.type))
                TLog.success("  (priority={})".format(device.priority))
                TLog.success("  (weight={})".format(device.weight))
                TLog.success("  (properties={})".format(device.properties))
                TLog.success("")
        TLog.success("Total devices discovered = {}".format(cnt))
