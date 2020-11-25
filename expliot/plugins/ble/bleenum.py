"""Support to scan for BLE devices."""
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.radio.ble import BlePeripheral, \
    ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC
from expliot.plugins.ble import BLE_REF


# pylint: disable=bare-except, too-many-nested-blocks
class BleEnum(Test):
    """
    Enumerate services/characteristics of a BLE device.

    Output Format:
    There are three types of output:
    1. Only services
    2. Only Characteristics
    3. Services and characteristics both

    [
        # Services
        {
            "service_uuid": "0000fee7-0000-1000-8000-00805f9b34fb",
            "service_uuid_name": "Foobar", # Human readable name of service, if any
            "handle_start": "0xa",
            "handle_end": "0x12"
        },
        # ... May be zero or more entries.
        # If no services found the above dict will not be present
        # Characteristics
        {
            "char_uuid": "00002a05-0000-1000-8000-00805f9b34fb",
            "char_uuid_name": "Foobar",
            "handle": "0xe",
            "supported_properties": "READ NOTIFY WRITE INDICATE NO RESPONSE",
                                    # One or more properties space separated
            "readvalue": "Foobar_value", # optional field, only present it characteristic
                                         # value can be read i.e. READ property is supported
        },
        # ... May be zero or more entries.
        # If no characteristics found the above dict will not be present
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="enum",
            summary="BLE Service/Characteristic Enumerator",
            descr="This plugin enumerates services and/or characteristics "
                  "of a single BLE device as specified by its BLE address.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[BLE_REF],
            category=TCategory(TCategory.BLE, TCategory.RD, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--addr",
            required=True,
            help="Address of BLE device whose services/characteristics will "
                 "be enumerated. If not specified, it does an address scan for all devices",
        )
        self.argparser.add_argument(
            "-r",
            "--randaddrtype",
            action="store_true",
            help="Use LE address type random. If not specified use address type public",
        )
        self.argparser.add_argument(
            "-s",
            "--services",
            action="store_true",
            help="Enumerate the services of the BLE device",
        )
        self.argparser.add_argument(
            "-c",
            "--chars",
            action="store_true",
            help="Enumerate the characteristics of the BLE device",
        )

    def execute(self):
        """
        Execute the plugin.
        Enumerate the services and/or characteristics of the specified BLE device.

        Returns:
            Nothing
        """
        # Documentation is wrong, the first keyword argument is deviceAddr instead of
        # deviceAddress. http://ianharvey.github.io/bluepy-doc/
        if self.args.services is False and self.args.chars is False:
            reason = "Incomplete args. Enumerate what? Either or both - services, chars"
            self.result.setstatus(passed=False, reason=reason)
            return
        TLog.generic(
            "Enumerating services/characteristics of the device {}".format(
                self.args.addr
            )
        )
        device = BlePeripheral()
        try:
            device.connect(
                self.args.addr,
                addrType=(
                    ADDR_TYPE_RANDOM
                    if self.args.randaddrtype
                    else ADDR_TYPE_PUBLIC
                ),
            )
            if self.args.services is True:
                services = device.getServices()
                for service in services:
                    self.output_handler(service_uuid=str(service.uuid),
                                        service_uuid_name=service.uuid.getCommonName(),
                                        handle_start=hex(service.hndStart),
                                        handle_end=hex(service.hndEnd))
            if self.args.chars is True:
                chars = device.getCharacteristics()
                for char in chars:
                    chardict = {"char_uuid": str(char.uuid),
                                "char_uuid_name": char.uuid.getCommonName(),
                                "handle": hex(char.getHandle()),
                                "supported_properties": char.propertiesToString()}
                    if char.supportsRead():
                        chardict["readvalue"] = char.read()
                    self.output_handler(**chardict)
        except:  # noqa: E722
            self.result.setstatus(passed=False,
                                  reason="Exception caught: {}".format(sysexcinfo()))
        finally:
            device.disconnect()
