BusAuditor
======

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
  [+] 
  [+] Bus Auditor Details:
  [+] Device Name:	Payatu BusAuditor
  [+] Serial Number:	348435533437
  [+] FW Revision:	0.0.52
  [+] HW Revision:	0.1
  [*]  
  [+] Services:
  [+] 	Read Revision:	True
  [+] 	Read Services:	True
  [+] 	JTAG Port Scan:	True
  [+] 	SWD Port Scan:	True
  [+] 	UART Port Scan:	True
  [+] 	I2C Bus Scan:	True
  [*] 
  [+] Test busauditor.generic.devinfo passed


busauditor.generic.jtagscan
-------------------------

This plugin scans the target device for JTAG pins and JTAG IDCODE using 
IDCODE scan and pattern scan method.

Note:
By default, TRST excluded from a scan. To included TRST pin detection use -i option

**Usage details:**

.. code-block:: console

   ef> run busauditor.generic.jtagscan -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run busauditor.generic.jtagscan -s 0 -e 4 -v 3.3
  [...]
  [*] Start Pin (0), End Pin (4)
  [*] Target Voltage (3.3)
  [*] TRST pin excluded from scan
  [*]
  [+] 
  [+] JTAG port scan result:
  [+] Device: 1
  [+] 	ID Code : 0x4ba00477
  [+] 	TCK     : 0
  [+] 	TMS     : 1
  [+] 	TDO     : 3
  [+] 	TDI     : 2
  [*]  
  [+] Device: 2
  [+] 	ID Code : 0x06431041
  [+] 	TCK     : 0
  [+] 	TMS     : 1
  [+] 	TDO     : 3
  [+] 	TDI     : 2
  [*]  
  [+] Test busauditor.generic.jtagscan passed

  ef> run busauditor.generic.jtagscan -s 0 -e 4 -i -v 3.3
  [...]
  [*] Start Pin (0), End Pin (4)
  [*] Target Voltage (3.3)
  [*] TRST pin included in scan
  [*]
  [+] 
  [+] JTAG port scan result:
  [+] Device: 1
  [+] 	ID Code : 0x4ba00477
  [+] 	TCK     : 0
  [+] 	TMS     : 1
  [+] 	TDO     : 3
  [+] 	TDI     : 2
  [*] 	TRST    : 4
  [*]  
  [+] Device: 2
  [+] 	ID Code : 0x06431041
  [+] 	TCK     : 0
  [+] 	TMS     : 1
  [+] 	TDO     : 3
  [+] 	TDI     : 2
  [*] 	TRST    : 4
  [*]  
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
  [*] Start Pin (0), End Pin (4)
  [*] Target Voltage (3.3)
  [+] 
  [+] SWD port scan result:
  [+] Device: 1
  [+] 	ID code : 0x2ba01477
  [+] 	SW CLK  : 0
  [+] 	SW DIO  : 1
  [*]  
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

  ef> run busauditor.generic.i2cscan -s 5 -e 7 -v 3.3
  [...]
  [*] Start Pin (5), End Pin (6)
  [*] Target Voltage (3.3)
  [+] 
  [+] I2C port scan result: 
  [+] Device 1:
  [+] 	I2C Address: 0x48
  [+] 	SCL     : 5
  [+] 	SDA     : 6
  [*]  
  [+] Device 2:
  [+] 	I2C Address: 0x50
  [+] 	SCL     : 5
  [+] 	SDA     : 6
  [*]  
  [+] Test busauditor.generic.i2cscan passed


busauditor.generic.uartscan
-------------------------

This plugin scans the target device for UART pins and BaudRate.

**Usage details:**

.. code-block:: console

   ef> run busauditor.generic.uartscan -h

Examples
^^^^^^^^

.. code-block:: text

  ef> run busauditor.generic.uartscan -s 8 -e 9 -v 3.3
  [...]
  [*] Start Pin (8), End Pin (9)
  [*] Target Voltage (3.3)
  [+] 
  [+] UART port scan result:
  [+] BaudRate: 115200
  [+] UART pins:
  [+] 	Tx pin: 9, Rx pin: 8
  [*]  
  [+] Test busauditor.generic.uartscan passed

  ef> run busauditor.generic.uartscan -s 8 -e 10 -v 3.3
  [*] Start Pin (8), End Pin (10)
  [*] Target Voltage (3.3)
  [+] 
  [+] UART port scan result:
  [+] BaudRate: 115200
  [+] UART pins:
  [+] 	Possible pin combinations:
  [+] 	1. Tx pin: 9, Rx pin: 8
  [+] 	2. Tx pin: 9, Rx pin: 10
  [*]  
  [+] Test busauditor.generic.uartscan passed
