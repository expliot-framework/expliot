"""Utility for ZB Auditor class."""

# from struct import pack


# def calculate_crc(data):
#     """Returns CRC of data
#     CRC algorithm implementation is based on pseudo code from
#     Frank da Cruz (June 1986), Kermit Protocol Manual, Sixth Edition
#     Refer: http://reveng.sourceforge.net/crc-catalogue/16.htm#crc.cat.crc-16-kermit

#     :return: a CRC that is the FCS for the frame, as two hex bytes in little-endian order.
#     """

#     crc = 0
#     for i, dummy in enumerate(data):
#         tmp = data[i]
#         quot = (crc ^ tmp) & 15				# Do low-order 4 bits
#         crc = (crc // 16) ^ (quot * 4225)
#         quot = (crc ^ (tmp // 16)) & 15		# And high 4 bits
#         crc = (crc // 16) ^ (quot * 4225)
#     return pack('<H', crc)                  # return as bytes in little endian order
