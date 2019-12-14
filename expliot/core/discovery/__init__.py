"""Discovery support for EXPLIoT."""


class Discovery:
    """Representation of a discovery entity."""

    def __init__(self):
        """Initialize the discovery."""
        pass

    def device_list(self):
        """Return the found devices."""
        raise NotImplementedError

    def scan(self):
        """Scan the network for devices."""
        raise NotImplementedError
