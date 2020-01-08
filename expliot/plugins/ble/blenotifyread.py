"""Test the possibility of enabling notification for a characteristic on a Bluetooth LE device."""
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.protocols.radio.ble import BlePeripheral, \
    BleNotifyDelegate, ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC, \
    DEFAULT_NOTIFY_TIMEOUT
from expliot.core.common.timer import Timer
from expliot.plugins.ble import BLE_REF


# pylint: disable=bare-except
class BleNotifyRead(Test):
    """Plugin to enable notification and read characteristic data from a Bluetooth LE device."""

    def __init__(self):
        """Initialize the plugin."""
        super().__init__(
            name="notifychar",
            summary="BLE Characteristic Notification Reader",
            descr="This plugin allows you to send a notify request for a "
                  " characteristic, wait for notification data and display"
                  " the values received from the BLE peripheral device",
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
            help="Address of BLE device whose characteristic notify value will be read from",
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
        self.argparser.add_argument(
            "-t",
            "--timeout",
            default=DEFAULT_NOTIFY_TIMEOUT,
            type=int,
            help="Notification data timeout in seconds. Default is {} seconds".format(DEFAULT_NOTIFY_TIMEOUT),
        )

    @staticmethod
    def notifycb(handle, data):
        """Notification data read callback.

        Args:
            handle (int): The handle of the characteristic whose data is received.
            data (bytes): The data that is received from the BLE device.
        Returns:
            Nothing
        """
        TLog.success(data.hex())

    def execute(self):
        """Execute the test."""

        TLog.generic(
            "Reading from Notify handle ({}) on BLE device ({})".format(
                hex(self.args.handle), self.args.addr)
        )
        timer = Timer(self.args.timeout)
        ndelegate = BleNotifyDelegate(self.notifycb)
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
            TLog.generic("Enabling Notify on the handle")
            device.enable_notify(ndelegate, self.args.handle, write_response=True)
            while not timer.is_timeout():
                device.waitForNotifications(1)
            if ndelegate.count() > 0:
                TLog.success("Total notification data received {}".format(ndelegate.count()))
            else:
                self.result.setstatus(passed=False, reason="No notification data received from BLE peripheral")
        except:  # noqa: E722
            self.result.exception()
        finally:
            device.disconnect()
