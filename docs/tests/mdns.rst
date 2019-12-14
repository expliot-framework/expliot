mDNS
====

Devices which are supporting `mDNS <https://en.wikipedia.org/wiki/Multicast_DNS>`_
can be found in the local network without additional configuration. Multicast
DNS is a zero-configuration service and is used in various IoT products.

mdns.generic.discover
---------------------

This test is checking the local network for devices with enabled mDNS.

**Usage details:**

.. code-block:: console

   ef> run mdns.generic.discover -h

Examples
^^^^^^^^

The output of a local network can look like the sample shown below.

.. code-block:: console

   ef> run mdns.generic.discover
   [...]
   [*] Search local network for devices which are discoverable
   [+] Chromecast-afraf32._googlecast._tcp.local. - 192.168.0.172:8009
   [+] TRADFRI gateway._hap._tcp.local. - 192.168.0.160:80
   [+] b4d1._http._tcp.local. - 192.168.0.121:80
   [+] hassio._sftp-ssh._tcp.local. - 192.168.0.192:22
   [+] Test mdns.generic.discover Passed
