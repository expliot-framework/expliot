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

from time import time
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from logging import ERROR, getLogger
from pyftdi.i2c import I2cController, I2cNackError
import binascii

class I2cScan(Test):
    def __init__(self):
        super().__init__(name     = "scan",
                         summary  = "I2C Scanner",
                         descr    = """This plugin scans the I2C bus and displays all the address connected to the bus""",
                         author   = "Arun Magesh",
                         email    = "arun.m@payatu.com",
                         ref      = ["https://github.com/eblot/pyftdi"],
                         category = TCategory(TCategory.I2C, TCategory.HW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))


        self.argparser.add_argument("-u", "--url", default="ftdi:///1",
                                    help="""URL of the connected FTDI device. Default is "ftdi:///1". For more details
                                            on the URL scheme check https://eblot.github.io/pyftdi/urlscheme.html""")

    def execute(self):
        TLog.generic("Scanning for I2C devices...")
        passed = 0 
        fail = 0 
        try:
            i2c = I2cController()
            getLogger('pyftdi.i2c').setLevel(ERROR)
            try:
            	i2c.set_retry_count(1)
            	i2c.configure(self.args.url)
            	for addr in range(i2c.HIGHEST_I2C_ADDRESS+1):
            		port = i2c.get_port(addr)
            		try:
            			port.read(0)
            			print(hex(addr))
            			passed = passed + 1
            		except I2cNackError:
            			fail = fail + 1 
            finally:
            	i2c.terminate()
            TLog.success("Done. Found {} and not found {}  ".format(str(passed),str(fail)))
        except:
            self.result.exception()


