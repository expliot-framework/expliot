CoAP
====

`Constrained Application Protocol <(https://en.wikipedia.org/wiki/Constrained_Application_Protocol>`_
(CoAP) is a light weight network communication protocol used for constrained
devices. It is an IETF standard defined in `RFC 7252 <https://tools.ietf.org/html/rfc7252>`_
and is used in various IoT products.

coap.generic.get
----------------

This test allows you to send a CoAP GET request to a CoAP server on a specified
resource path and get the payload and various other details back.

**Usage details:**

.. code-block:: console

   ef> run coap.generic.get -h

Examples
^^^^^^^^

To get to know this plugin, you can use the ``coap-server`` which is part of
`libcoap <https://libcoap.net/>`_ or ``coapserver.py`` from
`CoAPthon <https://github.com/Tanganelli/CoAPthon>`_ (this is a dependency and
should be already available).

Start the server:

.. code-block:: bash

   $ coap-server -A 127.0.0.1 -p 5683

Check with ``nmap`` if the server is running.

.. code-block:: bash

   $ sudo nmap -p U:5683 -sU --script coap-resources localhost
   [...]
   PORT     STATE SERVICE
   5683/udp open  coap
   | coap-resources:
   |   /:
   |     ct: 0
   |     title: General Info
   |   /time:
   |     ct: 0
   |     if: clock
   |     obs,</async>;ct: 0
   |     rt: ticks
   |_    title: Internal Clock

   Nmap done: 1 IP address (1 host up) scanned in 0.49 seconds

``coap-client`` (also part of `libcoap <https://libcoap.net/>`_) can be used
if ``nmap`` is not present on your system.

.. code-block:: bash

   $ coap-client -m get coap://127.0.0.1/time
   Aug 29 22:54:10

The EXPLIoT command for this sample would look like the one below:

.. code-block:: bash

   $ expliot run coap.generic.get -r 127.0.0.1 -u time
   [...]
   [*] Sending GET request for URI path time to CoAP server 127.0.0.1 on port 5683
   [+] Response details: {'version': 1, 'source': ('127.0.0.1', 5683),
       'destination': None, 'type': 'ACK', 'mid': 4888, 'code': 'CONTENT',
       'token': 'ok', 'options': [{'name': 'ETag', 'value': b'\xf59Lg',
       'length': 4, 'is_safe': True}, {'name': 'Content-Type', 'value': 0,
       'length': 0, 'is_safe': True}, {'name': 'Max-Age', 'value': 1, 'length': 1,
       'is_safe': False}], 'payload': 'Aug 29 22:59:07'}
   [+] Test coap.generic.get Passed   [+] Test coap.generic.get Passed


coap.generic.post
-----------------

This test allows you to send a CoAP POST request to a CoAP server on a specified
resource path and payload.

**Usage details:**

.. code-block:: console

   ef> run coap.generic.post -h


coap.generic.sample
-------------------

This is just a sample plugin. It is intended for developers to understand
the structure of a plugin class and how to implement one.

**Usage details:**

.. code-block:: console

   ef> run coap.generic.sample -h
