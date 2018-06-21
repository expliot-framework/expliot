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

class MBTcpRead(Test):
    COIL = 0
    DINPUT = 1
    HREG = 2
    IREG = 3
    ITEMS = ["coil", "discrete input", "holding register", "input register"]
    def __init__(self):
        super().__init__(name     = "Modbus TCP Read",
                         summary  = "Read coil and register values from a Modbus server (slave)",
                         descr    = """This plugin reads the item (coil, discrete input, holding and input register) 
                                       values from a Modbus server""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://en.wikipedia.org/wiki/Modbus", "http://www.modbus.org/specs.php"],
                         category = TCategory(TCategory.MODBUSTCP, TCategory.SW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-r", "--rhost", required=True, help="hotname/IP address of the Modbus server")
        self.argparser.add_argument("-p", "--rport", default=502, type=int,
                                    help="Port number of the Modbus server. Default is 502")
        self.argparser.add_argument("-i", "--item", default=0, type=int,
                                    help="""The item to read from. {} = {},
                                            {} = {}, {} = {}, {} = {}. Default is {}""".format(self.COIL,
                                                                                               self.ITEMS[self.COIL],
                                                                                               self.DINPUT,
                                                                                               self.ITEMS[self.DINPUT],
                                                                                               self.HREG,
                                                                                               self.ITEMS[self.HREG],
                                                                                               self.IREG,
                                                                                               self.ITEMS[self.IREG],
                                                                                               self.COIL))
        self.argparser.add_argument("-a", "--address",default=0, type=int, help="The start address of item to read from")
        self.argparser.add_argument("-c", "--count",default=1, type=int, help="The count of items to read. Default is 1")
        self.argparser.add_argument("-u", "--unit", default=1, type=int,
                                    help="The Unit ID of the slave on the server to read from")

    def execute(self):
        c = ModbusTcpClient(self.args.rhost, port=self.args.rport)
        try:
            values = None
            # Check what to read i.e. coils, holding registers etc
            if self.args.item < 0 or self.args.item >= len(self.ITEMS):
                raise AttributeError("Unknown --item specified ({})".format(self.args.item))

            TLog.generic("Sending read command to Modbus Server ({}) on port ({})".format(self.args.rhost,
                                                                                          self.args.rport))
            TLog.generic("(item={})(address={})(count={})(unit={})".format(self.ITEMS[self.args.item],
                                                                           self.args.address,
                                                                           self.args.count,
                                                                           self.args.unit))
            c.connect()
            if self.args.item == self.COIL:
                r = c.read_coils(self.args.address, self.args.count, unit=self.args.unit)
                if r.isError() == True:
                    raise Exception(str(r))
                values = r.bits
            elif self.args.item == self.DINPUT:
                # below r = class pymodbus.bit_read_message.ReadDiscreteInputsResponse
                r = c.read_discrete_inputs(self.args.address, self.args.count, unit=self.args.unit)
                if r.isError() == True:
                    raise Exception(str(r))
                values = r.bits
            elif self.args.item == self.HREG:
                # below r = class pymodbus.register_read_message.ReadHoldingRegistersResponse
                r = c.read_holding_registers(self.args.address, self.args.count, unit=self.args.unit)
                if r.isError() == True:
                    raise Exception(str(r))
                values = r.registers
            elif self.args.item == self.IREG:
                # below r = class pymodbus.register_read_message.ReadInputRegistersResponse
                r = c.read_input_registers(self.args.address, self.args.count, unit=self.args.unit)
                if r.isError() == True:
                    raise Exception(str(r))
                values = r.registers
            else:
                raise AttributeError("Unknown --item specified ({})".format(self.args.item))
            for i in range(0, self.args.count):
                TLog.success("({}[{}]={})".format(self.ITEMS[self.args.item], self.args.address + i, values[i]))
        except:
            self.result.exception()
        finally:
            c.close()

