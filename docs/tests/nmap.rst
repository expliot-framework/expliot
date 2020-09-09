nmap
====

`nmap <https://nmap.org>`_ allows to scan for the hosts, open ports and other
details in a network. It's required that you have the ``nmap`` binary present
in your PATH.

.. note:: Certain nmap options require you to use root privileges to run.

nmap.generic.cmd
-----------------

As default ``-oX`` is used for all scans.

**Usage details:**

.. code-block:: console

   ef> run nmap.generic.cmd -h


**Example:**

Scan the local network 192.168.0.0/24 with ``-sP`` to skip the port scan part.

.. code-block:: console

   ef> run nmap.generic.cmd -a "-sP 192.168.0.0/24"
   [...]
   [+] nmap arguments = (-sP 192.168.0.0/24)
   [+] nmaprun:
   [+]   @scanner: nmap
   [+]   @args: nmap -oX - -sP 192.168.0.0/24
   [+]   @start: 1599642315
   [+]   @startstr: Wed Sep  9 11:05:15 2020
   [+]   @version: 7.80
   [+]   @xmloutputversion: 1.04
   [+]   verbose:
   [+]     @level: 0
   [+]   debugging:
   [+]     @level: 0
   [+]   host:
   [+]       status:
   [+]         @state: up
   [+]         @reason: arp-response
   [+]         @reason_ttl: 0
   [+]       address:
   [+]           @addr: 192.168.0.1
   [+]           @addrtype: ipv4
   [+]           @addr: 90:55:21:12:6E:DD
   [+]           @addrtype: mac
   [+]           @vendor: affolter engineering networks
   [+]       hostnames: None
   [...]
   [+] Test nmap.generic.cmd passed
