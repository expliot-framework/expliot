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
from expliot.core.protocols.hardware.spi.ftdi import FlashManager

class SPIFlashWrite(Test):
    def __init__(self):
        super().__init__(name     = "SPI Flash Write",
                         summary  = "write data to a SPI Flash chip",
                         descr    = """This plugin writes data to a serial flash chip that implements SPI protocol.
                                       It needs an FTDI interface to write data to the target flash chip. You can buy 
                                       an FTDI device online. If you are interested we have an FTDI based product - 
                                       Expliot Nano which you can order online from www.expliot.io
                                       This plugin uses pyspiflash package which in turn uses pyftdi python driver 
                                       for ftdi chips. For more details on supported flash chips check the readme at 
                                       https://github.com/eblot/pyspiflash. Thank you Emmanuel Blot for pyspiflash. 
                                       You may want to run it as root in case you get a USB error related to langid""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://github.com/eblot/pyspiflash"],
                         category = TCategory(TCategory.SPI, TCategory.HW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-a", "--addr", default=0, type=int,
                                    help="""Specify the start address where data is to be written. Default is 0""")
        self.argparser.add_argument("-u", "--url", default="ftdi:///1",
                                    help="""URL of the connected FTDI device. Default is "ftdi:///1". For more details
                                            on the URL scheme check https://eblot.github.io/pyftdi/urlscheme.html""")
        self.argparser.add_argument("-f", "--freq", type=int,
                                    help="""Specify a frequency in Hz(example: 1000000 for 1 MHz). If not, specified, 
                                            default frequency of the device is used. You may want to decrease the 
                                            frequency if you keep seeing FtdiError:UsbError.""")
        self.argparser.add_argument("-d", "--data", help="Specify the data to write, as hex stream, without the 0x prefix")

        self.argparser.add_argument("-r", "--rfile", help="""Specify the file path from where data is to be read. This
                                                             takes precedence over --data option i.e if both options 
                                                             are specified --data would be ignored""")

    def execute(self):
        TLog.generic("Writing data to spi flash at address({}) using device({})".format(self.args.addr,
                                                                                        self.args.url))
        d = None
        try:
            stime = None
            etime = None
            data  = None
            saddr = self.args.addr
            if self.args.rfile:
                TLog.trydo("Reading data from the file ({})".format(self.args.rfile))
                f = open(self.args.rfile, "r+b")
                data = f.read()
                f.close()
            elif self.args.data:
                data = bytes.fromhex(self.args.data)
            else:
                raise AttributeError("Specify either --data or --rfile (but not both)")

            d = FlashManager.get_flash_device(self.args.url, freq=self.args.freq)
            TLog.success("(chip found={})(chip size={} bytes)(using frequency={})".format(d,
                                                                                          len(d),
                                                                                          int(d.spi_frequency)))

            ln = len(data)
            eaddr = saddr + ln - 1
            TLog.trydo("Writing {} byte(s) at start address {}".format(ln, saddr))
            if self.args.addr + ln > len(d):
                raise IndexError("Length is out of range of the chip size")
            # We can't write on any arbitrary address for an aritrary length unless it is aligned to the page size
            # Get erase page size, start/end enclosing page addresses and length
            esz = d.get_erase_size()
            spaddr = saddr - saddr % esz
            epaddr = eaddr + esz - (eaddr % esz) - 1
            pln = epaddr - spaddr + 1
            TLog.trydo("Page aligned start address({}) end address({}) lenght({})".format(spaddr, epaddr, pln))
            # Backup the data from chip
            stime = time()
            tmpdata = d.read(spaddr, pln)
            etime = time()
            TLog.success("Backed up page aligned {} byte(s) from address {}. Time taken {} secs".format(pln,
                                                                                                        spaddr,
                                                                                                        round(etime - stime, 2)))
            tmpdata = tmpdata.tobytes()
            # We can only write on erased data
            # Now erase the enclosing pages (of the start and end addresses)
            d.unlock()
            stime = time()
            d.erase(spaddr, pln)
            etime = time()
            TLog.success("Erased {} byte(s) of data from address {}. Time taken {} secs".format(pln,
                                                                                                spaddr,
                                                                                                round(etime - stime, 2)))
            # Now overwrite with the updated data i.e. backedup data containing the changes
            wdata = tmpdata[0:saddr % esz] + data + tmpdata[saddr % esz + ln:]
            stime = time()
            d.write(spaddr, wdata)
            etime = time()
            TLog.success("wrote {} byte(s) of data from address {}. Time taken {} secs".format(pln,
                                                                                               spaddr,
                                                                                               round(etime - stime, 2)))
        except:
            self.result.exception()
        finally:
            FlashManager.close(d)
