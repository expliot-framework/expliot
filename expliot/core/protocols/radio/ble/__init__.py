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

from bluepy import btle

class Ble():
    """
    A wrapper around simple BLE operations
    """

class Ble():

    ADDR_TYPE_RANDOM = btle.ADDR_TYPE_RANDOM
    ADDR_TYPE_PUBLIC = btle.ADDR_TYPE_PUBLIC
    # Advertising Data Type value for "Complete Local Name"
    # Ref: https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile
    ADTYPE_NAME = 9

    @staticmethod
    def scan(iface=0, tout=10):
        scanner = BleScanner(iface)
        scanentries = scanner.scan(timeout=tout)
        return scanentries


class BleScanner(btle.Scanner):
    """
    A wrapper around bluepy Scanner class
    """
    pass

class BlePeripheral(btle.Peripheral):
    """
    A wrapper around bluepy Peripheral class
    """
    pass
