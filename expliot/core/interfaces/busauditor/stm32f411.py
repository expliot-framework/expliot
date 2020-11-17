"""STM32F411 usb driver."""
import struct
import time
import usb.core
import usb.util
from expliot.core.interfaces.common_services import BusAuditorServices


class STM32F411(BusAuditorServices):
    """
    Driver for STM32F411 BusAuditor Hardware.
    Search, initialized BusAuditor Device and related driver
    Initialized flags related to driver
    Read FW, HW revisions and supported services
    """

    # USB EP for Bud Auditor
    USB_DIR_OUT = 0x40
    USB_DIR_IN = 0xC0
    USB_DATA_EP = 0x81

    # Vendor ID and Product code of BusAuditor
    USB_VID = 0x0483
    USB_PID = 0xBA20

    # USB timeout error code
    USB_OP_TIMEOUT_ERROR = 110

    # Bus Auditor services
    SRV_GET_REVISIONS = 0x01
    SRV_GET_SERVICES = 0x02

    SRV_JTAG_IDCODE_SCAN = 0x11
    SRV_JTAG_PATTERN_SCAN = 0x12
    SRV_JTAG_IDCODE_TRST_SCAN = 0x13
    SRV_JTAG_PATTERN_TRST_SCAN = 0x14

    SRV_SWD_IDCODE_SCAN = 0x1B

    SRV_UART_TX_SCAN = 0x21
    SRV_UART_TX_RX_SCAN = 0x22

    SRV_I2C_ADDR_SCAN = 0x23
    SRV_SPI_SCAN = 0x24

    # Response mask for service
    SERVICE_RESP_BIT = 0x80

    # Service response byte
    SRV_GET_REVISIONS_RESP = SERVICE_RESP_BIT | SRV_GET_REVISIONS       # 0x81
    SRV_GET_SERVICES_RESP = SERVICE_RESP_BIT | SRV_GET_SERVICES         # 0x82

    # Service Resp data lengths
    SRV_GET_REVISIONS_RESP_LEN = 8
    SRV_GET_SERVICES_RESP_LEN = 7

    # Supported service bits
    SRV_JTAG_SCAN_BIT = 0x01
    SRV_SWD_SCAN_BIT = 0x02

    SRV_UART_SCAN_BIT = 0x10
    SRV_I2C_SCAN_BIT = 0x20
    SRV_SPI_SCAN_BIT = 0x10

    # Service byte indexes
    SRV_RESP_BYTE_1 = 3
    SRV_RESP_BYTE_2 = 4
    SRV_RESP_BYTE_3 = 5
    SRV_RESP_BYTE_4 = 6

    # Service Error codes
    _srv_err = [
        "No error",
        "Service error",
        "Device busy",
        "Same start and end channel",
        "Invalid start channel",
        "Invalid end channel",
        "Invalid start and end channel",
        "Insufficient channel count",
        "Invalid target voltage value",
        "Application error",
    ]

    def __init__(self):
        """
        Constructor: Driver for STM32F411 based BusAuditor Device.

        Args:
            Nothing
        Returns:
            Nothing
        Raises:
            OSError("Device not found")
        """

        super().__init__()

        self.__data_ep = self.USB_DATA_EP
        self.__fw_version = None
        self.__hw_version = None
        self.__serial_num = None
        self.__maxpacketsize = 64        # default USB packet size

        self.dev = usb.core.find(
            idVendor=self.USB_VID,
            idProduct=self.USB_PID
        )

        if self.dev is None:
            raise OSError("Device not found")

        # Must call this to establish the USB's "Config"
        self.dev.reset()
        self.dev.set_configuration()

        self.__dev_name = usb.util.get_string(self.dev, self.dev.iProduct)
        self.__serial_num = self.dev.serial_number

        # Get wMaxPacketSize from the data endpoint
        for cfg in self.dev:
            for intf in cfg:
                for endpoint in intf:
                    if endpoint.bEndpointAddress == self.__data_ep:
                        self.__maxpacketsize = endpoint.wMaxPacketSize

        self.get_device_revisions()
        self.read_supported_service()

    def get_device_revisions(self):
        """
        Read Firmware and Hardware revision by Get Revision Service.
        This method save FW and HW revision for BusAuditor instance
        Args:
            Nothing
        Returns:
            byte array: Five bytes of fw and hw revision,
                        [FW_MAJOR, FW_MINOR, FW_SUNMINOR, HW_MAJOR, HW_MINOR]
        Raises:
            NotImplementedError("Invalid response for Get FW Version")
        """

        pdata = self.usb_cntrl_read(
            self.SRV_GET_REVISIONS,
            data_or_wlength=self.SRV_GET_REVISIONS_RESP_LEN
        )

        if (
            len(pdata) == self.SRV_GET_REVISIONS_RESP_LEN
            and pdata[0] == self.SRV_GET_REVISIONS_RESP
        ):
            self.set_base_serivce(self.GET_FW_REV, True)
            ver = pdata[3:]
            self.__fw_version = str(ver[0]) + "." + str(ver[1]) + "." + str(ver[2])
            self.__hw_version = str(ver[3]) + "." + str(ver[4])
            return pdata[3:]

        raise NotImplementedError("Invalid response for Get FW version")

    def read_supported_service(self):
        """
        Read services supported by BusAuditor hardware, and
        stores supported services info for service validation

        Args:
            Nothing
        Returns:
            Nothing
        Raises:
            ValueError("Invalid response for Get Services")
        """

        resp = self.usb_cntrl_read(
            self.SRV_GET_SERVICES,
            data_or_wlength=self.SRV_GET_SERVICES_RESP_LEN
        )

        if (
            len(resp) == self.SRV_GET_SERVICES_RESP_LEN
            and resp[0] == self.SRV_GET_SERVICES_RESP
        ):
            self.set_base_serivce(self.GET_FW_SERV, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_JTAG_SCAN_BIT:
                self.set_device_serivce(self.JTAG_SCAN, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_SWD_SCAN_BIT:
                self.set_device_serivce(self.SWD_SCAN, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_UART_SCAN_BIT:
                self.set_device_serivce(self.UART_SCAN, True)

            if resp[self.SRV_RESP_BYTE_4] & self.SRV_I2C_SCAN_BIT:
                self.set_device_serivce(self.I2C_SCAN, True)

            return self.get_supported_services()

        raise ValueError("Invalid response for Get services")

    @staticmethod
    def __build_jtag_idcode_dict(resp_array, include_trst=False):
        """
        Build JTAG idcode list from idcode scan response array

        Args:
            resp_array (byte array): Jtag idcode scan service response
            from BusAuditor
        Returns:
            list: List of device ID code and corresponding JTAG pins
        Raises:
            Nothing
        """

        idcode_array = []

        for resp in resp_array:

            data_len = resp[1] - 1
            data = resp[3:]

            # When TRST included in scan, data represent as below:
            # data = device_count (1byte)
            #       + trst (1byte) + tck (1byte) + tms (1byte)
            #       + tdo (1byte) + tdi (1byte)
            #       + device_count * idcode (4byte)
            #
            # When TRST not included in scan, data represent as below:
            # data = device_count (1byte)
            #       +tck (1byte) + tms (1byte) + tdo (1byte) + tdi (1byte)
            #       + device_count * idcode (4byte)

            if len(data) != data_len:
                continue

            idcode_dict = dict()
            idcode_dict["count"] = data[0]
            pin_dict = dict()
            if include_trst:
                pin_dict["trst"] = data[1]
                pin_dict["tck"] = data[2]
                pin_dict["tms"] = data[3]
                pin_dict["tdo"] = data[4]
                pin_dict["tdi"] = data[5]
                idcodes = data[6:]
            else:
                pin_dict["tck"] = data[1]
                pin_dict["tms"] = data[2]
                pin_dict["tdo"] = data[3]
                pin_dict["tdi"] = data[4]
                idcodes = data[5:]

            idcode_dict["pins"] = pin_dict

            idcodes_num = len(idcodes) / 4
            if idcode_dict["count"] != idcodes_num:
                continue

            code_array = []
            for indx in range(idcode_dict["count"]):
                s_id = indx * 4
                e_id = s_id + 4
                idcode = idcodes[s_id:e_id]
                code_list = ["", ]
                code_list = struct.unpack_from("<I", idcode)
                code_array.append(int(code_list[0]))

            idcode_dict["idcodes"] = code_array
            idcode_array.append(idcode_dict)
        return idcode_array

    def device_jtag_idcode_scan(self, start, end, volts, include_trst=False):
        """
        Send request for JTAG pattern scan, TRST pin not included.

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out
        Returns:
            list: List of device ID code and corresponding JTAG Pins
        Raises:
            Nothing
        """

        # Target voltage is split in to digit str and fraction str
        (digitstr, fractstr) = volts.rstrip().split(".")

        # create sevice data as an array of
        # [start, end, int(digitstr), int(fractstr)]
        indata = [start, end, int(digitstr), int(fractstr)]

        if include_trst:
            service = self.SRV_JTAG_IDCODE_TRST_SCAN
        else:
            service = self.SRV_JTAG_IDCODE_SCAN

        self.usb_cntrl_write(
            brequest=service,
            wvalue=0, windex=0,
            data_or_wlength=indata
        )

        resp_array = self.__read_service_response(service)
        if resp_array:
            return self.__build_jtag_idcode_dict(resp_array, include_trst)
        return None

    @staticmethod
    def __build_jtag_patten_dict(resp_array, include_trst=False):
        """
        Build JTAG pin dict from pattern scan response array

        Args:
            resp_array (byte array): Jtag pattern scan service response
            from BusAuditor
        Returns:
            dict: dict of JTAG pins on which pattern found
            and dict of active pins where pattern not found but pins are active
        Raises:
            Nothing
        """

        pattern_dict = dict()
        matched_list = []
        active_list = []

        for resp in resp_array:
            data_len = resp[1] - 1
            data = resp[3:]

            # When TRST included in scan, data represent as below:
            # data = found/active (1byte)
            #       + trst (1byte) + tck (1byte) + tms (1byte)
            #       + tdo (1byte) + tdi (1byte)
            #       + pattern_matchcount

            # # When TRST not included in scan, data represent as below:
            # data = found/active (1byte)
            #       + tck (1byte) + tms (1byte) + tdo (1byte) + tdi (1byte)
            #       + pattern_matchcount

            if len(data) != data_len:
                continue

            idcode_dict = dict()
            if include_trst:
                if data[0] == 1:
                    idcode_dict["trst"] = data[1]
                    idcode_dict["tck"] = data[2]
                    idcode_dict["tms"] = data[3]
                    idcode_dict["tdo"] = data[4]
                    idcode_dict["tdi"] = data[5]
                    matched_list.append(idcode_dict)
                else:
                    idcode_dict["trst"] = data[1]
                    idcode_dict["tck"] = data[2]
                    idcode_dict["tms"] = data[3]
                    idcode_dict["tdo"] = data[4]
                    idcode_dict["tdi"] = data[5]
                    active_list.append(idcode_dict)
            else:
                if data[0] == 1:
                    idcode_dict["tck"] = data[1]
                    idcode_dict["tms"] = data[2]
                    idcode_dict["tdo"] = data[3]
                    idcode_dict["tdi"] = data[4]
                    matched_list.append(idcode_dict)
                else:
                    idcode_dict["tck"] = data[1]
                    idcode_dict["tms"] = data[2]
                    idcode_dict["tdo"] = data[3]
                    idcode_dict["tdi"] = data[4]
                    active_list.append(idcode_dict)

        pattern_dict["matched"] = matched_list
        pattern_dict["active"] = active_list
        return pattern_dict

    def device_jtag_pattern_scan(self, start, end, volts, include_trst=False):
        """
        Send request for JTAG pattern scan, TRST pin not included.

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out
        Returns:
            dict: dict of JTAG pins on which pattern found
            and dict of active pins where pattern not found but pins are active
        Raises:
            Nothing
        """

        # Target voltage is split in to digit str and fraction str
        (digitstr, fractstr) = volts.rstrip().split(".")

        # create sevice data as an array of
        # [start, end, int(digitstr), int(fractstr)]
        indata = [start, end, int(digitstr), int(fractstr)]

        if include_trst:
            service = self.SRV_JTAG_PATTERN_TRST_SCAN
        else:
            service = self.SRV_JTAG_PATTERN_SCAN

        self.usb_cntrl_write(
            brequest=service,
            wvalue=0, windex=0,
            data_or_wlength=indata
        )

        resp_array = self.__read_service_response(service)
        if resp_array:
            return self.__build_jtag_patten_dict(resp_array, include_trst)
        return None

    @staticmethod
    def __extract_jtag_idcode_pins_data(idcode_list, pattern_dict):
        """
        This method compares matched pins from pattern_dict to pins from
        idcode_list and build idcode list for JTAG devices from idcode_list.

        Args:
            idcode_list (list): List of ID code and corresponding JTAG pins
            pattern_dict (dict): Dict of Matched and Active pins
        Returns:
            dict: dict of JTAG device ID code and JTAG pins
        Raises:
            Nothing
        """

        tmp_id_list = []
        device_list = []

        matched_list = pattern_dict["matched"]
        if len(matched_list) == 0:
            return None

        for _, pvalue in enumerate(matched_list):
            for _, ivalue in enumerate(idcode_list):
                id_scan_pins = ivalue["pins"]
                if pvalue == id_scan_pins:
                    tmp_id_list.append(ivalue)

        if len(tmp_id_list) == 0:
            return None

        for _, value in enumerate(tmp_id_list):
            idcodes = value["idcodes"]
            for _, idcode in enumerate(idcodes):
                device_dict = dict()
                device_dict["jtag_idcode"] = "0x{:08x}".format(idcode)
                device_dict["pins"] = value["pins"]
                device_list.append(device_dict)

        return device_list

    def device_jtag_scan(self, start, end, volts, include_trst=False):
        """
        This method initiates JTAG ID code scan and followed by Pattern scan

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out
            include_trst (boolean): Include trst pin in scan.
                                    trst pin excluded by default

        Returns:
            dict: dict of JTAG device ID code and JTAG pins
        Raises:
            Nothing
        """

        idcode_list = self.device_jtag_idcode_scan(
            start,
            end,
            volts,
            include_trst
        )

        time.sleep(2)

        pattern_dict = self.device_jtag_pattern_scan(
            start,
            end,
            volts,
            include_trst
        )

        # Extract ID code and jtag pin info:
        if idcode_list and pattern_dict:
            return self.__extract_jtag_idcode_pins_data(
                idcode_list,
                pattern_dict
            )
        return None

    @staticmethod
    def __build_swd_idcode_dict(resp_array):
        """
        Build SWD idcode dict from swd scan response array

        Args:
            resp_array (byte array): SWD idcode scan service response
                from BusAuditor

        Returns:
            dict: dict of SWD device ID code and SWD pins
        Raises:
            Nothing
        """

        idcode_dist = dict()
        for resp in resp_array:
            data = resp[3:]
            data_len = resp[1] - 1

            # data represent as below:
            # data = swclk (1byte) + swdio (1byte) + idcode (4bytes)

            if len(data) != data_len:
                return None

            code_list = ["", ]
            code_list = struct.unpack_from("<I", data[2:6])

            idcode = int(code_list[0])
            if idcode not in idcode_dist:
                idcode_dist.update(
                    {
                        idcode: {"swclk": data[0], "swdio": data[1]}
                    }
                )

        device_list = []
        for idcode, value in idcode_dist.items():
            device_dict = dict()
            device_dict["swd_idcode"] = "0x{:08x}".format(idcode)
            device_dict["pins"] = value
            device_list.append(device_dict)
        return device_list

    def device_swd_scan(self, start, end, volts):
        """
        This method initiates SWD ID code scan to find SWD pins

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Returns:
            dict: dict of SWD device ID code and SWD pins
        Raises:
            Nothing
        """

        # Target voltage is split in to digit str and fraction str
        (digitstr, fractstr) = volts.rstrip().split(".")

        # create sevice data as an array of
        # [start, end, int(digitstr), int(fractstr)]
        indata = [start, end, int(digitstr), int(fractstr)]

        self.usb_cntrl_write(
            brequest=self.SRV_SWD_IDCODE_SCAN,
            wvalue=0, windex=0,
            data_or_wlength=indata
        )

        resp_array = self.__read_service_response(self.SRV_SWD_IDCODE_SCAN)
        if resp_array:
            return self.__build_swd_idcode_dict(resp_array)
        return None

    @staticmethod
    def __build_uart_pin_dict(resp_array):
        """
        Build dict of TX, RX and Baudrate of UART port from response array

        Args:
            resp_array (byte array): UART scan service response
                from BusAuditor

        Returns:
            dict: dict of TX, RX and Baudrate of UART port
        Raises:
            Nothing
        """

        baud_array = []

        for resp in resp_array:
            data = resp[3:]
            data_len = resp[1] - 1

            # data represent as below:
            # data = tx (1byte) + rx (1byte) + baud (4bytes)

            if len(data) != data_len:
                return None

            baud_list = ["", ]
            baud_list = struct.unpack_from("<I", data[2:6])
            baudrate = int(baud_list[0])

            baud_dict = dict()
            baud_dict["baud"] = baudrate
            baud_dict.update({"pins": {"tx": data[1], "rx": data[0]}})
            baud_array.append(baud_dict)

        # baud_array[] look like
        #  [{'baud': 115200, 'pins': {'tx': 1, 'rx': 0}},
        #   {'baud': 115200, 'pins': {'tx': 1, 'rx': 2}},
        #   {'baud': 115200, 'pins': {'tx': 1, 'rx': 3}} ....
        #  ]

        # combine same baud rate and diff pins together in one dict
        baud = None
        new_baud = True
        new_pins = True
        uart_array = []

        for port in baud_array:
            # start with new element of array
            baud = port["baud"]
            pins = port["pins"]

            # Scan through new uart array for matched baudrate
            for item in uart_array:
                abaud = item["baud"]
                pins_array = item["pins"]

                if abaud == baud:
                    new_baud = False
                    new_pins = True
                    for apins in pins_array:
                        if apins == pins:
                            new_pins = False

                    if new_pins:
                        pins_array.append(pins)
                        new_baud = False
                else:
                    new_baud = True
                    break

            if new_baud:
                uart_array.append({"baud": baud, "pins": [pins]})
                new_baud = False

        return uart_array

        # uart_dict["uart_port"] = uart_array
        # return uart_dict

    def device_uart_tx_scan(self, start, end, volts):
        """
        This method initiates UART port scan for TX pin and Baudrate

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Returns:
            dict: dict of RX, TX and Baudrate of UART port
        Raises:
            Nothing
        """

        # Target voltage is split in to digit str and fraction str
        (digitstr, fractstr) = volts.rstrip().split(".")

        # create sevice data as an array of
        # [start, end, int(digitstr), int(fractstr)]
        indata = [start, end, int(digitstr), int(fractstr)]

        self.usb_cntrl_write(
            brequest=self.SRV_UART_TX_SCAN,
            wvalue=0, windex=0,
            data_or_wlength=indata
        )

        resp_array = self.__read_service_response(self.SRV_UART_TX_SCAN)
        if resp_array:
            return self.__build_uart_pin_dict(resp_array)
        return None

    def device_uart_tx_rx_scan(self, start, end, volts):
        """
        This method initiates UART port scan for TX, RX pin and Baudrate

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Returns:
            dict: dict of JTAG device ID code and JTAG pins
        Raises:
            Nothing
        """

        # Target voltage is split in to digit str and fraction str
        (digitstr, fractstr) = volts.rstrip().split(".")

        # create sevice data as an array of
        # [start, end, int(digitstr), int(fractstr)]
        indata = [start, end, int(digitstr), int(fractstr)]

        self.usb_cntrl_write(
            brequest=self.SRV_UART_TX_RX_SCAN,
            wvalue=0, windex=0,
            data_or_wlength=indata
        )

        resp_array = self.__read_service_response(self.SRV_UART_TX_RX_SCAN)
        if resp_array:
            return self.__build_uart_pin_dict(resp_array)
        return None

    def device_uart_scan(self, start, end, volts):
        """
        This method initiates UART port scan for TX pin first,
        followed by TX, RX pins scan.
        if tx pin is actively transmitting data then method
        returns TX pin and baudrate.
        if tx pin is not active, then this method generate data on RX pin
        with fixed baudrate and wait for activity on tx pin to find baudrate

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Returns:
            dict: dict of JTAG device ID code and JTAG pins
        Raises:
            Nothing
        """

        tx_pin_dict = self.device_uart_tx_scan(start, end, volts)
        if tx_pin_dict:
            return tx_pin_dict

        rx_pin_dict = self.device_uart_tx_rx_scan(start, end, volts)
        if rx_pin_dict:
            return rx_pin_dict

        return None

    @staticmethod
    def __build_i2c_addr_dict(resp_array):
        """
        Build dict of I2C device addr and I2C pins from response array

        Args:
            resp_array (byte array): I2C scan service response
                from BusAuditor

        Returns:
            dict: dict of SCL, SDA and addr of I2C device on I2C bus
        Raises:
            Nothing
        """

        device_list = []
        for resp in resp_array:
            data = resp[3:]
            data_len = resp[1] - 1

            # data represent as below:
            # data = scl (1byte) + sda (1byte)
            #        + addr1 (1bytes) + addr2 (1bytes) ...

            if len(data) != data_len:
                continue

            addr_list = data[2:]
            for _, addr in enumerate(addr_list):
                device_dict = dict()
                device_dict["i2c_addr"] = "0x{:02x}".format(addr)
                device_dict["pins"] = {"scl": data[0], "sda": data[1]}
                device_list.append(device_dict)

        return device_list

    def device_i2c_scan(self, start, end, volts):
        """
        This method initiates I2C bus scan for active I2C devices

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Returns:
            dict: dict of I2C pins and I2C device addr on I2C bus
        Raises:
            Nothing
        """

        # Target voltage is split in to digit str and fraction str
        (digitstr, fractstr) = volts.rstrip().split(".")

        # create sevice data as an array of
        # [start, end, int(digitstr), int(fractstr)]
        indata = [start, end, int(digitstr), int(fractstr)]

        self.usb_cntrl_write(
            brequest=self.SRV_I2C_ADDR_SCAN,
            wvalue=0, windex=0,
            data_or_wlength=indata
        )

        resp_array = self.__read_service_response(self.SRV_I2C_ADDR_SCAN)
        if resp_array:
            return self.__build_i2c_addr_dict(resp_array)
        return None

    def __read_service_response(self, service):
        """
        This method read data from USB core driver on fixed EP of BusAuditor

        Args:
            service (int): Service response to be verified.
        Returns:
            list: List of valid service response packets
        Raises:
            USBError
        """

        resp = None
        resp_array = []
        while True:
            try:
                resp = self.usb_read(size_or_buffer=self.__maxpacketsize)

            # Raise exceptions other than timeout
            except usb.core.USBError as err:
                if err.errno != self.USB_OP_TIMEOUT_ERROR:  # not timed out
                    raise err

                continue

            if (
                len(resp) == 2
                and resp[0] == self.SERVICE_RESP_BIT | service
                and resp[1] == 0
            ):
                # Scan end here, return collected  data for processing
                break
            if (
                len(resp) == 3
                and resp[0] == self.SERVICE_RESP_BIT | service
                and resp[2] == 0
            ):
                # Service accepted by BusAuditor, read for next packets in queue
                continue
            if (
                len(resp) == 3
                and resp[0] == self.SERVICE_RESP_BIT | service
                and resp[2] != 0
            ):
                # Some service error occured
                raise ValueError(
                    "Service Error - {}".format(self._srv_err[resp[2]])
                )
            if (
                len(resp) > 3
                and resp[0] == self.SERVICE_RESP_BIT | service
                and resp[2] == 0
            ):
                resp_array.append(resp)
            else:
                raise ValueError(
                    "Unknow Error - {}".format(resp[2])
                )

        return resp_array

    def usb_cntrl_read(
        self, brequest, wvalue=0, windex=0, data_or_wlength=None, timeout=100
    ):
        """
        USB Control Transfer, EP0 DIR IN

        Args:
            brequest (int): usb bRequest
            wvalue (int): usb wValue
            windex (int): usb wIndex
            data_or_wlength (int/list): usb data to be write
            timeout (int): timeout for write transaction
        Returns:
            bytes array: bytes read from driver (array object)
        Raises:
            Nothing
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
        self, brequest, wvalue=0, windex=0, data_or_wlength=None, timeout=100
    ):
        """
        USB Control Transfer, EP0 DIR OUT

        Args:
            brequest (int): usb bRequest
            wvalue (int): usb wValue
            windex (int): usb wIndex
            data_or_wlength (int/list): usb data to be write
            timeout (int): timeout for write transaction
        Returns:
            int: number of bytes written
        Raises:
            Nothing
        """

        return self.dev.ctrl_transfer(
            self.USB_DIR_OUT,
            bRequest=brequest,
            wValue=wvalue,
            wIndex=windex,
            data_or_wLength=data_or_wlength,
            timeout=timeout,
        )

    def usb_read(self, size_or_buffer, timeout=1000):
        """
        USB Bulk read for EP1.

        Args:
            size_or_buffer (int/list): data buffer or size to be read
            timeout (int): timeout for write transaction
        Returns:
            bytes array: bytes read from driver (array object)
        Raises:
            Nothing
        """

        return self.dev.read(self.__data_ep, size_or_buffer, timeout)

    def get_device_fw_rev_str(self):
        """
        Return firmware revision in string format.

        Args:
            Nothing
        Returns:
            str: firmware revision
        Raises:
            Nothing
        """

        return self.__fw_version

    def get_device_hw_rev_str(self):
        """
        Return hardware revision in string format.

        Args:
            Nothing
        Returns:
            str: firmware revision
        Raises:
            Nothing
        """

        return self.__hw_version

    def get_device_name(self):
        """
        Return the device name.

        Args:
            Nothing
        Returns:
           str: Device Name
        Raises:
            Nothing
        """

        return self.__dev_name

    def get_device_serial_num(self):
        """
        Return the device serial number.

        Args:
            Nothing
        Returns:
           str: Device serial number
        Raises:
            Nothing
        """

        return self.__serial_num

    def close(self):
        """
        Close usb device and cleanup.

        Args:
            Nothing
        Returns:
           Nothing
        Raises:
            Nothing
        """

        pass

    def __del__(self):
        """Close device."""
        self.close()
