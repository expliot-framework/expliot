"""Wrapper for FDTI."""
# pylint: disable=protected-access
from logging import ERROR, getLogger

from spiflash.serialflash import SerialFlashManager
from i2cflash.serialeeprom import SerialEepromManager
from pyftdi.i2c import I2cController, I2cNackError

DEFAULT_FTDI_URL = "ftdi:///1"

getLogger("pyftdi.i2c").setLevel(ERROR)


class SpiFlashManager(SerialFlashManager):
    """A wrapper around pyspiflash SerialFlashManager.

    More details can be found at https://github.com/eblot/pyspiflash

    Calls terminate() on the SpiController to close the FTDI device. As of
    now there is no close or terminate method provided in pyspiflash.

    TODO: Remove me when pyspiflash implements one.
    """

    @staticmethod
    def close(device):
        """Close connection to device."""
        if device:
            device._spi._controller.terminate()


class I2cEepromManager(SerialEepromManager):
    """A wrapper around pyi2cflash SerialEepromManager.

    More details can be found at https://github.com/eblot/pyi2cflash

    Calls terminate() on the I2cController to close the FTDI device. As of
    now there is no close or terminate method provided in pyi2cflash.

    TODO: Remove me when pyspiflash implements one.
    """

    @staticmethod
    def close(device):
        """Close connection to device"""
        if device:
            device._slave._controller.terminate()
