mDNS
====

Devices that support `mDNS <https://en.wikipedia.org/wiki/Multicast_DNS>`_
can be found in the local network without additional configuration. Multicast
DNS is a zero-configuration service and is used in various IoT products.

mdns.generic.discover
---------------------

This plugin scans the local network for devices with enabled mDNS.

**Usage details:**

.. code-block:: console

   ef> run mdns.generic.discover -h

Examples
^^^^^^^^

Scan for all supported discoverable devices on the local network. You can also
use the ``-v`` option to see which device type is being scanned at any moment.

.. code-block:: console

   ef> run mdns.generic.discover
   [...]
   [*] Search local network for mDNS enabled devices
   [+] Device 1
   [+]   (name=foobar._http._tcp.local.)
   [+]   (address=192.168.0.20)
   [+]   (port=80)
   [+]   (server=foobar.local.)
   [+]   (type=_http._tcp.local.)
   [+]   (priority=0)
   [+]   (weight=0)
   [+]   (properties={b'path': b'/conf/authentication.htm'})
   [+]
   [+] Device 2
   [+]   (name=HP LaserJet 5081 @ myprinter._ipp._tcp.local.)
   [+]   (address=192.168.0.56)
   [+]   (port=631)
   [+]   (server=myprinter.local.)
   [+]   (type=_ipp._tcp.local.)
   [+]   (priority=0)
   [+]   (weight=0)
   [+]   (properties={b'txtvers': b'1', b'qtotal': b'1', b'rp': b'printers/HP_LaserJet_5081', b'ty': b'HP LaserJet 5081 Foomatic/foobla-y2 (recommended)', b'adminurl': b'https://myprinter.local:631/printers/HP_LaserJet_5081', b'priority': b'0', b'product': b'(HP LaserJet 5081)', b'pdl': b'application/octet-stream,application/pdf,application/postscript,image/jpeg,image/png,image/pwg-raster,image/urf', b'URF': b'DM3', b'UUID': b'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', b'TLS': b'1.2', b'printer-state': b'3', b'printer-type': b'0xXXXXXX'})
   [+]
   [+] Total devices discovered = 2
   [+] Test mdns.generic.discover passed


Scan for a specific discoverable device type from the supported devices (The next
example shows how to get the list of supported device types).

.. code-block:: console

   ef> run mdns.generic.discover -d printer -v
   [...]
   [*] Search local network for mDNS enabled devices
   [?] Looking for printer devices
   [+] Device 1
   [+]   (name=HP LaserJet 4040 @ myprinter2._printer._tcp.local.)
   [+]   (address=192.168.0.78)
   [+]   (port=0)
   [+]   (server=myprinter2.local.)
   [+]   (type=_printer._tcp.local.)
   [+]   (priority=0)
   [+]   (weight=0)
   [+]   (properties={})
   [+]
   [+] Total devices discovered = 1
   [+] Test mdns.generic.discover passed


Output the list of all EXPLIoT supported mDNS discoverable device types

.. code-block:: console

   ef> run mdns.generic.discover -l
   [...]
   [?] Supported Device types
   [+] aidroid
   [+] aiplay
   [+] airport
   [+] amzn_wplay
   [+] android_tv_remote
   [+] apple_tv
   [+] arduino
   [+] axis_video
   [+] brew_pi
   [+] cloud
   [...]
   [+] soundtouch
   [+] spotify_connect
   [+] ssh
   [+] teamviewer
   [+] telnet
   [+] tivo_remote
   [+] touh_able
   [+] tunnel
   [+] ultimaker
   [+] workstation
   [+] Test mdns.generic.discover passed
