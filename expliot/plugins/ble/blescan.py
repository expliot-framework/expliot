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

from expliot.core.tests.test import *
from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.radio.ble import Ble, BlePeripheral

class BleScan(Test):

    def __init__(self):
        super().__init__(name     = "BLE Scan",
                         summary  = "Scan for BLE devices",
                         descr    = """This test allows you to scan and list the BLE devices
                                        in the proximity. It can also enumerate the characteristics
                                        of a single device if specified. NOTE: This plugin needs
                                        root privileges. You may run it as $ sudo efconsole""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://en.wikipedia.org/wiki/Bluetooth_Low_Energy"],
                         category = TCategory(TCategory.BLE, TCategory.RD, TCategory.RECON),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
                         needroot = True)

        self.argparser.add_argument("-i", "--iface", default=0, type=int,
                                    help="HCI interface no. to use for scanning. 0 = hci0, 1 = hci1 and so on. Default is 0")
        self.argparser.add_argument("-t", "--timeout", default=10, type=int,
                                    help="Scan timeout. Default is 10 seconds")
        self.argparser.add_argument("-a", "--addr",
                                    help="""Address of BLE device whose services/characteristics will be enumerated.
                                            If not specified, it does an address scan for all devices""")
        self.argparser.add_argument("-r", "--randaddrtype", action="store_true",
                                    help="Use LE address type random. If not specified use address type public")
        self.argparser.add_argument("-s", "--services", action="store_true",
                                    help="Enumerate the services of the BLE device")
        self.argparser.add_argument("-c", "--chars", action="store_true",
                                    help="Enumerate the characteristics of the BLE device")
        self.argparser.add_argument("-v", "--verbose", action="store_true", help="""Verbose output. Use it for more
                                    info about the devices and their characteristics""")
        self.found = False
        self.reason = None

    def execute(self):
        if self.args.addr is not None:
            self.enumerate()
        else:
            self.scan()
        self.result.setstatus(passed=self.found,reason=self.reason)

    def scan(self):
        """
        Scan for BLE devices in the proximity
        :return:
        """
        TLog.generic("Scanning BLE devices for {} second(s)".format(self.args.timeout))
        try:
            devs = Ble.scan(iface=self.args.iface, tout=self.args.timeout)
            for d in devs:
                self.found=True
                TLog.success("(name={})(address={})".format(d.getValueText(Ble.ADTYPE_NAME) or "Unknown", d.addr))
                if self.args.verbose is True:
                    TLog.success("    (rssi={}dB)".format(d.rssi))
                    TLog.success("    (connectable={})".format(d.connectable))
                    for sd in d.getScanData():
                        TLog.success("    ({}={})".format(sd[1], sd[2]))
        except:
            self.reason="Exception caught: {}".format(sysexcinfo())

        if self.found is False and self.reason is None:
            self.reason = "No BLE devices found"


    def enumerate(self):
        """
        Enumerate the services and/or characteristsics of the specified BLE device

        :return:
        """
        # documentation is wrong, the first keyword argument is deviceAddr instead of deviceAddress as per the doc
        # Doc: http://ianharvey.github.io/bluepy-doc/
        if self.args.services is False and self.args.chars is False:
            TLog.fail("Specify the enumerations option(s). Either or both - services, chars")
            self.reason = "Incomplete arguments"
            return

        TLog.generic("Enumerating services/characteristics of the device {}".format(self.args.addr))
        d = BlePeripheral()
        try:
            d.connect(self.args.addr, addrType=(Ble.ADDR_TYPE_RANDOM if self.args.randaddrtype else Ble.ADDR_TYPE_PUBLIC))
            self.found = True
            if self.args.services is True:
                svcs = d.getServices()
                for s in svcs:
                    TLog.success("(service uuid={})(handlestart={})(handleend={})".format(s.uuid,
                                                                                         hex(s.hndStart),
                                                                                         hex(s.hndEnd)))
            if self.args.chars is True:
                chrs = d.getCharacteristics()
                for c in chrs:
                    TLog.success("(characteristic uuid={})(handle={})".format(c.uuid, hex(c.getHandle())))
                    if self.args.verbose is True:
                        sr = c.supportsRead()
                        TLog.success("    (supports_read={})".format(sr))
                        if sr is True:
                            TLog.success("    (value={})".format(c.read()))
        except:
            self.reason = "Exception caught: {}".format(sysexcinfo())
        finally:
            d.disconnect()
        if self.found is False and self.reason is None:
            self.reason = "Couldnt find any devices"
