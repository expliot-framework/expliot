#
#
# expliot - Internet Of Things Security Testing and Exploitation Framework
# 
# Copyright (C) 2018  Aseem Jakhar
#
# Email:   aseemjakhar@gmail.com
# Twitter: @aseemjakhar
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import sys
import argparse
from collections import namedtuple
from os import geteuid
from expliot.core.common.exceptions import sysexcinfo

class TCategory(namedtuple("TCategory", "proto, iface, action")):
    """
    TCategory class

    The class that defines thet category of the test case. It is part of the Test class
    member _category. It can be used to identy the type of test or search for a specific
    category. It is a namedtuple that defines three attributes (for categorizing test cases)
    1. proto  - What protocol does the test use
    2. iface  - Interface of the test i.e. whether it is for software or hardware
    3. action - What action does the test perform i.e. is it an exploit or a recon test for example.
    """

    #Protocol category - The protocol used by the test
    # internet protocols
    COAP      = "coap"
    MQTT      = "mqtt"
    UDP       = "udp"
    MODBUSTCP = "modbustcp"
    # Radio protocols
    BLE    = "ble"
    ZIGBEE = "zigbee"
    # hardware protocols
    CAN    = "can"
    UART   = "uart"
    JTAG   = "jtag"
    I2C    = "i2c"
    SPI    = "spi"
    _protocols = [COAP, MQTT, UDP, MODBUSTCP, BLE, ZIGBEE, CAN, UART, JTAG, I2C, SPI]

    # Interface category - whether the test is for software, hardware or radio
    SW = "software"
    HW = "hardware"
    RD = "radio"
    _interfaces = [SW, HW, RD]

    # Action category - The type of test
    RECON    = "recon"
    ANALYSIS = "analysis"
    FUZZ     = "fuzz"
    EXPLOIT  = "exploit"
    _actions = [RECON, ANALYSIS, FUZZ, EXPLOIT]

    def __init__(self, proto, iface, action):
        if proto not in TCategory._protocols:
            raise AttributeError("Unknown Protocol for Category - ({})".format(proto))
        if iface not in TCategory._interfaces:
            raise AttributeError("Unknown Interface for Category - ({})".format(iface))
        if action not in TCategory._actions:
            raise AttributeError("Unknown Action for Category - ({})".format(action))
        super().__init__()


class TTarget(namedtuple("TTarget", "name, version, vendor")):
    """
    TTarget class

    Class that hold details about the target of the test. It is a namedtuple and
    holds the below details:
    1. name - Target/product name
    2. version - Version of the product
    3. vendor - Vendor that owns the product
    Please note, in case it is a generic test case that can be used for multiple products
    use Target.GENERIC for all attributes

    """
    GENERIC = "generic"

    def __init__(self, name, version, vendor):
        super().__init__()

class TResult():

    defaultrsn = "No reason specified"

    def __init__(self):
        self.passed = True
        self.reason  = None

    def setstatus(self, passed=True, reason=None):
        """
        Set the Test result status

        :param passed: True or False
        :param reason: Reason for failure if any
        :return:
        """
        self.passed = passed
        self.reason = reason

    def exception(self):
        """
        Set passed to False and reason to the exception message

        :return:
        """
        self.passed=False
        self.reason="Exception caught: [{}]".format(sysexcinfo())

class TLog():
    """
    TLog

    Logger class for logging test case output. By default log to sys.stdout
    Must not instantiate. Use class methods. The logger needs to be initialized
    with the output file using init() class method
    """
    _f = sys.stdout
    _spre = "[+]" # Success prefix
    _fpre = "[-]" # Fail prefix
    _tpre = "[?]" # Try/search prefix
    _gpre = "[*]" # Generic prefix

    @classmethod
    def init(cls, file=None):
        """
        Initialize the file object. This method should be called in the beginning
        of the application to open the log output file.

        :param file: The file where to log Test output
        :return: void
        """
        cls.close()
        if file == None:
            cls._f = sys.stdout
        else:
            cls._f = open(file, mode="w")

    @classmethod
    def close(cls):
        """
        Close the file object if it is not sys.stdout
        :return:
        """
        if cls._f != sys.stdout and cls._f is not None:
            cls._f.close()

    @classmethod
    def _p(cls, prefix, msg):
        """
        The actual print methods that write the formatted message to the _f file.
        :param prefix: the prefix to be used for the message (defined above)
        :param msg: The actual message from the Test object
        :return: void
        """
        print("{} {}".format(prefix, msg), file=cls._f)

    @classmethod
    def success(cls, msg):
        """
        Write a message with success prefix to the file
        :param msg: The message to be written
        :return: void
        """
        cls._p(cls._spre, msg)

    @classmethod
    def fail(cls, msg):
        """
        Write a message with faile prefix to the file
        :param msg: The message to be written
        :return: void
        """
        cls._p(cls._fpre, msg)

    @classmethod
    def trydo(cls, msg):
        """
        Write a message with try prefix to the file
        :param msg: The message to be written
        :return: void
        """
        cls._p(cls._tpre, msg)

    @classmethod
    def generic(cls, msg):
        """
        Write a message with success prefix to the file
        :param msg: The message to be written
        :return: void
        """
        cls._p(cls._gpre, msg)


class Test:
    """
    Test

    The Base class for test cases (plugins). It defines the basic interface and basic implementation
    for the test cases. All test case plugins need to inherit from a test class derived from this class
    or this class itself depending on the purpose of the test case.
    """
    def __init__(self, **kwargs):
        self.name     = kwargs["name"]
        self.summary  = kwargs["summary"]
        self.descr    = kwargs["descr"]
        self.author   = kwargs["author"]
        self.email    = kwargs["email"]
        self.ref      = kwargs["ref"]
        self.category = kwargs["category"]
        self.target   = kwargs["target"]
        self.needroot = kwargs["needroot"] if ("needroot" in kwargs.keys()) else False

        self._setid()
        self.argparser = argparse.ArgumentParser(prog=self.id, description=self.descr)
        self.result = TResult()

        # Namespace returned by self.argparser.parser_args()
        # This gets defined in the run() method and has a getter self.args for inherited class Plugin
        self.args = None

    def pre(self):
        pass
        #TLog.generic("Test base class pre({}) method".format(self.__class__.__name__))

    def post(self):
        pass
        #TLog.generic("Test base class post({}) method".format(self.__class__.__name__))

    def execute(self):
        print("Test base class execute() method")

    def intro(self):
        TLog.generic("{:<13} {}".format("Test:", self.name))
        TLog.generic("{:<13} {}".format("Author:", self.author))
        TLog.generic("{:<13} {}".format("Author Email:", self.email))
        TLog.generic("{:<13} {}".format("Reference(s):", self.ref))
        TLog.generic("{:<13} Protocol={}|Interface={}|Action={}".format("Category:",
                                                                        self.category.proto,
                                                                        self.category.iface,
                                                                        self.category.action))
        TLog.generic("{:<13} Name={}|Version={}|Vendor={}".format("Target:",
                                                                  self.target.name,
                                                                  self.target.version,
                                                                  self.target.vendor))
        TLog.generic("")


    def run(self, arglist):
        # Not keeping parse_args in try block because it raises SystemExit in case of -h/--help
        # which gets handled by cmd or argparse I think. If we keep in it below try block
        # run plugin with -h/--help catches the exception and fails the test case due to the
        # below except
        self.args = self.argparser.parse_args(arglist)
        for i in range(0,1): #try:
            # Log Test Intro messages
            self.intro()

            # Check if the plugin needs root privileges and the program has the required privileges
            self._assertpriv()

            # Test pre() method is used for setup related tasks, if any.
            self.pre()

            # Test execute() method is for the main test case execution.
            self.execute()

            # Test post() method is used for cleanup related tasks, if any.
            self.post()
        #except:
        #    self.result.exception()

        # Log Test status
        self._logstatus()

    def _assertpriv(self):
        """
        Raises an exception if the plugin needs root privileges but program is not executing as root
        :return:
        """
        if self.needroot and geteuid() != 0:
            raise PermissionError("Need root privilege to execute the plugin ({})".format(self.id))

    def _setid(self):
        """
        Set the Unique Test ID. The ID is the plugin class name in lower case

        :return:
        """
        self.id = self.__class__.__name__.lower()

    def _logstatus(self):
        if self.result.passed:
            TLog.success("Test {} Passed".format(self.id))
        else:
            TLog.fail("Test {} Failed. Reason = {}".format(self.id, self.result.reason))