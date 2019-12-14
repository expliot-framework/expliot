"""Support for zero-configuration networking discovery."""
from expliot.core.discovery.mdns.constants import MDNS_SERVICE_TYPES
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.mdns import MDNS_REFERENCE
from expliot.core.discovery.mdns import MdnsDiscovery


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
            "-v", "--verbose", action="store_true", help="show verbose output"
        )

    def execute(self):
        """Execute the mDNS discovery."""
        TLog.generic("Search local network for mDNS enabled devices")

        for service_name in MDNS_SERVICE_TYPES:
            if self.args.verbose:
                TLog.generic("Looking for {} devices".format(service_name))
            details = MdnsDiscovery(service_name)
            details.scan()
            for device in details.devices:
                TLog.success(device)

        self.result.setstatus(passed=True)
