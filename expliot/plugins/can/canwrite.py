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
from expliot.core.protocols.hardware.can import CanBus, CanMessage

class CANWrite(Test):

    def __init__(self):
        super().__init__(name     = "CANbus write",
                         summary  = "Send a data frame on CANBus",
                         descr    = """This test case allows you to write a message on the CANBus i.e. send a data 
                                       frame. As of now it uses socketcan but if you want to extend it to other 
                                       interfaces, just open an issue on the official project repository""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://en.wikipedia.org/wiki/CAN_bus"],
                         category = TCategory(TCategory.CAN, TCategory.HW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-i", "--iface", default="vcan0", help="Interface to use. Default is vcan0")
        self.argparser.add_argument("-a", "--arbitid", required=True, type=lambda x: int(x,0),
                                    help="Specify the arbitration ID. For hex value prefix it with 0x")
        self.argparser.add_argument("-e", "--exid", action="store_true",
                                    help="Speficy this option if using extended format --arbitid")
        self.argparser.add_argument("-d", "--data", required=True,
                                    help="Specify the data to write, as hex stream, without the 0x prefix")

    def execute(self):
        TLog.generic("Writing to CANbus on interface({}), arbitration id({}), extended?({}) data({})".format(self.args.iface,
                                                                                                             self.args.arbitid,
                                                                                                             self.args.exid,
                                                                                                             self.args.data))
        bus = None
        try:
            bus = CanBus(bustype="socketcan", channel=self.args.iface)
            msg = CanMessage(arbitration_id=self.args.arbitid,
                         extended_id=self.args.exid,
                         data=list(bytes.fromhex(self.args.data)))
            bus.send(msg)
        except:
            self.result.exception()
        finally:
            bus.shutdown()