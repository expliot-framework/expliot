Zigbee
======

ZigBee Auditor - XA device is a tool developed for professionals working with 
ZigBee network as developers, auditors, and cybersecurity professionals. 
ZigBee Auditor - XA comes with an on-board antenna that provides indispensable
100m signal range for network auditing and scanning task. To use ZigBee Auditor,
you need to install EXPLIoT, an open source framework for security testing and 
exploiting IoT. 
ZigBee Auditor provides ZigBee network scanning, packet sniffing, and packet 
replay functionality.

.. note:: 
   All ZigBee Auditor plugins need root privileges to access lowlevel usb 
   driver.
   If you are seeing permission issues, kindly add a udev rule for your user 
   for the ZigBee Auditor device.


zbauditor.generic.devinfo
-------------------------

This plugin displays information about ZigBee Auditor hardware that is used
with framework, information like device name, device firmware revision and
services that supported by this device.

**Usage details:**

.. code-block:: console

   ef> run zbauditor.generic.devinfo -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run zbauditor.generic.devinfo
  [...]
  [*] Zigbee Auditor Details:
  [*] Device Name      : ZigBee Auditor
  [*] FW Revision      : 1.0.0
  [*]
  [*] Services:
  [*] 	 GET_FW_REV       : True
  [*] 	 GET_FW_SERV      : True
  [*] 	 CHANNEL_CHNG     : True
  [*] 	 MAC_ON_OFF       : True
  [*] 	 802154_SNIFF     : True
  [*] 	 802154_INJECT    : True
  [*] 	 802154_NWK_SCAN  : True
  [*] 	 SUPP_FREQ_2400   : True
  [*]
  [+] Test zbauditor.generic.devinfo passed

zbauditor.generic.nwkscan
-------------------------

This plugin scans 2.4 GHz network for active IEEE 802.15.4 and Zigbee devices
by sending IEEE 802.15.4 beacon requests on selected channels and save result
in specified log file.

**Usage details:**

.. code-block:: console

   ef> run zbauditor.generic.nwkscan -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run zbauditor.generic.nwkscan -s 11 -e 26 -f ./zigbee_nwkscan.log
  [...]
  [*] Start Channel: (11)
  [*] End Channel  : (26)
  [*] Log File     : (./zigbee_nwkscan.log)
  [*]
  [*] Devices found     1
  [*] Device Number    : 1
  [*] Channel          : 21
  [*] Source Address   : 0x0
  [*] Source PAN ID    : 0x1234
  [*] Extended PAN ID (Device Address): ['0x0', '0x12', '0x34', '0x56', '0x78', '0x90', '0xab', '0xcd']
  [*] Pan Coordinator  : True
  [*] Permit Joining   : False
  [*] Router Capacity  : True
  [*] Device Capacity  : True
  [*] Protocol Version : 2
  [*] Stack Profile    : 2
  [*] LQI              : 160
  [*] rssi             : -53
  [*]
  [*] Scan duration     6.543011665344238
  [*]
  [+] Test zbauditor.generic.nwkscan passed

zbauditor.generic.sniffer
-------------------------

This plugin captures IEEE 802.15.4 packets on a specified channel and saves
them in pcap format.

**Usage details:**

.. code-block:: console

   ef> run zbauditor.generic.sniffer -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run zbauditor.generic.sniffer -c 25 -f ../1450.pcap
  [...]
  [*] Channel      : (25)
  [*] File         : (../1450.pcap)
  [*] Count        : (65535)
  [*] Time-Out     : (0)
  [*]

  ef> run zbauditor.generic.sniffer -c 25 -f ../1500.pcap -n 10
  [...]
  [*] Channel      : (25)
  [*] File         : (../1500.pcap)
  [*] Count        : (10)
  [*] Time-Out     : (0)
  [*]
  [*] Packet Received: (10)
  [*] Packet Transmit: (0)
  [+] Test zbauditor.generic.sniffer passed

  ef> run zbauditor.generic.sniffer -c 25 -f ../1530.pcap -t 10
  [...]
  [*] Channel      : (25)
  [*] File         : (../1530.pcap)
  [*] Count        : (65535)
  [*] Time-Out     : (10)
  [*]
  [*] Packet Received: (2)
  [*] Packet Transmit: (0)
  [+] Test zbauditor.generic.sniffer passed

zbauditor.generic.replay
------------------------

This plugin reads packets from the specified pcap file and replays them on the
specified channel ignores ACK packets. If destination PAN is specified, plugin
transmits packets with matching destination PAN.

**Usage details:**

.. code-block:: console

   ef> run zbauditor.generic.replay -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run zbauditor.generic.replay -c 25 -f ../0500.pcap
  [...]
  [*] Channel      : (25)
  [*] File         : (../0500.pcap)
  [*] Delay (seconds): (0.2)
  [*]
  [*] Packet Received: (0)
  [*] Packet Transmit: (31)
  [+] Test zbauditor.generic.replay passed


  ef> run zbauditor.generic.replay -c 25 -f ../0500.pcap -p 0x1234
  [...]
  [*] Channel      : (25)
  [*] File         : (../0500.pcap)
  [*] Delay (seconds): (0.2)
  [*] Destination PAN: (0x1234)
  [*]
  [*] Packet Received: (0)
  [*] Packet Transmit: (24)
  [+] Test zbauditor.generic.replay passed
