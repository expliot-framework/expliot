I2C
===

`Inter-Integrated Circuit <https://en.wikipedia.org/wiki/I%C2%B2C>`_ (I2C) is a
synchronous, serial hardware bus communication protocol used for intra-board
(short distance) communication i.e. between two components on a circuit board.
It is a *2-wire* bus. It is also used in EEPROMs for example to read and write
data.

The current implementation is dependent on the *pyi2cflash* package which in
turn is dependent on *pyftdi* package. Note that there will be some extra info
printed on the console, when the plugin executes, which comes from the
*pyi2cflash* package and is not part of the plugin code. To interface your
PC with the I2C EEPROM chip, you need a hardware connector or bridge. You can
use any FTDI based device, that provides an I2C interface. We have created a
multi-protocol connector called **EXPLIoT Nano** which is available at our
`online store <https://expliot.io>`_. Although, the framework should work with
any *pyftdi* compatible FTDI device.

i2c.generic.scan
----------------

The scan will be performed over the available address space of the I2C bus
to detect connected units.

**Usage details:**

.. code-block:: console

   ef> run i2c.generic.scan -h

Examples
^^^^^^^^

Environmental sensors are often connected to the I2C bus and used in a large
scale in the IoT and home automation eco-system. To get a feeling how the test
works, a `BMP280 <https://www.bosch-sensortec.com/bst/products/all_products/bme280>`_
breakout board is wired to a `Expliot-NANO <https://expliot.io/collections/frontpage/products/expliot-nano>`_.

.. code-block:: text

   +---------+                    +-----------------+
   |         | VCC +--------+ 3V3 |                 |
   | BMP280  |                    |                 |
   |         | GND +--------+ GND |   Expliot-NANO  |
   |         |                    |                 |
   |         | SCL +--------+ SCL |                 |
   |         |                    |                 |
   |         | SDA +-----+--+ SDA |                 |
   +---------+           |        |                 |
                         +--+ SDA |                 |
                                  +-----------------+

For further details check the `pin layout <https://drive.google.com/file/d/1291LTG39IQXhTzfLoDozLIAVztg-vJOo/view>`_.

.. code-block:: console

   ef> run i2c.generic.scan
   [...]
   [*] Scanning for I2C devices...
   [+] Address found: 0x76
   [+] Done. Found 1 and not found 120
   [+] Test i2c.generic.scan Passed

i2c.generic.readeeprom
----------------------

This test is reading data from an EEPROM. Currently the following chips are
supported:

- 24AA32A
- 24AA64
- 24AA128
- 24AA256
- 24AA512

**Usage details:**

.. code-block:: console

   ef> run i2c.generic.readeeprom -h

i2c.generic.writeeeprom
-----------------------

See ``i2c.generic.readeeprom`` as the same details apply for writing.

**Usage details:**

.. code-block:: console

   ef> run i2c.generic.writeeeprom -h
