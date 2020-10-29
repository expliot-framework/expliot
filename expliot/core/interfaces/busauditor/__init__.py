"""Wrapper for BusAuditor interface."""

from expliot.core.interfaces.busauditor.stm32f411 import STM32F411


class BusAuditor:
    """BusAuditor interface class."""

    def __init__(self):
        """
        Constructor: BusAuditor interface for STM32F411 USB driver.

        Args:
            Nothing
        Returns:
            Nothing
        Raises:
            Nothing
        """

        self.driver = None

        # Read driver
        self.driver = STM32F411()

    def get_interface_info(self):
        """
        Returns Device information in dictionary format.

        Args:
            Nothing

        Return:
            dict: The dict containing Device Name, FW, HW Revision, Services

        Raises:
            Nothing
        """

        if self.driver is not None:
            dev_info = dict()
            dev_info["device_name"] = self.driver.get_device_name()
            dev_info["serial_number"] = self.driver.get_device_serial_num()
            dev_info["fw_revision"] = self.driver.get_device_fw_rev_str()
            dev_info["hw_revision"] = self.driver.get_device_hw_rev_str()
            dev_info["services"] = self.driver.get_supported_services()
            return dev_info

    def jtag_scan(self, start, end, volts, include_trst=False):
        """
        Call BusAuditor driver to scan JTAG port pins using IDCODE
        and pattern scan.

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out
            include_trst (boolean): Include TRST pin in scan.
                                    TRST pin excluded by default

        Return:
            list: The list of dict containing JTAG ID and pin info

        Raises:
            Nothing
        """

        return self.driver.device_jtag_scan(start, end, volts, include_trst)

    def swd_scan(self, start, end, volts):
        """
        Returns SWD IDCODE scan result in dictionary format.

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Return:
            list: The list of dict containing SWD ID and pin info

        Raises:
            Nothing
        """

        return self.driver.device_swd_scan(start, end, volts)

    def uart_scan(self, start, end, volts):
        """
        Returns UART Rx, Tx and baudrate scan result in dictionary format.

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Return:
            list: The list of dict containing UART baudrate and pin info

        Raises:
            Nothing
        """

        return self.driver.device_uart_scan(start, end, volts)

    def i2c_scan(self, start, end, volts):
        """
        Returns I2C device addr, and pin scan result in dictionary format.

        Args:
            start (int): First pin (channel number) to start the scan
            stop (int): Last pin (channel number) to stop the scan
            volts (str): Target voltage out

        Return:
            list: The list of dict containing I2C device addr and pin info
        Raises:
            Nothing
        """

        return self.driver.device_i2c_scan(start, end, volts)

    def close(self):
        """
        Close USB port of BUS Auditor.

        Args:
            Nothing
        Retrun:
            Nothing
        Raises:
            Nothing
        """

        if self.driver:
            return self.driver.close()
