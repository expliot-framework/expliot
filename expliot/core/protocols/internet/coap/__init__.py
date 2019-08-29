"""Wrapper for the CoAP communication."""
import logging

# pylint: disable=protected-access
from coapthon.client.helperclient import HelperClient
from coapthon.defines import Codes, Types

logging.disable(logging.CRITICAL)


class CoapClient(HelperClient):
    """A wrapper around HelperClient in CoAPthon."""

    def __init__(self, host, port):
        """Initialize the client."""
        super().__init__(server=(host, port))


def handle_response(response):
    """Re-work the content of a response."""
    options = []

    for option in response._options:
        option_data = {
            "name": option.name,
            "value": option.value,
            "length": option.length,
            "is_safe": option.is_safe(),
        }
        options.append(option_data)

    data = {
        "version": response.version,
        "source": response._source,
        "destination": response._destination,
        "type": next(state for state, code in Types.items() if code == response._type),
        "mid": response._mid,
        "code": 0 if response._code is None else Codes.LIST[response._code].name,
        "token": response._token,
        "options": options,
        "payload": response._payload,
    }
    return data
