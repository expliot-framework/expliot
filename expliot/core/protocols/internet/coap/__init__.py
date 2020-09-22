"""Wrapper for the CoAP communication."""
import logging
import asyncio
from collections import namedtuple
from aiocoap import GET, POST, PUT, DELETE, Context, Message

COAP_STR = "coap"
COAP_PORT = 5683
ROOTPATH = "/"
WKRPATH = "/.well-known/core"

logging.getLogger("coap").setLevel(logging.CRITICAL + 1)


class WKResource:
    """
    A resource on the CoAP server as advertised on the "/.well-known/core
    path.
    """
    def __init__(self, link):
        self.path = None
        self.title = None
        self.iface = None
        self.rt = None
        self.ct = None
        self.sz = None
        self.unknown = []

        if link:
            self.parse(link)

    def parse(self, link):
        if link.__class__ == bytes:
            link = link.decode()
        for item in link.split(";"):
            attr = item.split("=")
            if len(attr) == 1:
                if attr[0][0] == "<" and attr[0][-1] == ">":
                    self.path = attr[0][1:-1]
                else:
                    self.unknown.append(attr[0])
            elif len(attr) == 2:
                if attr[0] == "title":
                    self.title = attr[1]
                elif attr[0] == "if":
                    self.iface = attr[1]
                elif attr[0] == "rt":
                    self.rt = attr[1]
                elif attr[0] == "ct":
                    self.ct = attr[1]
                elif attr[0] == "sz":
                    self.sz = attr[1]
                else:
                    self.unknown.append(item)

    def link(self):
        linkstr = "<{}>".format(self.path)
        if self.title:
            linkstr += ";title={}".format(self.title)
        if self.iface:
            linkstr += ";if={}".format(self.iface)
        if self.rt:
            linkstr += ";rt={}".format(self.rt)
        if self.ct:
            linkstr += ";ct={}".format(self.ct)
        if self.sz:
            linkstr += ";sz={}".format(self.sz)
        return linkstr

    def linkdict(self):
        ldict = {"path": self.path}
        if self.title:
            ldict["title"] = self.title
        if self.iface:
            ldict["if"] = self.iface
        if self.rt:
            ldict["rt"] = self.rt
        if self.ct:
            ldict["ct"] = self.ct
        if self.sz:
            ldict["sz"] = self.sz
        return ldict


class CoapClient:
    """
    A CoAP Client Object
    """

    def __init__(self, host, port=COAP_PORT, secure=False):
        """
        Constructor for the CoapClient

        Args:
            host (str): The hostname or IP of the CoAP server
            port (int): The CoAP port number on the host
        Returns:
            Nothing
        """
        if not host:
            raise ValueError("Empty host!")
        self.host = host
        self.port = port


    def makeuri(self, path=None, secure=False):
        """
        Make a CoAP URI from the details provided

        Args:
            path (str): The resource path of the request
            secure (bool): Add s for secure or not
        Returns:
            str: The URI created using the parameters
        """
        scheme = COAP_STR
        if secure:
            scheme += "s"
        if not path:
            raise ValueError("Empty Resource Path!")
        if path[0] != "/":
            path = "/" + path
        return "{}://{}:{}{}".format(scheme, self.host, self.port, path)

    def request(self, method=GET, path=None, payload=b"", secure=True):
        """
        Wrapper on async_request() to make a sync request.

        Args:
            Check async_request()
        Returns:
            Check async_request()
        """
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(
            self.async_request(method=method, path=path, payload=payload, secure=secure)
        )
        loop.close()
        return response

    async def async_request(self, method=GET, path=None, payload=b"", secure=False):
        """
        Send a request to a CoAP server.

        Args:
            method (aiocoap.numbers.codes.Code): The request method e.g. GET
            path (str): The resource path of the request
            payload (bytes): The payload to send if any
            secure (bool): plain text (coap) or secure (coaps) request

        Returns:
            aiocoap.message.Message: Response message
        """
        uri = self.makeuri(path=path, secure=secure)
        # print("URI = ({})".format(uri))
        ctx = await Context.create_client_context()
        request = Message(code=method, uri=uri, payload=payload)
        response = await ctx.request(request).response
        await ctx.shutdown()
        return response

    def get(self, path=None, secure=False):
        """
        Wrapper on request() to make a GET request.

        Args:
            Check async_request()
        Returns:
            Check async_request()
        """
        return self.request(method=GET, path=path, secure=secure)

    def post(self, path=None, payload=b"", secure=False):
        """
        Wrapper on request() to make a POST request.

        Args:
            Check async_request()
        Returns:
            Check async_request()
        """
        return self.request(method=GET, path=path, payload=payload, secure=secure)

    def put(self, path=None, payload=b"", secure=False):
        """
        Wrapper on request() to make a PUT request.

        Args:
            Check async_request()
        Returns:
            Check async_request()
        """
        return self.request(method=GET, path=path, payload=payload, secure=secure)

    def delete(self, path=None, secure=False):
        """
        Wrapper on request() to make a DELETE request.

        Args:
            Check async_request()
        Returns:
            Check async_request()
        """
        return self.request(method=GET, path=path, secure=secure)

    def discover(self, secure=False):
        """
        Discover all resources available on the server. It does that
        by sending a GET request to /.well-known/core according to
        RFC 6690 - https://tools.ietf.org/html/rfc6690

        Args:
            Check async_request()
        Returns:
            list: A list of WKCResource objects corresponding to each
                  resource advertised by the CoAP server
        """
        response = self.request(path=WKCPATH, secure=secure)
        if not response.code.is_successful():
            # raise
            return None
