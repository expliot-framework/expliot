"""Test for getting data from a CoAP device."""

from expliot.core.tests.test import (
    Test,
    TCategory,
    TTarget,
    TLog,
)

from expliot.core.protocols.internet.coap import (
    CoapClient,
    WKRPATH,
    COAP_PORT,
    WKResource,
)


class Discover(Test):
    """Test for discovering and listing resources available on a CoAP server"""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="discover",
            summary="CoRE Resource Discovery",
            descr="This test allows you to discover and list the well-known "
                  "resources advertised as CoRE link format on a CoAP server.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://tools.ietf.org/html/rfc6690"],
            category=TCategory(TCategory.COAP, TCategory.SW, TCategory.DISCOVERY),
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

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Sending GET request to CoRE discovery URI Path ({}) "
            "to CoAP Server {} on port {}".format(
                WKRPATH,
                self.args.rhost,
                self.args.rport
            )
        )
        count = 0
        resources = []
        client = CoapClient(self.args.rhost, self.args.rport)
        response = client.get(path=WKRPATH)
        if not response.code.is_successful():
            self.result.setstatus(
                passed=False,
                reason="Error Response: ({})".format(
                    response.code
                )
            )
            return

        for link in response.payload.split(b","):
            count += 1
            resource = WKResource(link)
            rdict = resource.linkdict()
            self.output_handler(**rdict)
        self.output_handler(total_resources=count)
