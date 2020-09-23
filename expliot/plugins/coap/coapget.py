"""Test for getting data from a CoAP device."""

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
class CoapGet(Test):
    """
    Test for getting data from a CoAP device.

    Output Format:
    [
        {
            "response_code": "2.05 Content",
            "response_payload": "Foo bar"
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="get",
            summary="CoAP GET",
            descr="This test allows you to send a CoAP GET request (Message) "
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
            help="Resource URI path of the GET request. Default "
                 "is discover URI path {}".format(ROOTPATH),
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Sending GET request for URI Path ({}) "
            "to CoAP Server {} on port {}".format(
                self.args.path,
                self.args.rhost,
                self.args.rport
            )
        )
        try:
            client = CoapClient(self.args.rhost, port=self.args.rport)
            response = client.get(path=self.args.path)
            if not response.code.is_successful():
                self.result.setstatus(
                    passed=False,
                    reason="Error Response: ({})".format(
                        response.code
                    )
                )
                return
            self.output_handler(
                response_code=str(response.code),
                response_payload=response.payload
            )
        except:  # noqa: E722
            self.result.exception()
