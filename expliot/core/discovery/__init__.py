"""Discovery support for EXPLIoT."""


class Discovery:
    """Representation of a discovery entity."""

    def __init__(self):
        """Initialize the discovery."""
        pass

    def devices(self):
        """
        Return the found devices. This should be called after scan()

        Args:
            Nothing
        Returns:
            list: List of all devices discovered in scan()
        """
        raise NotImplementedError

    def services(self):
        """
        Return the found services. This should be called after scan()

        Args:
            Nothing
        Returns:
            list: List of all devices discovered in scan()"""
        raise NotImplementedError

    def scan(self):
        """
        Scan for devices or services depending on the Discovery type

        Args:
            Nothing
        Returns:
            Nothing

        """
        raise NotImplementedError
