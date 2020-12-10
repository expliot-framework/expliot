"""Support to scan for BLE devices."""
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.radio.ble import Ble
from expliot.plugins.ble import BLE_REF


# pylint: disable=bare-except, too-many-nested-blocks
class BleScan(Test):
    """
    Scan for BLE devices.

    output Format:
    [
        {
            "name": "Foobar", # Device name if present or "Unknown"
            "addr": "de:ad:be:ef:00:00", # Device BLE address
            "addrtype": "random", # or "public" addr type
            "rssi": "60 dBm",  # RSSI strength
            "connectable": True, # or False
            "adtype_data": [
                                {
                                    "adtype": 25, # int
                                    "description": "Foobar", # Human readable adtype name
                                    "value": "Foobar" # Value of adtype
                                },
                                ... # may be more than one adtype_data
                            ]
        },
        # ... May be zero or more entries.
        # If zero ble devices found the above dict will not be present
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="scan",
            summary="BLE Scanner",
            descr="This plugin scans for BLE devices in (BLE range) "
            " proximity. NOTE: This plugin needs root privileges. "
            "You may run it as $ sudo expliot.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[BLE_REF],
            category=TCategory(TCategory.BLE, TCategory.RD, TCategory.DISCOVERY),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )
        self.argparser.add_argument(
            "-i",
            "--iface",
            default=0,
            type=int,
            help="HCI interface no. to use for scanning. 0 = hci0, 1 = hci1 "
            "and so on. Default is 0",
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            default=10,
            type=int,
            help="Scan timeout. Default is 10 seconds",
        )
        self.found = False

    def execute(self):
        """
        Execute the plugin.
        Scan for BLE devices in the proximity.

        Returns:
            Nothing
        """
        found = False
        TLog.generic("Scanning BLE devices for {} second(s)".format(self.args.timeout))
        try:
            devices = Ble.scan(iface=self.args.iface, tout=self.args.timeout)
            for device in devices:
                found = True
                outdict = {"name": device.getValueText(Ble.ADTYPE_NAME) or "Unknown",
                           "addr": device.addr,
                           "addrtype": device.addrType,
                           "rssi": "{} dBm".format(device.rssi),
                           "connectable": device.connectable,
                           "adtype_data": []}
                for scan_data in device.getScanData():
                    outdict["adtype_data"].append({"adtype": scan_data[0],
                                                   "description": scan_data[1],
                                                   "value": scan_data[2]})
                self.output_handler(**outdict)
        except:  # noqa: E722
            self.result.setstatus(passed=False,
                                  reason="Exception caught: {}".format(sysexcinfo()))

        if found is False:
            TLog.fail("No BLE devices found")
