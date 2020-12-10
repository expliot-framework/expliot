"""Support for Zigbee packet replay for zigbee auditor."""
import time
from expliot.core.common.exceptions import sysexcinfo
from expliot.core.common.pcaphelper import PcapDumpReader
from expliot.core.protocols.radio.dot154 import Dot154Radio
from expliot.core.protocols.radio.dot154.dot154_utils import (
    get_dst_pan_from_packet,
    is_ack_packet,
)
from expliot.core.tests.test import TCategory, Test, TLog, TTarget


# pylint: disable=bare-except
class ZbAuditorReplay(Test):
    """
    Zigbee packet dump replay plugin.

    Output Format:
    [
        {
            "packets_received": 0,
            "packets_transmitted": 9
        }
    ]
    """
    DELAYMS = 200

    def __init__(self):
        super().__init__(
            name="replay",
            summary="IEEE 802.15.4 packet replay",
            descr="This plugin reads packets from the specified pcap file and "
            "replays them on the specified channel.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[
                "https://www.zigbee.org/wp-content/uploads/2014/11/docs-05-3474-20-0csg-zigbee-specification.pdf"
            ],
            category=TCategory(TCategory.ZB_AUDITOR, TCategory.RD, TCategory.EXPLOIT),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-c",
            "--channel",
            type=int,
            required=True,
            help="IEEE 802.15.4 2.4 GHz channel to inject with Zigbee packets",
        )
        self.argparser.add_argument(
            "-f",
            "--pcapfile",
            required=True,
            help="PCAP file name to be read for Zigbee packets",
        )
        self.argparser.add_argument(
            "-p",
            "--pan",
            type=lambda x: int(x, 0),
            help="Replays packets for destination PAN address. Prefix 0x if pan is hex"
            "Example:- 0x12ab or 4779",
        )
        self.argparser.add_argument(
            "-d",
            "--delay",
            type=int,
            default=self.DELAYMS,
            help="Inter-packet delay in milliseconds. Default is {}".format(self.DELAYMS),
        )

    def execute(self):
        """Execute the test."""
        dst_pan = None
        send_packet = False
        pcap_reader = None
        radio = None

        # Get Destination PAN address
        if self.args.pan:
            dst_pan = self.args.pan

        delay_sec = self.args.delay / 1000

        TLog.generic("{:<13}: ({})".format("Channel", self.args.channel))
        TLog.generic("{:<13}: ({})".format("File", self.args.pcapfile))
        TLog.generic("{:<13}: ({})".format("Delay (seconds)", delay_sec))
        if dst_pan:
            TLog.generic("{:<15}: ({})".format("Destination PAN", hex(dst_pan)))
        TLog.generic("")

        try:
            radio = Dot154Radio()
            pcap_reader = PcapDumpReader(self.args.pcapfile)

            radio.radio_on()
            radio.set_channel(self.args.channel)

            while True:
                packet = pcap_reader.read_next_packet()
                if packet:
                    if not dst_pan and not is_ack_packet(packet):
                        send_packet = True
                    elif dst_pan and dst_pan == get_dst_pan_from_packet(packet):
                        send_packet = True

                    if send_packet:
                        radio.inject_raw_packet(packet[0:-2])
                        send_packet = False
                        time.sleep(delay_sec)
                else:
                    break

        except:  # noqa: E722
            self.result.setstatus(passed=False,
                                  reason="Exception caught: {}".format(sysexcinfo()))

        finally:
            # Close file handler
            if pcap_reader:
                pcap_reader.close()

            # Turn OFF radio and exit
            if radio:
                self.output_handler(packets_received=radio.get_received_packets(),
                                    packets_transmitted=radio.get_transmitted_packets())
                radio.radio_off()
