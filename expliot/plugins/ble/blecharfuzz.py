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

from random import randint
from expliot.core.tests.test import *
from expliot.core.protocols.radio.ble import Ble, BlePeripheral


class BleCharFuzz(Test):

    def __init__(self):
        super().__init__(name     = "BLE Charecteristic value fuzzer",
                         summary  = "Fuzz and write values to a characteristic on a BLE peripheral",
                         descr    = """This test allows you to fuzz the value of a characteristic and
                                        write to a BLE peripheral device. Devices that have improper
                                        input handling code for values usually crash/reboot""",
                         author   = "Arun Magesh",
                         email    = "arun.m@payatu.com",
                         ref      = ["https://en.wikipedia.org/wiki/Bluetooth_Low_Energy"],
                         category = TCategory(TCategory.BLE, TCategory.RD, TCategory.FUZZ),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-a", "--addr", required=True,
                                    help="Address of BLE device whose characteristic value will be fuzzed")
        self.argparser.add_argument("-n", "--handle", required=True, type=lambda x: int(x,0),
                                    help="Specify the handle to write to. Prefix 0x if handle is hex")
        self.argparser.add_argument("-w", "--value", required=True,
                                    help="""Specify the value to fuzz and write. Mark the bytes as xx
                                            in the value that you want to fuzz. For ex. if the valid value is
                                            bd0ace and you want to fuzz the 2nd byte, specify the value as
                                            bdxxce. You can also fuzz the whole value just mark all bytes as
                                            xxxxxx""")
        #self.argparser.add_argument("-f", "--fuzz", type=int, default=0,
        #                            help="""Specify the type of fuzzing to be performed i.e. how to change the marked
        #                                    bytes in the value. 0 = random, 1 = sequential. Default is 0""")
        self.argparser.add_argument("-i", "--iter", type=int, default=255,
                                    help="""Specify the no. of iterations to fuzz the value. Default is 255""")

        self.argparser.add_argument("-r", "--randaddrtype", action="store_true",
                                    help="Use LE address type random. If not specified use address type public")

        self.argparser.add_argument("-s", "--noresponse", action="store_true",
                                    help="Send write command instead of write request i.e. no response, if specified")


    def execute(self):
        TLog.generic("Fuzzing the value ({}), iterations ({}) for handle ({}) on BLE device ({})".format(self.args.value,
                                                                                                         self.args.iter,
                                                                                                         hex(self.args.handle),
                                                                                                         self.args.addr))
        try:
            d = BlePeripheral()
            d.connect(self.args.addr, addrType=(Ble.ADDR_TYPE_RANDOM if self.args.randaddrtype else Ble.ADDR_TYPE_PUBLIC))
            for i in range(self.args.iter):
                f = self.args.value
                while f.find("xx") >= 0:
                    f = f.replace("xx", "{:02x}".format(randint(0, 0xff)), 1)

                TLog.trydo("Writing the fuzzed value ({})".format(f))
                d.writeCharacteristic(self.args.handle, bytes.fromhex(f),
                                          withResponse=(not self.args.noresponse))
        except:
            self.result.exception()
        finally:
            d.disconnect()
