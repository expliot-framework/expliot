"""Class support for common service and auditor specific services"""


class Services:
    """Base class for Services."""

    def __init__(self):
        """Init Base and device specific services."""

        self.base_services = {}
        self.device_services = {}

    def get_supported_services(self):
        """Returns Base Service Supported by device.

        :return: Dictionary of Base Services
        """

        services = dict()
        services.update(self.base_services)
        services.update(self.device_services)
        return services

    def get_supported_base_services(self):
        """Returns Base Service Supported by device.

        :return: Dictionary of Base Services
        """

        return self.base_services

    def get_supported_device_services(self):
        """Returns Base Service Supported by device.

        :return: Dictionary of Base Services
        """

        return self.device_services

    def set_base_serivce(self, service, value):
        """Set base service true if device supports it.

        :param service: service from services dictionary
        :param value: Ture or False
        """

        self.base_services[service] = value

    def set_device_serivce(self, service, value):
        """Set device service true if device supports it.

        :param service: service from services dictionary
        :param value: Ture or False
        """

        self.device_services[service] = value

    def is_service_active(self, service):
        """Validate device supports service or not.

        :param service: service from services dictionary
        :return: True if service is available in device else False
        """
        if self.device_services[service]:
            return True

        return False


class BaseServices(Services):
    """Class to store Base Services."""

    GET_FW_REV = "read_revision"
    GET_FW_SERV = "read_services"

    def __init__(self):
        """Init Base Services to default."""

        super().__init__()

        self.base_services = {
            self.GET_FW_REV: False,
            self.GET_FW_SERV: False,
        }


class ZbAuditorServices(BaseServices):
    """Class to Zigbee Auditor's Services."""

    SET_MAC_POWER = "radio_on_off"
    SET_CH_CHNG = "channel_selection"
    RAW_CAPTURE = "802.15.4_sniffer"
    RAW_INJECT = "802.15.4_injection"
    NWK_SCAN = "802.15.4_network_scan"
    SUPP_FREQ_2400 = "2400_mhz"
    SUPP_FREQ_784 = "784_mhz"
    SUPP_FREQ_868 = "868_mhz"
    SUPP_FREQ_915 = "915_mhz"

    def __init__(self):
        """Init Zigbee Auditor services to default."""

        super().__init__()

        self.device_services = {
            self.SET_CH_CHNG: False,
            self.SET_MAC_POWER: False,
            self.RAW_CAPTURE: False,
            self.RAW_INJECT: False,
            self.NWK_SCAN: False,
            self.SUPP_FREQ_2400: False
        }


class BusAuditorServices(BaseServices):
    """Class to store BusAuditor's Services."""

    JTAG_SCAN = "jtag_port_scan"
    SWD_SCAN = "swd_port_scan"
    UART_SCAN = "uart_port_scan"
    I2C_SCAN = "i2c_bus_scan"

    def __init__(self):
        """Init BusAuditor services to default."""

        super().__init__()

        self.device_services = {
            self.JTAG_SCAN: False,
            self.SWD_SCAN: False,
            self.UART_SCAN: False,
            self.I2C_SCAN: False,
        }
