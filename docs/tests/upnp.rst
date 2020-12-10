UPnP
====

`Universal Plug aNd Play (UPnP) <https://en.wikipedia.org/wiki/Universal_Plug_and_Play>`_ is
a set of protocols that allows devices to automate discovery and communication. It helps in
identifying devices and their services in a network from IoT security assessment perspective.



upnp.generic.discover
---------------------

This plugin attempts to discover devices within a network and provides details about those devices.

.. note::

    The --verbose option displays the raw XML responses received from the devices in addition
    to the other information.

**Usage details:**

.. code-block:: console

   ef> run upnp.generic.discover -h


**Example:**

Discover UPNP devices on the local network and get their details.
Limit the discovery to 5 seconds.

.. code-block:: console

   ef> run upnp.generic.discover --timeout 5
   [...]
   [*] Search local network for UPNP enabled devices
   [*]
   [+] Device 1:
   [+]
   [+] host: 192.168.12.11
   [+] port: 1900
   [+] friendly_name: WFADevice
   [+] type: urn:schemas-wifialliance-org:device:WFADevice:1
   [+] base_url: http://192.168.12.11:1900
   [+] services:
   [+]     name: urn:schemas-wifialliance-org:service:WFAWLANConfig:1
   [+]     type: WFAWLANConfig
   [+]     version: 1
   [+]     id: urn:wifialliance-org:serviceId:WFAWLANConfig1
   [+]     scpd_url: http://192.168.12.11:1900/wlanconfig.xml
   [+]     control_url: /controls?WLANConfig
   [+]     event_sub_url: /events?WLANConfig
   [+]     base_url: http://192.168.12.11:1900
   [+]     actions:
   [+]         name: ModAPSettings
   [+]         arguments:
   [+]             name: NewAPSettings
   [+]             direction: in
   [+]             return_value: None
   [+]             related_state_variable: APSettings
   [+]     state_variables:
   [+]       WLANResponse
   [+]       WLANEventType
   [...]
   [+] total_devices_discovered: 4
   [+]
   [+] Test upnp.generic.discover passed