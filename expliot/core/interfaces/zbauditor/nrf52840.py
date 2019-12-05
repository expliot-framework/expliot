"""nRF52840 usb driver."""
import array
import struct
import time

import usb.core
import usb.util

from expliot.core.interfaces.common_services import ZbAuditorServices


class NRF52840(ZbAuditorServices):
    """Driver for NRF52840 Zigbee Auditor Hardware."""

    USB_DIR_OUT = 0x40
    USB_DIR_IN = 0xC0
    USB_DATA_EP = 0x83

    # Vendor ID and Product code of Zigbee Auditor
    USB_VID = 0x1915
    USB_PID = 0x521A

    USB_READ_TIMEOUT_MIN = 100  # ms
    USB_READ_TIMEOUT_MAX = 2000  # ms

    USB_MAX_BYTE_READ = 64  # 64Bytes

    # Services
    SRV_GET_FW_VER = 0x01
    SRV_GET_FW_SRV = 0x02
    SRV_POWER_ON = 0x20
    SRV_GET_POWER_STATUS = 0x21
    SRV_SET_CHANNEL = 0x22
    SRV_SET_SNIFF_START = 0x23
    SRV_SET_SNIFF_STOP = 0x24
    SRV_SEND_PACKET_INJECT = 0x25
    SRV_ZB_NWKSCAN_REQ = 0x31

    # Response mask for service
    SERVICE_RESP_MASK = 0x80

    # Service response byte
    SRV_GET_FW_VER_RESP = SERVICE_RESP_MASK | SRV_GET_FW_VER
    SRV_GET_FW_SRV_RESP = SERVICE_RESP_MASK | SRV_GET_FW_SRV
    SRV_GET_POWER_STATUS_RESP = SERVICE_RESP_MASK | SRV_GET_POWER_STATUS
    SRV_ZB_NWKSCAN_RESP = SERVICE_RESP_MASK | SRV_ZB_NWKSCAN_REQ

    # Response len for services
    SRV_GET_FW_VER_RESP_LEN = 5
    SRV_GET_FW_SRV_RESP_LEN = 6
    SRV_ZB_NWKSCAN_RESP_MIN_LEN = 3
    SRV_ZB_NWKSCAN_RESP_DATA_LEN = 1

    # General service Data byte indexs
    SRV_RESP_BYTE_1 = 2
    SRV_RESP_BYTE_2 = 3
    SRV_RESP_BYTE_3 = 4
    SRV_RESP_BYTE_4 = 5

    # Network Discovery response position index
    SRV_ZB_NWKSCAN_RESP_LEN_INDEX = 1
    SRV_ZB_NWKSCAN_RESP_NUM_DEV_INDEX = 3

    # Network Discovery response Data size
    SRV_ZB_NWKSCAN_RESP_DEV_NUM_LEN = 1

    SRV_SET_CH_CHNG_BIT = 0x01
    SRV_RAW_CAPTURE_BIT = 0x02
    SRV_RAW_INJECT_BIT = 0x04
    SRV_NWK_SCAN_BIT = 0x08
    SRV_SUPP_FREQ_2400_BIT = 0x01

    # Service response status
    SERVICE_STATUS_OK = 0
    SERVICE_STATUS_END = 1

    # Service Response Data
    MAC_POWER_ON_STATUS = 0x01

    # IEEE 802.15.4 Channel and page
    MAC_24GHZ_CHANNEL_11 = 11
    MAC_24GHZ_CHANNEL_26 = 26

    MAC_24GHZ_DEFAULT_PAGE = 0x00

    # Start of frame byte for Sniffer response
    SOF_BYTE = 0x00

    # Zigbee Beacon Response packet length
    BEACON_INFO_LEN = 28

    # USB timeout error code
    USB_OPERATION_TIMEOUT = 110

    def __init__(self, channel=0, page=0):
        """Driver for NRF52840 based Zigbee Auditor Device.

        Search, initialized Zigbee Auditor Device and related driver
        Initialized flags related to driver
        Read supported services

        :param channel : 802.15.4 frequency channel
        :param page :  802.15.4 Page
        """
        super().__init__()

        self.__data_ep = self.USB_DATA_EP
        self.__channel = channel
        self.__page = page
        self.__radio_on = False
        self.__sniffer_on = False
        self.__fw_version = None
        self.rxcount = 0
        self.txcount = 0

        self.dev = usb.core.find(idVendor=self.USB_VID, idProduct=self.USB_PID)

        if self.dev is None:
            raise OSError("Device not found")

        # Must call this to establish the USB's "Config"
        self.dev.reset()
        self.dev.set_configuration()

        self._dev_name = usb.util.get_string(self.dev, self.dev.iProduct)

        # Get wMaxPacketSize from the data endpoint
        for cfg in self.dev:
            for intf in cfg:
                for endpoint in intf:
                    if endpoint.bEndpointAddress == self.__data_ep:
                        self._maxpacketsize = endpoint.wMaxPacketSize

        self.read_supported_service()

    def get_device_fw_rev(self):
        """Read and validate response to GET Firmware Revision Service.

        :return: Firmware version array (3 bytes)
        """
        pdata = self.usb_cntrl_read(
            self.SRV_GET_FW_VER, data_or_wlength=self.SRV_GET_FW_VER_RESP_LEN
        )

        if (
            len(pdata) == self.SRV_GET_FW_VER_RESP_LEN
            and pdata[0] == self.SRV_GET_FW_VER_RESP
        ):
            self.set_base_serivce(self.GET_FW_REV, True)
            return pdata[2:]

        raise NotImplementedError("Invalid response for Get FW Version")

    def get_device_fw_rev_str(self):
        """"Return firmware revision in string format."""
        ver = self.get_device_fw_rev()
        self.__fw_version = str(ver[0]) + "." + str(ver[1]) + "." + str(ver[2])

        return self.__fw_version

    def read_supported_service(self):
        """Read and validate response to GET Firmware Capability Service.

        :return: Firmware Capability
        """
        resp = self.usb_cntrl_read(self.SRV_GET_FW_SRV, data_or_wlength=6)

        if (
            len(resp) == self.SRV_GET_FW_SRV_RESP_LEN
            and resp[0] == self.SRV_GET_FW_SRV_RESP
        ):

            self.set_base_serivce(self.GET_FW_SERV, True)

            self.set_device_serivce(self.SET_MAC_POWER, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_SET_CH_CHNG_BIT:
                self.set_device_serivce(self.SET_CH_CHNG, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_RAW_CAPTURE_BIT:
                self.set_device_serivce(self.RAW_CAPTURE, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_RAW_INJECT_BIT:
                self.set_device_serivce(self.RAW_INJECT, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_NWK_SCAN_BIT:
                self.set_device_serivce(self.NWK_SCAN, True)

            if resp[self.SRV_RESP_BYTE_1] & self.SRV_SUPP_FREQ_2400_BIT:
                self.set_device_serivce(self.SUPP_FREQ_2400, True)

            return self.get_supported_services()

        raise ValueError("Invalid response for Get Services")

    def _device_set_channel(self):
        """Set the channel in the device MAC hardware."""
        # Note: Check is radio is On and Sniffing is OFF before calling this function
        self.usb_cntrl_write(
            self.SRV_SET_CHANNEL, windex=0, data_or_wlength=[self.__channel]
        )

        self.usb_cntrl_write(
            self.SRV_SET_CHANNEL,
            windex=1,
            data_or_wlength=[self.MAC_24GHZ_DEFAULT_PAGE],
        )

    def device_set_channel(self, channel, page=0):
        """Set channel locally and of device hardware."""

        # Check set channel service is supported
        if not self.is_service_active(self.SET_CH_CHNG):
            raise NotImplementedError("Service not implemented")

        if not (
            channel < self.MAC_24GHZ_CHANNEL_11 or channel > self.MAC_24GHZ_CHANNEL_26
        ):

            self.__channel = channel

            if page:
                raise ValueError("SubGHz not supported")

            # set page if it is zero
            self.__page = page

            if self.__radio_on:
                if self.__sniffer_on:
                    self.usb_cntrl_write(self.SRV_SET_SNIFF_STOP)
                    self._device_set_channel()
                    self.usb_cntrl_write(self.SRV_SET_SNIFF_START)
                else:
                    self._device_set_channel()
            else:
                raise RuntimeError("Radio is Off")
        else:
            raise ValueError("Invalid Channel")

    def device_radio_on(self):
        """Turn on radio and MAC layer."""
        # Check raw packet inject service is supported
        if not self.is_service_active(self.SET_MAC_POWER):
            raise NotImplementedError("Service not active")

        if not self.__radio_on:
            # Turn on Radio
            self.usb_cntrl_write(self.SRV_POWER_ON, windex=4)

            while True:
                # Check if radio is powered up
                status = self.usb_cntrl_read(
                    self.SRV_GET_POWER_STATUS, data_or_wlength=3
                )

                if status[self.SRV_RESP_BYTE_1] == self.MAC_POWER_ON_STATUS:
                    self.__radio_on = True
                    break
                time.sleep(0.1)

    def device_sniffer_on(self, channel=None, page=0):
        """Start sniffer service."""
        # Check packet capture service is supported
        if not self.is_service_active(self.RAW_CAPTURE):
            raise NotImplementedError("Service not active")

        if not self.__radio_on:
            self.device_radio_on()

        self.device_set_channel(channel, page)

        if not self.__sniffer_on:
            # Start capture
            self.usb_cntrl_write(self.SRV_SET_SNIFF_START)
            self.__sniffer_on = True

    @staticmethod
    def calculate_crc(data):
        """Return CRC of data.

        CRC algorithm implementation is based on pseudo code from
        Frank da Cruz (June 1986), Kermit Protocol Manual, Sixth Edition
        Refer: http://reveng.sourceforge.net/crc-catalogue/16.htm#crc.cat.crc-16-kermit

        :return: a CRC that is the FCS for the frame, as two hex bytes in little-endian order.
        """
        crc = 0
        for i, dummy in enumerate(data):
            tmp = data[i]
            quot = (crc ^ tmp) & 15  # Do low-order 4 bits
            crc = (crc // 16) ^ (quot * 4225)
            quot = (crc ^ (tmp // 16)) & 15  # And high 4 bits
            crc = (crc // 16) ^ (quot * 4225)
        return struct.pack("<H", crc)  # return as bytes in little endian order

    def _process_sniffer_response(self, rxframe):
        """Return dictionary of Zigbee packet and timestamp.

        :param array: Frame data array
        :return: dictionary {"packet": zbpacket, "timestamp": 32bit timestamp}
        """
        # Get Start of Frame byte & encap len
        # Start of Frame @ 0th byte = 00
        # Frame Length @ 1st byte of frame
        # Frame Length = Zigbee packet len + 5
        (sof_byte, encap_len) = struct.unpack_from("<BH", rxframe)

        if self.SOF_BYTE != sof_byte:
            return None

        # Ignore first 3 bytes, read reamining bytes
        pktstream = array.array("B", rxframe[3:])
        if len(pktstream) == encap_len:

            # IEEE 802.15.4 Packet Length @ 7st byte of frame
            (timestamp, payloadlen) = struct.unpack_from("IB", pktstream)

            # Get Zigbee packet from 8th bytes on word
            payload = pktstream[5:]

            if len(payload) != payloadlen:
                return None

            # Last byte of mac payload is CRC OK MASK (0x80) & LQI
            crc_lqi = payload[-1]
            if (crc_lqi & 0x80) == 0x80:
                packet = payload[:-2]
                crc = self.calculate_crc(payload[:-2])
                for byte in crc:
                    packet.append(byte)
            else:
                packet = payload

            # Now we have valid packet
            ret = {"packet": packet.tostring(), "timestamp": timestamp}
            return ret

    def device_read(self, timeout=100):
        """Read packet from USB interface.

        If Zigbee packet length is less than 56 bytes process the packet
        If Zigbee packet length is more than 56 bytes, waits for next chunk

        :param timeout: Time out for read operation
        :return: Zigbee packet and timestamp as {"packet": packet, "timestamp": timestamp (32bit) }
        """

        if not self.__sniffer_on:
            self.device_sniffer_on(self.__channel)  # start sniffing

        rxframe = array.array("B")

        while True:
            frame_chunk = None  # This will receive chunk of 64 bytes
            try:
                frame_chunk = self.usb_read(
                    size_or_buffer=self._maxpacketsize, timeout=timeout
                )

            except usb.core.USBError as err:
                # Raise exceptions other than time out
                if err.errno != self.USB_OPERATION_TIMEOUT:  # Not Timeout error
                    raise err

                return None

            for byte in frame_chunk:
                rxframe.append(byte)

            # Valid frame should be 64 bytes or less
            if len(frame_chunk) <= self.USB_MAX_BYTE_READ:

                # Need minimum 3 bytes to get frame len
                if len(rxframe) >= 3:

                    # Get Start of Frame byte & encap len
                    # Start of Frame @ 0th byte = 00
                    # Frame Length @ 1st byte of frame
                    # Frame Length = Zigbee packet len + 5
                    (sof_byte, encap_len) = struct.unpack_from("<BH", rxframe)

                    # Expected frame len would be encap len + 3 bytes
                    expectetd_frame_len = encap_len + 3

                    # Chk for valid SOF
                    if self.SOF_BYTE == sof_byte:

                        # Handle Zigbee packet greater than 56 byte long
                        if expectetd_frame_len > len(rxframe):
                            # Go back and wait for next chunk of frame
                            # "Warrning: zigbee len {} > {} bytes, wait for next chunk.."
                            # .format((encap_len - 5), len(frame_chunk)))
                            continue

                        ret = self._process_sniffer_response(rxframe)
                        self.rxcount += 1
                        return ret
            else:
                raise BufferError("Frame length greater than 64")

    def process_scan_response(self, response):
        """Return dictionary of number of deivces found in scan
        and device zigbee beacon info.

        :param array: Frame data array
        :return: Result of Network scan as {"Device Count": 1, "Beacons": [{ ... }]}
        """
        numdevices = response[0]
        framedata = response[1:]

        beacon_list = list()
        offset = 0

        # Parsed device info
        for i in range(numdevices):
            offset = i * self.BEACON_INFO_LEN
            beacondata = array.array(
                "B", framedata[offset : offset + self.BEACON_INFO_LEN]
            )

            data_list = ["", "", "", "", "", "", "", "", "", "", "", [], "", "", ""]
            data_list = struct.unpack_from("<HHBBBBBBBBBB8sIbB", beacondata)

            extnpanid = []
            beacon = dict()
            beacon["source_addr"] = hex(data_list[0])
            beacon["source_panid"] = hex(data_list[1])
            beacon["channel"] = data_list[2]
            beacon["pan_coordinator"] = bool(data_list[3])
            beacon["permit_joining"] = bool(data_list[4])

            beacon["zigbee_layer"] = bool(data_list[5])

            if bool(data_list[5]):
                zigbeeinfo = dict()
                zigbeeinfo["router_capacity"] = bool(data_list[6])
                zigbeeinfo["device_capacity"] = bool(data_list[7])
                zigbeeinfo["protocol_version"] = data_list[8]
                zigbeeinfo["stack_profile"] = data_list[9]

                zigbeeinfo["depth"] = data_list[10]
                zigbeeinfo["update_id"] = data_list[11]

                # Conver extended PANID to big-endiean format
                extnpanid.append(hex(data_list[12][7]))
                extnpanid.append(hex(data_list[12][6]))
                extnpanid.append(hex(data_list[12][5]))
                extnpanid.append(hex(data_list[12][4]))
                extnpanid.append(hex(data_list[12][3]))
                extnpanid.append(hex(data_list[12][2]))
                extnpanid.append(hex(data_list[12][1]))
                extnpanid.append(hex(data_list[12][0]))
                zigbeeinfo["extn_panid"] = extnpanid
                zigbeeinfo["tx_offset"] = hex(data_list[13])

                beacon.update(zigbeeinfo)

            beacon["rssi"] = data_list[14]
            beacon["lqi"] = data_list[15]

            # Append beacon to beacon list
            beacon_list.append(beacon)

        nwk_data = dict()
        nwk_data["device_count"] = numdevices
        nwk_data["beacons"] = beacon_list
        return nwk_data

    def device_scan_zigbee_network(self, mask=0x07FFF800):
        """Set device in IEEE802.15.4 network scan mode.

        Also, the IEEE 802.15.4 channels are scan for beacon and data

        :param mask: channel mask, channel 25 => 0x07000000 .. channel 11 => 0x00000800
        :return: network scan data
        """
        # Check network scan service is supported
        if not self.is_service_active(self.NWK_SCAN):
            raise NotImplementedError("Service not active")

        # Turn ON Radio
        if not self.__radio_on:
            self.device_radio_on()

        # Convert int to bytes array, pyusb receives bytes only
        mask_bytes = mask.to_bytes(4, byteorder="big", signed=False)

        # Send Network Scan command
        self.usb_cntrl_write(self.SRV_ZB_NWKSCAN_REQ, 0, 0, data_or_wlength=mask_bytes)

        # Read network scan data
        scan_resp = []
        dev_data_len = 0
        data_len = 0
        while True:
            pdata = None
            try:
                pdata = self.usb_read(
                    size_or_buffer=self._maxpacketsize,
                    timeout=self.USB_READ_TIMEOUT_MIN,
                )
            # Raise exceptions other than timeout
            except usb.core.USBError as err:
                if err.errno != self.USB_OPERATION_TIMEOUT:  # not timed out
                    raise err

                continue

            if len(pdata) == self.SRV_ZB_NWKSCAN_RESP_MIN_LEN:
                (service, data_len, status) = struct.unpack_from("<BBB", pdata)

                # Check returned data is command response
                if service == self.SRV_ZB_NWKSCAN_RESP:
                    if data_len == self.SRV_ZB_NWKSCAN_RESP_DATA_LEN:
                        # If response is 3 byte then it must be scan start or end
                        if status == self.SERVICE_STATUS_OK:
                            continue

                        if status == self.SERVICE_STATUS_END:

                            # Turn OFF radio
                            self.device_radio_off()

                            # Network Scan finished, Process response data
                            if (
                                len(scan_resp)
                                == dev_data_len + self.SRV_ZB_NWKSCAN_RESP_MIN_LEN
                            ):
                                ret = self.process_scan_response(scan_resp[3:])
                                return ret
                            return None

            # Response length is not three then its data packet
            for byteval in pdata:
                scan_resp.append(byteval)

            # we need 4 bytes to confirm scan response
            if len(scan_resp) > 4:
                data_len = scan_resp[self.SRV_ZB_NWKSCAN_RESP_LEN_INDEX]
                numdev = scan_resp[self.SRV_ZB_NWKSCAN_RESP_NUM_DEV_INDEX]

                dev_data_len = (
                    numdev * self.BEACON_INFO_LEN
                ) + self.SRV_ZB_NWKSCAN_RESP_DEV_NUM_LEN

            if len(scan_resp) < dev_data_len + self.SRV_ZB_NWKSCAN_RESP_MIN_LEN:
                continue

            continue

    def device_inject_packet(self, packet):
        """Inject packet too device.

        :param packet: byte array
        """

        # Check raw packet inject service is supported
        if not self.is_service_active(self.RAW_INJECT):
            raise NotImplementedError("Service not active")

        # Append two bytes to be replaced with FCS by firmware.
        # packet += b"\x00\x00"
        self.usb_cntrl_write(self.SRV_SEND_PACKET_INJECT, 0, 0, data_or_wlength=packet)
        self.txcount += 1

    def device_sniffer_off(self):
        """Turn off sniffer service."""
        if self.__sniffer_on:
            self.usb_cntrl_write(self.SRV_SET_SNIFF_STOP)
            self.__sniffer_on = False

    def device_radio_off(self):
        """Turn off sniffer and radio."""
        # First stop sniffer
        self.device_sniffer_off()

        # Turn off radio & MAC
        if self.__radio_on:
            self.usb_cntrl_write(self.SRV_POWER_ON, windex=0)
            self.__radio_on = False

    def usb_cntrl_read(
        self, brequest, wvalue=0, windex=0, data_or_wlength=None, timeout=100
    ):
        """USB Control Transfer, EP0 DIR IN.

        :param brequest: usb bRequest
        :param wvalue: usb wValue
        :param windex: usb wIndex
        :param data_or_wlength: usb data to be write
        :param timeout: timeout for write transaction
        :return: bytes read from driver (array object)
        """
        return self.dev.ctrl_transfer(
            self.USB_DIR_IN,
            bRequest=brequest,
            wValue=wvalue,
            wIndex=windex,
            data_or_wLength=data_or_wlength,
            timeout=timeout,
        )

    def usb_cntrl_write(
        self, brequest, wvalue=0, windex=0, data_or_wlength=None, timeout=200
    ):
        """USB Control Transfer, EP0 DIR OUT.

        :param brequest: usb bRequest
        :param wvalue: usb wValue
        :param windex: usb wIndex
        :param data_or_wlength: usb data to be write
        :param timeout: timeout for write transaction
        :return: number of bytes written
        """
        return self.dev.ctrl_transfer(
            self.USB_DIR_OUT,
            bRequest=brequest,
            wValue=wvalue,
            wIndex=windex,
            data_or_wLength=data_or_wlength,
            timeout=timeout,
        )

    def usb_read(self, size_or_buffer, timeout=200):
        """USB Bulk read for EP3.

        :param size_or_buffer: data buffer or size to be read
        :param timeout: Timeout for read transaction
        :return: bytes read from driver (array object)
        """
        return self.dev.read(self.__data_ep, size_or_buffer, timeout)

    def get_device_name(self):
        """Return the device name."""
        return self._dev_name

    def get_radio_on_flag(self):
        """Returns radio_on flag value."""

        return self.__radio_on

    def set_radio_on_flag(self, flag):
        """Set radio_on flag value.

        :param flag: True or False
        """
        self.__radio_on = flag

    def get_sniffer_on_flag(self):
        """Return the sniffer_on flag value."""
        return self.__sniffer_on

    def set_sniffer_on_flag(self, flag):
        """Set sniffer_on flag value."""
        self.__sniffer_on = flag

    def close(self):
        """Turn off sniffer and radio before closing."""
        self.device_radio_off()

    def __del__(self):
        """Close device."""
        self.close()
