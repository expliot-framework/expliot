"""Wrapper for the serial interface."""
from serial import Serial as Pserial


class Serial(Pserial):
    """A wrapper around pyserial's Serial class."""

    def readfull(self, bsize=1):
        """
        Read from the serial device, bsize at a time and return the complete
        response.
        Please note if timeout is not set for the Serial object, then this
        method will block (on read).

        :param bsize: Size of buffer to pass to read() method
        :return: bytes containing the complete response from the serial device
        """
        ret = B""
        while True:
            r = self.read(bsize)
            if not r:
                break
            ret += r
        self.flush()
        return ret

