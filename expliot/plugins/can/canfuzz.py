"""Testcase for fuzzing the CAN bus data message."""
from time import sleep
from random import randint
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.protocols.hardware.can import CanBus, CanMessage


class CANFuzz(Test):
    """Test for reading from the CAN bus."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="fuzzcan",
            summary="CAN bus fuzzer",
            descr="This plugin allows you to fuzz the message(s) on the CAN bus "
            "e.g, fuzz a data  frame. As of now it uses socketcan but if "
            "you want to extend it to other interfaces, just open an issue "
            "on the official expliot project repository.",
            author="Arun Magesh",
            email="arun.m@payatu.com",
            ref=["https://en.wikipedia.org/wiki/CAN_bus"],
            category=TCategory(TCategory.CAN, TCategory.HW, TCategory.FUZZ),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )
        self.argparser.add_argument(
            "-i", "--iface", default="vcan0", help="Interface to use. Default is vcan0"
        )
        self.argparser.add_argument(
            "-a",
            "--arbitid",
            required=True,
            type=lambda x: int(x, 0),
            help="Specify the arbitration ID. For hex value prefix it with 0x",
        )
        self.argparser.add_argument(
            "-e",
            "--exid",
            action="store_true",
            help="Specify this option if using extended format --arbitid",
        )
        self.argparser.add_argument(
            "-d",
            "--data",
            required=True,
            help="Specify the data to fuzz and the fuzzing byte to xx, as hex stream without the 0x prefix ",)
        self.argparser.add_argument(
            "-c",
            "--count",
            type=int,
            default=1,
            help="Specify the no. of messages to write. Default is 1",
        )
        self.argparser.add_argument(
            "-w",
            "--wait",
            type=float,
            default=0,
            help="Specify the wait time, in seconds, between each consecutive"
            "message write. Default is to not wait between writes. You "
            "may use float values as well, e.g., 0.5",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Fuzz Writing to CANbus on interface({}), arbitration id(0x{:x}), "
            "extended?({}) data({})".format(
                self.args.iface, self.args.arbitid, self.args.exid, self.args.data
            )
        )
        bus = None
        try:
            if self.args.count < 1:
                raise ValueError(
                    "Illegal count value {}".format(
                        self.args.count))
            if self.args.wait < 0:
                raise ValueError(
                    "Illegal wait value {}".format(
                        self.args.wait))
            bus = CanBus(bustype="socketcan", channel=self.args.iface)
            for count in range(self.args.count):
                datacan = self.args.data
                while datacan.find("xx") >= 0:
                    datacan = datacan.replace("xx", "{:02x}".format(
                        randint(0, 0xFF)), 1)  # main fuzzing magic with randint
                message = CanMessage(
                    arbitration_id=self.args.arbitid,
                    extended_id=self.args.exid,
                    data=list(
                        bytes.fromhex(datacan)))
                bus.send(message)
                TLog.success("{} : Wrote message {}  ".format(count, datacan))
                if self.args.wait > 0:
                    sleep(self.args.wait)
        except BaseException:
            self.result.exception()
        finally:
            if bus:
                bus.shutdown()
