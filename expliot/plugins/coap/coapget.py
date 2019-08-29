"""Test for getting data from a CoAP device."""
from coapthon.messages.response import Response

from expliot.core.protocols.internet.coap import CoapClient, handle_response
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.coap import REFERENCE


# pylint: disable=protected-access
class CoapGet(Test):
    """Test for getting data from a CoAP device."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="get",
            summary="CoAP GET",
            descr="This test allows you to send a CoAP GET request (Message) "
            "to a CoAP server on a specified resource path.",
            author="Fabian Affolter",
            email="fabian@affolter-engineering.ch",
            ref=REFERENCE,
            category=TCategory(TCategory.COAP, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="The hostname/IP address of the target CoAP Server",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=5683,
            type=int,
            help="The port number of the target CoAP Server. Default is 5683",
        )
        self.argparser.add_argument(
            "-u",
            "--path",
            default="/.well-known/core",
            help="Resource URI path of the GET request. Default is discover URI path /.well-known/core",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Sending GET request for URI path {} to CoAP server {} on port {}".format(
                self.args.path, self.args.rhost, self.args.rport
            )
        )
        coap_client = CoapClient(self.args.rhost, self.args.rport)
        response = coap_client.get(
            self.args.path, proxy_uri=None, callback=None, timeout=10
        )

        if isinstance(response, Response):
            data = handle_response(response)
            TLog.success("Response details: {}".format(data))
            self.result.setstatus(passed=True)
        else:
            reason = "No valid response. Response class: {}".format(
                response.__class__.__name__
            )
            self.result.setstatus(passed=False, reason=reason)

        coap_client.stop()
