"""Test for sending data to a CoAP device."""
from coapthon.defines import Content_types
from coapthon.messages.response import Response

from expliot.core.protocols.internet.coap import CoapClient, handle_response
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.coap import REFERENCE


class CoapPost(Test):
    """Test for sending data to a CoAP device."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="post",
            summary="CoAP POST",
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
            "-u", "--path", required=True, help="Resource URI path for the POST request"
        )
        self.argparser.add_argument(
            "-l", "--payload", required=True, help="Payload of the POST request"
        )

    # pylint: disable=protected-access
    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Sending POST request for URI path {} to CoAP server {} on port {} with payload {}".format(
                self.args.path, self.args.rhost, self.args.rport, self.args.payload
            )
        )
        coap_client = CoapClient(self.args.rhost, self.args.rport)
        content_type = {"content_type": Content_types["application/link-format"]}

        response = coap_client.put(
            self.args.path,
            self.args.payload,
            proxy_uri=None,
            callback=None,
            timeout=10,
            **content_type,
        )

        if isinstance(response, Response):
            if response._code == 133:
                reason = "Method not allowed"
                self.result.setstatus(passed=False, reason=reason)
                coap_client.stop()
                return

            if response._code == 132:
                reason = "URI not found"
                self.result.setstatus(passed=False, reason=reason)
                coap_client.stop()
                return

            data = handle_response(response)
            TLog.success("Response details: {}".format(data))
            self.result.setstatus(passed=True)
        else:
            reason = "No valid response. Response class: {}".format(
                response.__class__.__name__
            )
            self.result.setstatus(passed=False, reason=reason)

        coap_client.stop()
