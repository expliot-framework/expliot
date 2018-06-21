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

from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.protocols.internet.modbus import ModbusTcpClient

class MBTcpWrite(Test):
    COIL = 0
    REG = 1

    ITEMS = ["coil", "register"]
    def __init__(self):
        super().__init__(name     = "Modbus TCP Write",
                         summary  = "Write coil and register values to a Modbus server (slave)",
                         descr    = "This plugin writes the item (coil, register) values to a Modbus server",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://en.wikipedia.org/wiki/Modbus", "http://www.modbus.org/specs.php"],
                         category = TCategory(TCategory.MODBUSTCP, TCategory.SW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-r", "--rhost", required=True, help="hotname/IP address of the Modbus server")
        self.argparser.add_argument("-p", "--rport", default=502, type=int,
                                    help="Port number of the Modbus server. Default is 502")
        self.argparser.add_argument("-i", "--item", default=0, type=int,
                                    help="""The item to read from. {} = {}, {} = {}. 
                                            Default is {}""".format(self.COIL,
                                                                    self.ITEMS[self.COIL],
                                                                    self.REG,
                                                                    self.ITEMS[self.REG],
                                                                    self.COIL))
        self.argparser.add_argument("-a", "--address",default=0, type=int, help="The start address of item to write to")
        self.argparser.add_argument("-c", "--count",default=1, type=int, help="The count of items to write. Default is 1")
        self.argparser.add_argument("-u", "--unit", default=1, type=int,
                                    help="The Unit ID of the slave on the server to write to")
        self.argparser.add_argument("-w", "--value", required=True, type=int, help="The value to write")

    def execute(self):
        c = ModbusTcpClient(self.args.rhost, port=self.args.rport)
        try:
            # Check what to write to i.e. coils, registers etc
            if self.args.item < 0 or self.args.item >= len(self.ITEMS):
                raise AttributeError("Unknown --item specified ({})".format(self.args.item))
            if self.args.count < 1:
                raise AttributeError("Invalid --count specified ({})".format(self.args.count))

            TLog.generic("Sending write command to Modbus Server ({}) on port ({})".format(self.args.rhost,
                                                                                           self.args.rport))
            TLog.generic("(item={})(address={})(count={})(unit={})".format(self.ITEMS[self.args.item],
                                                                           self.args.address,
                                                                           self.args.count,
                                                                           self.args.unit))
            c.connect()
            if self.args.item == self.COIL:
                val = True if self.args.value != 0 else False
                TLog.trydo("Writing value(s) ({})".format(val))
                # below r = class pymodbus.bit_write_message.WriteMultipleCoilsResponse
                r = c.write_coils(self.args.address, [val]*self.args.count, unit=self.args.unit)
                if r.isError() == True:
                    raise Exception(str(r))
            elif self.args.item == self.REG:
                TLog.trydo("Writing value(s) ({})".format(self.args.value))
                # below r = class pymodbus.register_write_message.WriteMultipleRegistersResponse
                r = c.write_registers(self.args.address, [self.args.value]*self.args.count, unit=self.args.unit)
                if r.isError() == True:
                    raise Exception(str(r))
            else:
                raise AttributeError("Unknown --item specified ({})".format(self.args.item))
            TLog.success("Values successfully written")
        except:
            self.result.exception()
        finally:
            c.close()
