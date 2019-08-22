"""Main part of EXPLIoT."""


class Expliot:
    """Main class for EXPLIoT."""

    VERSION_MAJOR = 0
    VERSION_MINOR = 6
    VERSION_PATCH = 0

    SUB = ""
    # Name for 0.x.x version
    VERSION_NAME = "agni"

    @classmethod
    def version(cls):
        """Return the current version of EXPLIoT."""
        return "{}.{}.{}{}".format(
            cls.VERSION_MAJOR, cls.VERSION_MINOR, cls.VERSION_PATCH, cls.SUB
        )

    @classmethod
    def version_name(cls):
        """Return the current version name."""
        return cls.VERSION_NAME
