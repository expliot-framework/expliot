"""Plugin to decrypt TPlink PCAP."""


from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.core.vendors.tplink import crypto


class TPlinkdecrypt(Test):
    """Test for TPLink Smart devices."""

    def __init__(self):
        """Initialize the test for TPlink smart devices."""
        super().__init__(
            name="decrypt",
            summary="TPLink Smart device communication decryption ",
            descr="This plugin helps to fetch the json from the encrypted "
            "commands being sent by the user through the KASA mobile to the "
            "TP-Link smart device & this fetched json can be then sent to the "
            "target device using takeover plugin.",
            author="Appar Thusoo",
            email="appar@payatu.com",
            ref=[
                "https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/",
                "https://github.com/softScheck/tplink-smartplug"],
            category=TCategory(TCategory.CRYPTO, TCategory.SW, TCategory.EXPLOIT),
            target=TTarget(TTarget.TP_LINK_IOT, "1.0", TTarget.TP_LINK),
        )

        self.argparser.add_argument(
            "-d",
            "--data",
            required=True,
            help="Specify the hex string from the sniffed communication, without the 0x prefix. Ex. 2a3b4cddeeff11",
        )

    def execute(self):
        """Execute the test."""
        result = crypto.decrypt(self.args.data)
        TLog.generic("Decrypted Data :" + str(result))
