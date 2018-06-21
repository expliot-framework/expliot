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
from expliot.core.protocols.radio.ble import Ble, BlePeripheral

class BleCharWrite(Test):

    def __init__(self):
        super().__init__(name     = "BLE charecteristic write",
                         summary  = "Write a value to a characteristic on a BLE peripheral",
                         descr    = """This test allows you to write a value to a characteristic on
                                        a BLE peripheral device""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://en.wikipedia.org/wiki/Bluetooth_Low_Energy"],
                         category = TCategory(TCategory.BLE, TCategory.RD, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-a", "--addr", required=True,
                                    help="Address of BLE device whose characteristic value will be written to")
        self.argparser.add_argument("-n", "--handle", required=True, type=lambda x: int(x,0),
                                    help="Specify the handle to write to. Prefix 0x if handle is hex")
        self.argparser.add_argument("-w", "--value", required=True, help="Specify the value to write")

        self.argparser.add_argument("-r", "--randaddrtype", action="store_true",
                                    help="Use LE address type random. If not specified use address type public")

        self.argparser.add_argument("-s", "--noresponse", action="store_true",
                                    help="Send write command instead of write request i.e. no response, if specified")


    def execute(self):
        TLog.generic("Writing the value ({}) to handle ({}) on BLE device ({})".format(self.args.value,
                                                                                       hex(self.args.handle),
                                                                                       self.args.addr))
        d = BlePeripheral()
        try:
            d.connect(self.args.addr, addrType=(Ble.ADDR_TYPE_RANDOM if self.args.randaddrtype else Ble.ADDR_TYPE_PUBLIC))
            d.writeCharacteristic(self.args.handle, bytes.fromhex(self.args.value),
                                  withResponse=(not self.args.noresponse))
        except:
            self.result.exception()
        finally:
            d.disconnect()
