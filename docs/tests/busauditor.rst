BusAuditor
======

BUS Auditor is a compact multi-protocol tool used for scanning and identifying
debugging and communication interfaces exposed on any hardware board. It can 
brute force several hardware protocols including JTAG, arm SWD, UART, and I2C.
The device has 16 channels, every channel can be used to interface with 
a pin-out on the target board.
Bus Auditor channels must be connected in a sequential range and specified by 
the start and end pin arguments.

.. note:: 
   All Bus Auditor plugins need root privileges to access lowlevel usb driver. 
   If you are seeing permission issues, kindly add a udev rule for your user 
   for the Bus Auditor device.

busauditor.generic.devinfo
-------------------------

This plugin displays information about BusAuditor hardware that is used
with EXPLIOT framework, information like device name, firmware, hardware revision
and services supported by this device.

**Usage details:**

.. code-block:: console

   ef> run busauditor.generic.devinfo -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run busauditor.generic.devinfo
  [...]
  [+] device_name: BusAuditor
  [+] serial_number: 348435533437
  [+] fw_revision: 0.0.54
  [+] hw_revision: 0.1
  [+] services:
  [+]   read_revision: True
  [+]   read_services: True
  [+]   jtag_port_scan: True
  [+]   swd_port_scan: True
  [+]   uart_port_scan: True
  [+]   i2c_bus_scan: True
  [+] 
  [+] Test busauditor.generic.devinfo passed


busauditor.generic.jtagscan
-------------------------

This plugin scans the target device for JTAG pins and JTAG IDCODE using 
IDCODE scan and pattern scan method.

Note:
By default, TRST excluded from a scan. To included TRST pin detection use `-i` option

**Usage details:**

.. code-block:: console

   ef> run busauditor.generic.jtagscan -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run busauditor.generic.jtagscan -s 0 -e 4 -v 3.3
  [...]
  [*] Start Pin '0', End Pin '4'
  [*] Target Voltage '3.3'
  [*] TRST pin excluded from scan
  [*] Possible permutations to be tested: (120)
  [*]
  [+] JTAG Devices:
  [+] jtag_id: 0x4ba00477
  [+] pins:
  [+]   tck: 0
  [+]   tms: 1
  [+]   tdo: 3
  [+]   tdi: 2
  [+] 
  [+] jtag_id: 0x06431041
  [+] pins:
  [+]   tck: 0
  [+]   tms: 1
  [+]   tdo: 3
  [+]   tdi: 2
  [+] 
  [+] Test busauditor.generic.jtagscan passed

  ef> run busauditor.generic.jtagscan -s 0 -e 4 -i -v 3.3
  [...]
  [*] Start Pin '0', End Pin '4'
  [*] Target Voltage '3.3'
  [*] TRST pin included in scan
  [*] Possible permutations to be tested: (120)
  [*]
  [+] JTAG Devices:
  [+] jtag_id: 0x4ba00477
  [+] pins:
  [+]   trst: 4
  [+]   tck: 0
  [+]   tms: 1
  [+]   tdo: 3
  [+]   tdi: 2
  [+] 
  [+] jtag_id: 0x06431041
  [+] pins:
  [+]   trst: 4
  [+]   tck: 0
  [+]   tms: 1
  [+]   tdo: 3
  [+]   tdi: 2
  [+]
  [+] Test busauditor.generic.jtagscan passed


busauditor.generic.swdscan
-------------------------

This plugin scans the target device for SWD pins and SWD IDCODE.

**Usage details:**

.. code-block:: console

   ef> run busauditor.generic.swdscan -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run busauditor.generic.swdscan -s 0 -e 4 -v 3.3
  [...]
  [*] Start Pin '0', End Pin '4'
  [*] Target Voltage '3.3'
  [*] Possible permutations to be tested: (20)
  [*]
  [+] SWD Devices:
  [+] swd_id: 0x2ba01477
  [+] pins:
  [+]   swclk: 0
  [+]   swdio: 1
  [+] 
  [+] Test busauditor.generic.swdscan passed


busauditor.generic.i2cscan
-------------------------

This plugin scans the target device for I2C pins and I2C device address.

**Usage details:**

.. code-block:: console

   ef> run busauditor.generic.i2cscan -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run busauditor.generic.i2cscan -s 8 -e 9 -v 3.3
  [...]
  [*] Start Pin '8', End Pin '9'
  [*] Target Voltage '3.3'
  [*] Possible permutations to be tested: (2)
  [*] 
  [+] I2C Devices:
  [+] i2c_addr: 0x48
  [+] pins:
  [+]   scl: 8
  [+]   sda: 9
  [+] 
  [+] i2c_addr: 0x50
  [+] pins:
  [+]   scl: 8
  [+]   sda: 9
  [+]
  [+] Test busauditor.generic.i2cscan passed


busauditor.generic.uartscan
-------------------------

This plugin scans the target device for UART pins and Baudrate.

**Usage details:**

.. code-block:: console

   ef> run busauditor.generic.uartscan -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run busauditor.generic.uartscan -s 6 -e 7 -v 3.3
  [...]
  [*] Start Pin '6', End Pin '7'
  [*] Target Voltage '3.3'
  [*] Possible permutations to be tested: (2)
  [+] 
  [+] UART port scan result:
  [+] BaudRate: 115200
  [+] UART pins:
  [+] 	Tx pin: 6, Rx pin: 7
  [*]  
  [+] Test busauditor.generic.uartscan passed

  ef> run busauditor.generic.uartscan -s 8 -e 10 -v 3.3
  [*] Start Pin '8', End Pin '10'
  [*] Target Voltage '3.3'
  [*] Possible permutations to be tested: (2)
  [+] 
  [+] UART port scan result:
  [+] BaudRate: 115200
  [+] UART pins:
  [+] 	Possible pin combinations:
  [+] 	1. Tx pin: 9, Rx pin: 8
  [+] 	2. Tx pin: 9, Rx pin: 10
  [*]  
  [+] Test busauditor.generic.uartscan passed
