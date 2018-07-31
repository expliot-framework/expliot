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

from binascii import hexlify
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.protocols.hardware.can import CanBus #, CanMessage

class CANRead(Test):

    def __init__(self):
        super().__init__(name     = "CANbus read",
                         summary  = "Read frames from CANBus",
                         descr    = """This plugin allows you to read message(s) from the CANBus. As of now it 
                                       uses socketcan but if you want to extend it to other interfaces, just 
                                       open an issue on the official expliot project repository""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://en.wikipedia.org/wiki/CAN_bus"],
                         category = TCategory(TCategory.CAN, TCategory.HW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-i", "--iface", default="vcan0", help="Interface to use. Default is vcan0")
        self.argparser.add_argument("-a", "--arbitid", type=lambda x: int(x,0),
                                    help="Show messages of the specified arbitration ID only. For hex value prefix it with 0x")
        self.argparser.add_argument("-c", "--count", type=int, default=10,
                                    help="Specify the count of messages to read from the CANBus. Default is 10")
        self.argparser.add_argument("-t", "--timeout", type=float,
                                    help="""Specify the time, in seconds, to wait for each read. Default is to wait 
                                            forever. You may use float values as well i.e. 0.5""")

    def execute(self):
        TLog.generic("Reading ({}) messages from CANbus on interface({})".format(self.args.count, self.args.iface))

        bus = None
        try:
            if self.args.count < 1:
                raise ValueError("Illegal count value {}".format(self.args.count))
            bus = CanBus(bustype="socketcan", channel=self.args.iface)
            for cnt in range(1, self.args.count + 1):
                m = bus.recv(timeout=self.args.timeout)
                if m is None:
                    raise TimeoutError("Timed out while waiting for CAN message")
                if self.args.arbitid:
                    if self.args.arbitid == m.arbitration_id:
                        TLog.success("(msg={})(data={})".format(cnt, hexlify(m.data).decode()))
                else:
                    TLog.success("(msg={})(arbitration_id=0x{:x})(data={})".format(cnt,
                                                                                   m.arbitration_id,
                                                                                   hexlify(m.data).decode()))
        except:
            self.result.exception()
        finally:
            if bus:
                bus.shutdown()