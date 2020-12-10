"""Test for Sending POST request to a CoAP device."""

from expliot.core.tests.test import (
    Test,
    TCategory,
    TTarget,
    TLog,
)

from expliot.core.protocols.internet.coap import (
    CoapClient,
    ROOTPATH,
    COAP_PORT,
)


# pylint: disable=bare-except
class CoapPost(Test):
    """
    Test for POSTing data on a specified resource path on a CoAP device.

    Output Format:
    [
        {
            "response_code": 69  # Ex. 69=0b01000101 (0b010=2, 0b00101=5)
            "response_code": "2.05 Content",
            "response_payload": "Foo bar" # or "" if no payload in response
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="post",
            summary="CoAP POST request",
            descr="This test allows you to send a CoAP POST request (Message) "
                  "to a CoAP server on a specified resource path.",
            author="Aseem Jakhar",
            email="aseem@expliot.io",
            ref=["https://tools.ietf.org/html/rfc7252"],
            category=TCategory(TCategory.COAP, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="Hostname/IP address of the target CoAP Server",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=COAP_PORT,
            type=int,
            help="Port number of the target CoAP Server. Default "
                 "is {}".format(COAP_PORT),
        )
        self.argparser.add_argument(
            "-u",
            "--path",
            default=ROOTPATH,
            help="Resource URI path of the POST request. Default "
                 "is URI path {}".format(ROOTPATH),
        )
        self.argparser.add_argument(
            "-d",
            "--data",
            required=True,
            help="The POST data/payload to be sent to the CoAP server",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Sending POST request to URI Path ({}) "
            "to CoAP Server {} port {} with data ({})".format(
                self.args.path,
                self.args.rhost,
                self.args.rport,
                self.args.data
            )
        )
        try:
            client = CoapClient(self.args.rhost, port=self.args.rport)
            response = client.post(
                path=self.args.path,
                payload=self.args.data.encode()
            )
            if not response.code.is_successful():
                self.result.setstatus(
                    passed=False,
                    reason="Error Response: {}".format(
                        CoapClient.response_dict(response)
                    )
                )
                return
            self.output_handler(
                response_code=int(response.code),
                response_code_str=str(response.code),
                response_payload=response.payload
            )
        except:  # noqa: E722
            self.result.exception()
