"""Timer utility class."""
import time


class Timer:
    """Timer class to support time out."""

    def __init__(self, timeout=1):
        """Create Timer.

        :param timeout: Time out in seconds
        """
        self.__set_timeout(timeout)

    # Getter method
    def __get_timeout(self):
        """Return Timeout."""
        return self.__timeout

    # Setter method
    def __set_timeout(self, timeout=1):
        """Set current time, and timeout."""
        self.__start_time = time.time()
        self.__timeout = timeout

    # Check Timeout
    def is_timeout(self):
        """Return true if time out."""
        return time.time() - self.__start_time > self.__timeout

    timeout = property(__get_timeout, __set_timeout)
