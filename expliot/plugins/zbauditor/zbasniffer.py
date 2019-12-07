"""Support for IEEE 802.15.4 packet sniff amd packet dump for Zigbee auditor."""
from expliot.core.common.pcapdlt import PCAP_DLT_IEEE802_15_4
from expliot.core.common.pcaphelper import PcapDumper, PcapFrame
from expliot.core.common.timer import Timer
from expliot.core.protocols.radio.dot154 import Dot154Radio
from expliot.core.tests.test import TCategory, Test, TLog, TTarget


# pylint: disable=bare-except
class ZbAuditorSniffer(Test):
    """IEEE 802.15.4 packet sniffer Plugin."""

    def __init__(self):
        super().__init__(
            name="sniffer",
            summary="IEEE 802.15.4 packet sniffer",
            descr="This plugin captures IEEE 802.15.4 packets on a specified "
            "channel and saves them in pcap format.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[
                "https://www.zigbee.org/wp-content/uploads/2014/11/docs-05-3474-20-0csg-zigbee-specification.pdf"
            ],
            category=TCategory(TCategory.ZB_AUDITOR, TCategory.RD, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )

        self.argparser.add_argument(
            "-c",
            "--channel",
            type=int,
            required=True,
            help="IEEE 802.15.4 2.4 GHz channel to sniff for Zigbee packets",
        )

        self.argparser.add_argument(
            "-f",
            "--filepath",
            required=True,
            help="PACP file name to save packet dump file.",
        )

        self.argparser.add_argument(
            "-n",
            "--count",
            default=65535,
            type=int,
            help="Number of packets to be captured before plugin stop. "
            "Default is 65535 packets.",
        )

        self.argparser.add_argument(
            "-t",
            "--timeout",
            default=0,
            type=int,
            help="Sniffer timeout in seconds. "
            "Default is 0 seconds to mean keep running",
        )

    def execute(self):
        """Execute the test."""

        count = self.args.count
        timeout = self.args.timeout
        packetcount = 0

        TLog.generic("{:<13}: ({})".format("Channel", self.args.channel))
        TLog.generic("{:<13}: ({})".format("File", self.args.filepath))
        TLog.generic("{:<13}: ({})".format("Count", count))
        TLog.generic("{:<13}: ({})".format("Time-Out", timeout))

        try:
            # Get the Sniffer interface driver
            radio = Dot154Radio()

            # Create pcap file to dump the packet
            pcap_writer = PcapDumper(PCAP_DLT_IEEE802_15_4, self.args.filepath)

            try:
                # Turn ON radio sniffer
                radio.sniffer_on(self.args.channel)

                # kick start timer, if user set some timeout
                if timeout != 0:
                    # Create Timer for timeout check
                    timer = Timer()
                    timer.timeout = timeout

                while True:
                    packet = radio.read_raw_packet()
                    if packet is not None:
                        packetcount += 1
                        pcap_frame = PcapFrame(packet)
                        pcap_writer.write_to_pcapfile(pcap_frame.get_pcap_frame())

                    if timeout != 0:
                        if timer.is_timeout():
                            break

                    if packetcount == count:
                        break
            finally:
                TLog.generic("")
                TLog.generic(
                    "{:<13}: ({})".format(
                        "Packet received", radio.get_received_packets()
                    )
                )
                TLog.generic(
                    "{:<13}: ({})".format(
                        "Packet transmit", radio.get_transmitted_packets()
                    )
                )

                # Turn OFF radio sniffer and exit
                pcap_writer.close()
                radio.sniffer_off()

        except:  # noqa: E722
            self.result.exception()
