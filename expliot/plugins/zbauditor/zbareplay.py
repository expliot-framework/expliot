"""Support for Zigbee packet replay for zigbee auditor."""

import time
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.common.pcaphelper import PcapDumpReader
from expliot.core.protocols.radio.dot154 import Dot154Radio
from expliot.core.protocols.radio.dot154.dot154_utils import is_ack_packet, get_dst_pan_from_packet


# pylint: disable=bare-except
class ZbAuditorReplay(Test):
    """Zigbee packet dump replay plugin."""

    def __init__(self):
        super().__init__(
            name="replay",
            summary="IEEE 802.15.4 Packet Replay",
            descr="This plugin reads packets from the specified pcap file and "
            "replays them on the specified channel.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=["https://www.zigbee.org/wp-content/uploads/2014/11/docs-05-3474-20-0csg-zigbee-specification.pdf"],
            category=TCategory(TCategory.ZB_AUDITOR, TCategory.RD, TCategory.EXPLOIT),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
            needroot=True,
        )

        self.argparser.add_argument(
            "-c",
            "--channel",
            type=int,
            required=True,
            help="IEEE 802.15.4 2.4 GHz Channel to inject with zigbee packets",
        )

        self.argparser.add_argument(
            "-f",
            "--pcapfile",
            required=True,
            help="PCAP file name to be read for zigbee packets",
        )

        self.argparser.add_argument(
            "-p",
            "--pan",
            type=str,
            help="Replays packets for Destination PAN address in hex. "
            "Example:- 0x12ab or 12ab",
        )

        self.argparser.add_argument(
            "-d",
            "--delay",
            type=int,
            default=200,
            help="Interpacket delay in Miliseconds, default is 200ms",
        )

    def execute(self):
        """Execute the test."""

        # initialize local variables
        dst_pan = None
        send_packet = False

        # Get Destination PAN address
        if self.args.pan:
            dst_pan = int(self.args.pan, 16)

        delay_sec = self.args.delay / 1000

        TLog.generic("{:<13}: ({})".format("Channel", self.args.channel))
        TLog.generic("{:<13}: ({})".format("File", self.args.pcapfile))
        TLog.generic("{:<13}: ({})".format("Delay (seconds)", delay_sec))
        if dst_pan:
            TLog.generic("{:<15}: ({})".format("Destination PAN", hex(dst_pan)))
        TLog.generic("")

        try:
            # Get the zbauditor interface driver
            radio = Dot154Radio()

            # Get PCAP File Reader instance
            pcap_reader = PcapDumpReader(self.args.pcapfile)

            try:
                # Turn ON Radio
                radio.radio_on()

                # Set Channel
                radio.set_channel(self.args.channel)

                while True:
                    packet = pcap_reader.read_next_packet()
                    if packet:
                        if (not dst_pan
                                and not is_ack_packet(packet)):
                            send_packet = True

                        elif (dst_pan
                                and dst_pan == get_dst_pan_from_packet(packet)):
                            send_packet = True

                        if send_packet:
                            radio.inject_raw_packet(packet[0:-2])
                            send_packet = False
                            time.sleep(delay_sec)
                    else:
                        break

            finally:
                TLog.generic("{:<13}: ({})".format("Packet Received", radio.get_received_packets()))
                TLog.generic("{:<13}: ({})".format("Packet Transmit", radio.get_transmitted_packets()))
                pcap_reader.close()
                radio.radio_off()

        except:   # noqa: E722
            self.result.exception()
