"""Helper for pacp files."""
from datetime import datetime
import struct
import sys

# Wireshark file format, File Header and packet header are verified as per Wireshark development guide
# Refer: https://wiki.wireshark.org/Development/LibpcapFileFormat


# Wireshark magic number
# a1 b2 c3 d4 if the file was written on a BE machine and has microsecond-resolution time stamps;
# d4 c3 b2 a1 if the file was written on a LE machine and has microsecond-resolution time stamps;
# a1 b2 3c 4d if the file was written on a BE machine and has nanosecond-resolution time stamps;
# 4d 3c b2 a1 if the file was written on a LE machine and has nanosecond-resolution time stamps.
PCAPH_MAGIC_NUM_BE = 0xA1B2C3D4
PCAPH_MAGIC_NUM_LE = 0xD4C3B2A1
PCAPH_MAGIC_NUM_BE_NS = 0xA1B23C4D
PCAPH_MAGIC_NUM_LE_NS = 0x4D43CB2A1

# Wireshark Major, Minor versions, timezone, sigfigs, and snaplen
PCAPH_VER_MAJOR = 2
PCAPH_VER_MINOR = 4
PCAPH_THISZONE = 0
PCAPH_SIGFIGS = 0
PCAPH_SNAPLEN = 65535

# Wireshark global header length
WIRESHARK_GLB_HDR_LEN = 24

# Wireshark packet header length
WIRESHARK_PKT_HDR_LEN = 16

SYS_LE_STR = "little"
SYS_BE_STR = "big"


class PcapFrame:
    """Helper class to create pcap frame to write in pcap file."""

    def __init__(self, packet, ts32=None):
        """Build pcap frame from packet header and packet data.

        :param packet: packet data to be saved in a pcap file
        :param ts32: timestamp in microsecond
        """
        self.__packet = packet
        self.pktlen = len(packet)

        if ts32 is None:
            date = datetime.now()
            self.ts_sec = int(date.strftime("%s"))
            self.ts_usec = date.microsecond
        else:
            self.ts_sec = 0
            self.ts_usec = ts32

        self.__pcap_hdr = self.__build_packet_pcap_hdr()

        self.pcap_frame = self.__pcap_hdr + self.__packet

    def __build_packet_pcap_hdr(self):
        """Build the packet header string with timestamp and length info.

        :return: Packet header string
        """
        return struct.pack("<LLLL", self.ts_sec, self.ts_usec, self.pktlen, self.pktlen)

    def get_pcap_frame(self):
        """Return packet header string and packet string.

        :return: Packet header + packet string
        """
        return self.pcap_frame


class PcapDumper:
    """Helper class to create and write data to the pcap file."""

    def __init__(self, datalink, filename):
        """Open new pcap file as per name given.
        First writes Wireshark global header with Wireshark magic number,
        major, minor versions and datalink

        :param datalink : Wireshark datalink type
        :param filename : file name
        """

        self.__file = None

        # Check file name parameter is valid
        if filename is not None and isinstance(filename, str):
            self.__file = open(filename, mode="wb")
        else:
            raise ValueError("Unsupported argument type (filename)")

        # Save datalink
        self.datalink = datalink

        # Write global header
        if self.__file is not None:
            line = struct.pack(
                "IHHIIII",
                PCAPH_MAGIC_NUM_BE,
                PCAPH_VER_MAJOR,
                PCAPH_VER_MINOR,
                PCAPH_THISZONE,
                PCAPH_SIGFIGS,
                PCAPH_SNAPLEN,
                self.datalink,
            )
            self.__file.write(line)
            self.__file.flush()

    def write_to_pcapfile(self, pcapframe):
        """Write packet header and packet to pcap file.

        :param pcapframe: pcap frame including packet header and packet
        """

        self.__file.write(pcapframe)
        self.__file.flush()

    def close(self):
        """Close file if opened."""

        if self.__file is not None:
            self.__file.close()

    def __del__(self):
        self.close()


class PcapDumpReader:
    """Helper class to read packets from pcap file."""

    def __init__(self, pcapfile):
        """Opens pcap file for reading.
        Read wireshark global header
        Identify file endienness and read next bytes accordingly

        :param pcapfile: pcap file name to be rad from disk

        TODO: Test magic number for BE machine
        """
        self.__file = None

        # Open file for read only mode for binary data
        self.__file = open(pcapfile, mode="rb")

        # Read first pcap file header
        pcaphdr = self.__file.read(WIRESHARK_GLB_HDR_LEN)

        # Find the magic number
        pcap_magicnum = struct.unpack("I", pcaphdr[:4])[0]

        # Find endianness of file
        if sys.byteorder == SYS_LE_STR:

            if pcap_magicnum == PCAPH_MAGIC_NUM_BE:  # 0xa1b2c3d4
                # Little Endian file
                self.__endianness = "<"

            elif pcap_magicnum == PCAPH_MAGIC_NUM_LE:  # 0xd4c3b2a1
                # Big Endian file
                self.__endianness = ">"
            else:
                raise ValueError("invalid pcap magic number")

        elif sys.byteorder == SYS_BE_STR:

            if pcap_magicnum == PCAPH_MAGIC_NUM_BE:  # 0xa1b2c3d4
                # Big Endian file
                self.__endianness = ">"

            elif pcap_magicnum == PCAPH_MAGIC_NUM_LE:  # 0xd4c3b2a1
                # Little Endian file
                self.__endianness = "<"

            else:
                raise ValueError("invalid pcap magic number")

        # typedef struct pcap_hdr_s {
        #    guint32 magic_number;   /* magic number */
        #    guint16 version_major;  /* major version number */
        #    guint16 version_minor;  /* minor version number */
        #    gint32  thiszone;       /* GMT to local correction */
        #    guint32 sigfigs;        /* accuracy of timestamps */
        #    guint32 snaplen;        /* max length of captured packets, in octets */
        #    guint32 network;        /* data link type */
        # } pcap_hdr_t;

        pcap_hdr_t = ["", "", "", "", "", "", ""]
        pcap_hdr_t = struct.unpack("%sIHHIIII" % self.__endianness, pcaphdr)

        if pcap_hdr_t[1] != PCAPH_VER_MAJOR and pcap_hdr_t[2] != PCAPH_VER_MINOR:
            raise ValueError("Unsupported pcap file version")

        self._hdr_snaplen = pcap_hdr_t[5]
        self._hdr_datalink = pcap_hdr_t[6]

    def read_next_packet(self):
        """Read new packet from file.

        Validate packet length with packet header and return packet.

        :return: data packet
        """
        packet_header = self.__file.read(WIRESHARK_PKT_HDR_LEN)
        if not packet_header:
            return None

        # Wireshark Packet Header
        # hdr_unpack = typedef struct pcaprec_hdr_s {
        #    guint32 ts_sec;         /* timestamp seconds */
        #    guint32 ts_usec;        /* timestamp microseconds */
        #    guint32 incl_len;       /* number of octets of packet saved in file */
        #    guint32 orig_len;       /* actual length of packet */
        # } pcaprec_hdr_t;

        pcaprec_hdr_t = ["", "", "", ""]
        pcaprec_hdr_t = struct.unpack("%sIIII" % self.__endianness, packet_header)

        if (
            pcaprec_hdr_t[2] > pcaprec_hdr_t[3]
            or pcaprec_hdr_t[2] > self._hdr_snaplen
            or pcaprec_hdr_t[3] > self._hdr_snaplen
        ):
            raise ValueError("Invalid pcap packet header")

        # Header is valid, now read the packet with incl_len
        packet = self.__file.read(pcaprec_hdr_t[2])

        return packet

    def close(self):
        """Close file if open."""
        if self.__file is not None:
            self.__file.close()

    def __del__(self):
        """Delete the file."""
        self.close()
