"""Main part of EXPLIoT."""


class Expliot:
    """Main class for EXPLIoT."""
    VMAJOR = 0
    VMINOR = 6
    VPATCH = 0

    SUB = ""
    # Name for 0.x.x version
    VNAME = "agni"

    @classmethod
    def version(cls):
        """Return the current version of EXPLIoT."""
        return "{}.{}.{}{}".format(cls.VMAJOR, cls.VMINOR, cls.VPATCH, cls.SUB)

    @classmethod
    def vname(cls):
        """Return the current version name."""
        return cls.VNAME
