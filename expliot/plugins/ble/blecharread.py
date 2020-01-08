"""Test the possibility to read characteristic data from a Bluetooth LE device."""
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.protocols.radio.ble import BlePeripheral, \
    ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC
from expliot.plugins.ble import BLE_REF


# pylint: disable=bare-except
class BleCharRead(Test):
    """Plugin to read characteristic data from a Bluetooth LE device."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="readchar",
            summary="BLE Characteristic Reader",
            descr="This plugin allows you to read a characteristic value from a BLE peripheral device",
            author="Arun Magesh",
            email="arun.m@payatu.com",
            ref=[BLE_REF],
            category=TCategory(
                TCategory.BLE,
                TCategory.RD,
                TCategory.ANALYSIS),
            target=TTarget(
                TTarget.GENERIC,
                TTarget.GENERIC,
                TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--addr",
            required=True,
            help="Address of BLE device whose characteristic value will be read from",
        )
        self.argparser.add_argument(
            "-n",
            "--handle",
            required=True,
            type=lambda x: int(x, 0),
            help="Specify the handle to read from. Prefix 0x if handle is hex",
        )

        self.argparser.add_argument(
            "-r",
            "--randaddrtype",
            action="store_true",
            help="Use LE address type random. If not specified use address type public",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Reading from handle ({}) on BLE device ({})".format(
                hex(self.args.handle), self.args.addr
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
            TLog.success(
                " (value={})".format(
                    device.readCharacteristic(
                        self.args.handle)))
        except:  # noqa: E722
            self.result.exception()
        finally:
            device.disconnect()
