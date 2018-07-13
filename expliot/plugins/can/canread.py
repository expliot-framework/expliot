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
                         descr    = """This test case allows you to read messages from the CANBus. As of now it 
                                       uses socketcan but if you want to extend it to other interfaces, just 
                                       open an issue on the official project repository""",
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

    def execute(self):
        TLog.generic("Reading ({}) messages from CANbus on interface({})".format(self.args.count, self.args.iface))

        bus = None
        try:
            bus = CanBus(bustype="socketcan", channel=self.args.iface)
            cnt = 0
            for m in bus:
                if cnt >= self.args.count:
                    break
                if self.args.arbitid:
                    if self.args.arbitid == m.arbitration_id:
                        cnt += 1
                        TLog.success("(data={})".format(hexlify(m.data).decode()))
                else:
                    cnt += 1
                    TLog.success("(arbitration_id=0x{:x})(data={})".format(m.arbitration_id, hexlify(m.data).decode()))
        except:
            self.result.exception()
        finally:
            bus.shutdown()