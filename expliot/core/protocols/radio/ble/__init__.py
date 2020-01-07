"""Support for BLE."""
from bluepy.btle import Scanner, Peripheral, DefaultDelegate, \
    ADDR_TYPE_RANDOM, ADDR_TYPE_PUBLIC


DEFAULT_NOTIFY_TIMEOUT = 10


class Ble:
    """A wrapper around simple BLE operations."""
    # Advertising Data Type value for "Complete Local Name"
    # Ref: https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile
    ADTYPE_NAME = 9

    @staticmethod
    def scan(iface=0, tout=10):
        """Scan for BLE devices."""
        scanner = BleScanner(iface)
        scanentries = scanner.scan(timeout=tout)
        return scanentries


class BleScanner(Scanner):
    """A wrapper around bluepy Scanner class."""

    pass


class BlePeripheral(Peripheral):
    """A wrapper around bluepy Peripheral class."""

    def enable_notify(self, delegate, handle, write_response=False):
        """
        Enables notification for a specific characteristic on a Peripheral.
        It's a Wrapper on Peripheral class methods for setting Delegate and
        writing to the characteristic(handle + 1) the value "\0x01\x00" to
        enable the notification as per the BLE spec.

        Args:
            delegate (DefaultDelegate): Overriden DefaultDelegate Object
            handle (int): The handle of the characteristic for notification
            write_response (bool): True, if sending write command and False if
                sending only write request (for which there is no response
                from the peripheral). Default is False.
        """
        self.withDelegate(delegate)
        self.writeCharacteristic(handle + 1, b"\x01\x00", withResponse=write_response)


class BleNotifyDelegate(DefaultDelegate):
    """Delegate class for reading notification data as required by Bluepy"""

    def __init__(self, callback):
        """Initialize with super's init and set custom callback. This is implemented
           to keep a tab on the no. of times handleNotification is called.

        Args:
            callback (callback(handle, data)): Callback method to be specified
                by the caller. It takes two parameters - handle and data which
                are the same as Bluepy handleNotification() callback
        """
        DefaultDelegate.__init__(self)
        self._count = 0
        self._callback = callback

    def count(self):
        """Count of the no. of times handleNotification() is called.

        Args:
            None
        Returns:
            (int) Returns the count
        """
        return self._count

    def handleNotification(self, cHandle, data):
        """Callback method as defined by Bluepy.

        Args:
            cHandle(integer): handle for the characteristic - this can be
                used to distinguish between notifications from multiple
                sources on the same peripheral.
            data(bytes): The characteristic data received.
        Returns:
             Nothing

        """
        self._count += 1
        self._callback(cHandle, data)
