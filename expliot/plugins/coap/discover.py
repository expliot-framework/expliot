"""Test for getting data from a CoAP device."""

from expliot.core.tests.test import (
    Test,
    TCategory,
    TTarget,
    TLog,
)

from expliot.core.protocols.internet.coap import (
    CoapDiscovery,
    WKRPATH,
    COAP_PORT,
)


# pylint: disable=bare-except
class Discover(Test):
    """
    Test for discovering and listing resources available on a CoAP server

    Output Format:
    [
        {
            "path": "/foo", # Only Path key is mandatory.
            "ct": "0",
            "rt": "observe",
            "title": "Foo Bar Title"
        },
        #...
        {
            "path": "/bar", # Only Path key is mandatory.
            "sz": "0",
            "if": "Foo If",
        },
        # ...May be more than one resource entries. Please note
        # that only the "path" key is mandatory i.e. will be present
        # in all, other attributes may or may not be present depending
        # on what was advertised by the CoAP server
        {
            "total_resources": 35
        },

    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="discover",
            summary="CoRE Resource Discovery",
            descr="This test allows you to discover and list the well-known "
                  "resources advertised as CoRE link format on a CoAP server.",
            author="Aseem Jakhar",
            email="aseem@expliot.io",
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
        try:
            scanner = CoapDiscovery(self.args.rhost, port=self.args.rport)
            scanner.scan()
            resources = scanner.services()
            for resource in resources:
                self.output_handler(**resource)
            self.output_handler(total_resources=len(resources))
        except:  # noqa: E722
            self.result.exception()
