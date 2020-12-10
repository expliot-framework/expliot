"""Plugin/test details."""
import argparse
from collections import namedtuple
from os import geteuid
import sys

from expliot.core.common import recurse_list_dict, bstr
from expliot.core.common.exceptions import sysexcinfo

LOGNO = 0
LOGPRETTY = 1
LOGNORMAL = 2


class TCategory(namedtuple("TCategory", "tech, iface, action")):
    """
    Representation of Test Category.

    The class that defines the category of the test case. It is part of the
    Test class member _category. It can be used to identify the type of test
    or search for a specific category. It is a namedtuple that defines three
    attributes (for categorizing test cases).

    1. tech: What technology does the test use
    2. iface: Interface of the test i.e. whether it is for software or hardware
    3. action: What action does the test perform i.e. is it an exploit or a
               recon test for example.
    """

    # Tech category. The technology used by the test
    # Network Protocols
    COAP = "coap"
    DICOM = "dicom"
    HTTP = "http"
    MDNS = "mdns"
    MODBUS = "modbus"
    MQTT = "mqtt"
    TCP = "tcp"
    UDP = "udp"
    UPNP = "upnp"

    # Radio protocols
    BLE = "ble"
    IEEE802154 = "802154"
    ZIGBEE = "zigbee"

    # Hardware protocols
    CAN = "can"
    I2C = "i2c"
    JTAG = "jtag"
    SPI = "spi"
    UART = "uart"

    # Other
    CRYPTO = "crypto"
    # Auditors/Utilities
    ZB_AUDITOR = "zbauditor"
    BUS_AUDITOR = "busauditor"
    FW_AUDITOR = "fwauditor"
    NMAP = "nmap"

    _tech = [
        BLE,
        BUS_AUDITOR,
        CAN,
        COAP,
        CRYPTO,
        DICOM,
        FW_AUDITOR,
        HTTP,
        I2C,
        IEEE802154,
        JTAG,
        MDNS,
        MODBUS,
        MQTT,
        NMAP,
        SPI,
        TCP,
        UART,
        UDP,
        UPNP,
        ZB_AUDITOR,
        ZIGBEE,
    ]

    # Interface category. Whether the test is for software, hardware or radio
    HW = "hardware"
    RD = "radio"
    SW = "software"

    _interfaces = [SW, HW, RD]

    # Action category. The type of test
    ANALYSIS = "analysis"
    DISCOVERY = "discovery"
    EXPLOIT = "exploit"
    FUZZ = "fuzz"
    RECON = "recon"

    _actions = [RECON, DISCOVERY, ANALYSIS, FUZZ, EXPLOIT]

    def __init__(self, tech, iface, action):
        """Initialize the test category."""
        if tech not in TCategory._tech:
            raise AttributeError("Unknown technology for category - ({})".format(tech))
        if iface not in TCategory._interfaces:
            raise AttributeError("Unknown interface for category - ({})".format(iface))
        if action not in TCategory._actions:
            raise AttributeError("Unknown action for category - ({})".format(action))
        super().__init__()


class TTarget(namedtuple("TTarget", "name, version, vendor")):
    """
    Representation of Test Target class.

    Class that hold details about the target of the test. It is a namedtuple
    and holds the below details:

    1. name - Target/product name
    2. version - Version of the product
    3. vendor - Vendor that owns the product

    Please note, in case it is a generic test case that can be used for
    multiple products use Target.GENERIC for all attributes.
    """

    GENERIC = "generic"

    # Target name
    TP_LINK_IOT = "tpliot"
    AWS = "aws"
    _name = [
        AWS,
    ]

    # Target version

    # Target vendor
    TP_LINK = "tplink"
    AMAZON = "amazon"
    _vendor = [
        AMAZON,
    ]

    def __init__(self, name, version, vendor):
        """Initialize the test target."""
        super().__init__()


class TResult:
    """
    Representation of a test result.

    self.output is a list of dict. This is populated by the plugin
    when it needs to push results during the execution. To make it
    standardized, the plugin pushes a block of info in a dict object
    as and when it has certain info. For ex. when enumerating on
    something, each item identified will be push as a dict considering
    there is more than one data point to be stored for that item and
    once the plugin execution finishes we get a list of dicts containing
    same/similar data for each of the items.
    """

    defaultrsn = "No reason specified"

    def __init__(self):
        """
        Initialize a test result.

        NOTE: The output member MUST be populated as a list of dicts.
              This is the responsibility of the plugin and based on
              it's execution output it MUST document the format
              of output member clearly and explain the keys and meaning,
              type of values held by those keys.
        """
        self.passed = True
        self.reason = None
        # Test execution output list (of dicts)
        self.output = []

    def setstatus(self, passed=True, reason=None):
        """Set the Test result status.

        :param passed: True or False
        :param reason: Reason for failure if any
        :return:
        """
        self.passed = passed
        self.reason = reason

    def exception(self):
        """Set passed to False and reason to the exception message.

        Returns:
            Nothing
        """
        self.passed = False
        self.reason = "Exception caught: [{}]".format(sysexcinfo())

    def getresult(self):
        """
        Returns a dict with result data. Caller needs to make sure
        plugin execution (run()) is done before calling this.

        Returns:
            dict: the result data including status and output
        NOTE: This is the standard dict format that will be used by EXPLIoT
        for returning the plugin execution results. The dict keys and their
        meaning:
        status(int) - The execution status of the plugin. 0 if the test passed
                      1 otherwise.
        reason(str) - The reason the test failed. If it was successful, this
                      will be None.
        output(list) - The actual plugin execution output. This is a list of
                      dicts and the plugins MUST adhere to this format and
                      document their output format clearly in the plugin class.
        """
        return {"status": 0 if self.passed is True else 1,
                "reason": self.reason,
                "output": self.output}


class TLog:
    """
    Representation of a Test Log.

    Logger class for logging test case output. By default log to sys.stdout
    Must not instantiate. Use class methods. The logger needs to be initialized
    with the output file using init() class method
    """

    SUCCESS = 0
    FAIL = 1
    TRYDO = 2
    GENERIC = 3

    _prefix = ["[+]",  # SUCCESS prefix
               "[-]",  # FAIL prefix
               "[?]",  # TRYDO (Try/do/search) prefix
               "[*]"]  # GENERIC prefix]
    _errprefix = "[.]"
    _file = sys.stdout

    @classmethod
    def init(cls, file=None):
        """
        Initialize the file object. This method should be called in the
        beginning of the application to open the log output file.

        :param file: The file where to log the test output
        :return:
        """
        cls.close()
        if file is None:
            cls._file = sys.stdout
        else:
            cls._file = open(file, mode="w")

    @classmethod
    def close(cls):
        """Close the file object if it is not sys.stdout.

        :return:
        """
        if cls._file != sys.stdout and cls._file is not None:
            cls._file.close()

    @classmethod
    def print(cls, prefixtype, message):
        """
        The actual print methods that write the formatted message to the _file
        file.

        Args:
            prefixtype(int): the prefix type to be used for the message (defined above)
            message(str): The actual message from the Test object
        Returns:
            Nothing
        """
        try:
            pre = cls._prefix[prefixtype]
        except IndexError:
            pre = cls._errprefix
        print("{} {}".format(pre, message), file=cls._file)

    @classmethod
    def success(cls, message):
        """Write a message with success prefix to the file.

        :param message: The message to be written
        :return:
        """
        cls.print(cls.SUCCESS, message)

    @classmethod
    def fail(cls, message):
        """Write a message with fail prefix to the file.

        :param message: The message to be written
        :return:
        """
        cls.print(cls.FAIL, message)

    @classmethod
    def trydo(cls, message):
        """Write a message with try prefix to the file.

        :param message: The message to be written
        :return: void
        """
        cls.print(cls.TRYDO, message)

    @classmethod
    def generic(cls, message):
        """Write a message with success prefix to the file.

        :param message: The message to be written
        :return: void
        """
        cls.print(cls.GENERIC, message)


class Test:
    """
    Representation of Test.

    The Base class for test cases (plugins). It defines the basic interface
    and basic implementation for the test cases. All test case plugins need
    to inherit from a test class derived from this class or this class itself
    depending on the purpose of the test case.
    """

    def __init__(self, **kwargs):
        """Initialize the test."""
        self.name = kwargs["name"]
        self.summary = kwargs["summary"]
        self.descr = kwargs["descr"]
        self.author = kwargs["author"]
        self.email = kwargs["email"]
        self.ref = kwargs["ref"]
        self.category = kwargs["category"]
        self.target = kwargs["target"]
        self.needroot = kwargs["needroot"] if ("needroot" in kwargs.keys()) else False

        self._setid()
        self.argparser = argparse.ArgumentParser(prog=self.id, description=self.descr)
        self.result = TResult()

        # Namespace returned by self.argparser.parser_args()
        # This gets defined in the run() method and has a getter
        # self.args for inherited class Plugin
        self.args = None

    def pre(self):
        """Action to take before the test."""
        pass
        # TLog.generic("Test base class pre({}) method".format(self.__class__.__name__))

    def post(self):
        """Action to take after the test."""
        pass
        # TLog.generic("Test base class post({}) method".format(self.__class__.__name__))

    def execute(self):
        """Execute the test."""
        print("Test base class execute() method")

    def intro(self):
        """Show the intro for test."""
        TLog.generic("{:<13} {}".format("Test:", self.id))
        TLog.generic("{:<13} {}".format("Author:", self.author))
        TLog.generic("{:<13} {}".format("Author Email:", self.email))
        TLog.generic("{:<13} {}".format("Reference(s):", self.ref))
        TLog.generic(
            "{:<13} Technology={}|Interface={}|Action={}".format(
                "Category:",
                self.category.tech,
                self.category.iface,
                self.category.action,
            )
        )
        TLog.generic(
            "{:<13} Name={}|Version={}|Vendor={}".format(
                "Target:", self.target.name, self.target.version, self.target.vendor
            )
        )
        TLog.generic("")

    def output_dict_iter(self, cblog, robj, rlevel, key=None, value=None):
        """
        Callback method for recurse_list_dict(). It iterates over the dict
        output passed from a plugin to output_handler(). It performs two
        operations on the dict
            1. If the output data is to be TLog(ged) (LOGPRETTY) on the console,
               then log the data recursively from the dict.
            2. Convert any bytes or bytearray objects in the dict to binary string
               and update the original dict object itself.

        Args:
            cblog (dict): Contains logging information i.e. to log the data or not?
                and the Log prefix type.
            robj (list or dict): The list or dict object at the specified recursion
                level. This is updated by this callback i.e. bytes and bytearray
                objects found are converted to binary strings.
            rlevel (int): The current recursion level at which this callback
                instance is called.
            key (str): The key if the robj is a dict.
            value (can be any type): 1. The value of the key if robj is a dict or
                                     2. A value from the robj if it is a list
    Returns:
        Nothing
        """
        spaces = "  " * rlevel

        if robj.__class__ == dict and (value.__class__ == dict or value.__class__ == list):
            if cblog["logkwargs"] == LOGPRETTY:
                TLog.print(cblog["tlogtype"], "{}{}:".format(spaces, key))
        else:
            strval = value
            isbval = False
            if isinstance(value, bytes) or isinstance(value, bytearray):
                strval = bstr(value)
                isbval = True
            if key:
                if cblog["logkwargs"] == LOGPRETTY:
                    TLog.print(cblog["tlogtype"], "{}{}: {}".format(spaces, key, strval))
                if isbval:
                    robj[key] = strval
            else:
                if cblog["logkwargs"] == LOGPRETTY:
                    TLog.print(cblog["tlogtype"], "{}{}".format(spaces, strval))
                if isbval:
                    robj[robj.index(value)] = strval

    def output_handler(self,
                       tlogtype=TLog.SUCCESS,
                       msg=None,
                       logkwargs=LOGPRETTY,
                       **kwargs):
        """
        Handle the Test execution output Data
          - Add(append) data (dict) as an item in the TResult output (list).
          - And/or Log (print) the output

        Args:
            tlogtype (int): TLog prefix type to use i.e. Success, fail etc.
                Check TLog class for prefix details.
            msg (str): Specify a message to be logged, if any, apart from
                output data.
            logkwargs=LOGPRETTY(int): There are three options for kwargs logging
                LOGPRETTY(0) - formatted logging for dict or list.
                LOGNORMAL(1) - Direct print of dict or list as is.
                LOGNO(2) - Do not log kwargs.
            **kwargs: plugin output keyword arguments (or a **dictObject)

        Returns:
            Nothing.
        """
        if msg is not None:
            TLog.print(tlogtype, msg)
        if not kwargs:
            # empty dict
            return
        cblog = {"tlogtype": tlogtype,
                 "logkwargs": logkwargs}
        # Any bytes or bytearray value in kwargs are converted to binary
        # str using expliot.core.common.bstr().
        recurse_list_dict(kwargs, self.output_dict_iter, cblog)
        if logkwargs == LOGNORMAL:
            TLog.print(tlogtype, kwargs)
        TLog.print(tlogtype, "")
        self.result.output.append(kwargs)

    def run(self, arglist):
        """
        Run the test.

        Args:
            arglist (list): The argument list of the plugin.

        Returns:
            dict: The plugin result (status and output) on success,
                or an empty dict in case of any error.
        """
        try:
            self.args = self.argparser.parse_args(arglist)
        except SystemExit:
            # Nothing to do here. SystemExit occurs in case of wrong arguments
            # or help. Cmd2 does not catch SystemExit from v1.0.2 -
            # https://github.com/python-cmd2/cmd2/issues/932
            # returning instead of raising Cmd2ArgparseError so in future any
            # post command hooks implemented can run
            return {}

        # Log Test Intro messages
        self.intro()

        # Check if the plugin needs root privileges and the program has
        # the required privileges
        self._assertpriv()

        # Test pre() method is used for setup related tasks, if any.
        self.pre()

        # Test execute() method is for the main test case execution.
        self.execute()

        # Test post() method is used for cleanup related tasks, if any.
        self.post()
        # except:
        #    self.result.exception()

        # Log Test status
        self._logstatus()

        # Return test result
        # print(self.result.getresult())
        return self.result.getresult()

    def _assertpriv(self):
        """
        Raise an exception if the plugin needs root privileges but program
        is not executing as root.

        Args:
            None

        Returns:
            Nothing
        """
        if self.needroot and geteuid() != 0:
            raise PermissionError(
                "Need root privilege to execute the plugin ({})".format(self.id)
            )

    def _setid(self):
        """
        Set the Unique Test ID. The ID is the plugin class name in lowercase.

        Args:
            None

        Returns:
            Nothing
        """
        # self.id = self.__class__.__name__.lower()
        self.id = "{}.{}.{}".format(
            self.category.tech, self.target.name, self.name
        ).lower()

    def _logstatus(self):
        """
        Handle the log status.

        Args:
            None

        Returns:
            Nothing
        """
        if self.result.passed:
            TLog.success("Test {} passed".format(self.id))
        else:
            TLog.fail("Test {} failed. Reason = {}".format(self.id, self.result.reason))
