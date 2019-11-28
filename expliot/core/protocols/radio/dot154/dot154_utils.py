"""IEEE 802.15.4 Protocol support."""
import struct

MAC_FC_FTYPE_MASK = 0x0007
MAC_FC_FTYPE_BEACON = 0
MAC_FC_FTYPE_DATA = 1
MAC_FC_FTYPE_ACK = 2
MAC_FC_FTYPE_CMD = 3

DEST_ADDR_MODE_MASK = 0x0C00
SRC_ADDR_MODE_MASK = 0xC000

DEST_ADDR_MODE_SHORT = 0x0800
DEST_ADDR_MODE_LONG = 0x0C00


def is_beacon_packet(packet):
    """Return true if Frame type is BEACON.

    :param packet: Zigbee packet
    :return bool: True if packet is BEACON else False
    """
    fctype = struct.unpack("H", packet[0:2])[0]
    if (fctype & MAC_FC_FTYPE_MASK) == MAC_FC_FTYPE_BEACON:
        return True
    return False


def is_ack_packet(packet):
    """Return true if Frame type is ACK.

    :param packet: Zigbee packet
    :return bool: True if packet is ACK else False
    """
    fctype = struct.unpack("H", packet[0:2])[0]
    if (fctype & MAC_FC_FTYPE_MASK) == MAC_FC_FTYPE_ACK:
        return True
    return False


def is_data_packet(packet):
    """Return true if Frame type is DATA.

    :param packet: Zigbee packet
    :return bool: True if packet is DATA else False
    """
    fctype = struct.unpack("H", packet[0:2])[0]
    if (fctype & MAC_FC_FTYPE_MASK) == MAC_FC_FTYPE_DATA:
        return True
    return False


def is_cmd_packet(packet):
    """Return true if Frame type is CMD.

    :param packet: Zigbee packet
    :return bool: True if packet is CMD else False
    """
    fctype = struct.unpack("H", packet[0:2])[0]
    if (fctype & MAC_FC_FTYPE_MASK) == MAC_FC_FTYPE_CMD:
        return True
    return False


def get_dst_pan_from_packet(packet):
    """Return Destination PAN from data or command packets

    :param packet: Zigbee packet
    :return int: Destination PAN address
    """
    cntl_field = struct.unpack("H", packet[:2])[0]

    if (cntl_field & MAC_FC_FTYPE_MASK) == MAC_FC_FTYPE_DATA or (
        cntl_field & MAC_FC_FTYPE_MASK
    ) == MAC_FC_FTYPE_CMD:
        if (cntl_field & DEST_ADDR_MODE_MASK) == DEST_ADDR_MODE_SHORT or (
            cntl_field & DEST_ADDR_MODE_MASK
        ) == DEST_ADDR_MODE_LONG:
            return struct.unpack("<HBH", packet[:5])[2]
    return None
