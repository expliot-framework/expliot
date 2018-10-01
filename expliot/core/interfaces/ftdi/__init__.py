#
#
# expliot - Internet Of Things Security Testing and Exploitation Framework
#
# Copyright (C) 2018  Aseem Jakhar
#
# Email:   aseemjakhar@gmail.com
# Twitter: @aseemjakhar
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from spiflash.serialflash import SerialFlashManager
from i2cflash.serialeeprom import SerialEepromManager


class SpiFlashManager(SerialFlashManager):
    """
    A wrapper around pyspiflash SerialFlashManager. More details can be found at https://github.com/eblot/pyspiflash
    """

    """
    Calls terminate() on the SpiController to close the ftdi device. As of now there is no close or terminate method
    provided in pyspiflash.
    XXX: Remove me when pyspiflash implements one.

    :param device: The Flash device returned from get_flash_device()
    :return:
    """
    @staticmethod
    def close(device):
        if device:
            device._spi._controller.terminate()

class I2cEepromManager(SerialEepromManager):
    """
    A wrapper around pyi2cflash SerialEepromManager. More details can be found at https://github.com/eblot/pyi2cflash
    """

    """
    Calls terminate() on the I2cController to close the ftdi device. As of now there is no close or terminate method
    provided in pyi2cflash.
    XXX: Remove me when pyspiflash implements one.

    :param device: The Flash device returned from get_flash_device()
    :return:
    """

    @staticmethod
    def close(device):
        if device:
            device._slave._controller.terminate()