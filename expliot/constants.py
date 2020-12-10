"""Constants for EXPLIoT."""
MAJOR_VERSION = 0
MINOR_VERSION = 9
PATCH_VERSION = 6

__short_version__ = "{}.{}".format(MAJOR_VERSION, MINOR_VERSION)
__version__ = "{}.{}".format(__short_version__, PATCH_VERSION)

VERSION_NAME = "agni"

DESCRIPTION = "IoT Security Testing and Exploitation Framework"
DOCS = "https://expliot.readthedocs.io"
NAME = "EXPLIoT"
URL = "https://www.expliot.io"
BANNER_ART = r"""

          ____|   \    /    __ \    |       __  __|           __  __|
         |         \  /    |    |   |          |       __ \      |
          __|        (      ___/    |          |      /    \     |
         |         /  \    |        |          |      \    /     |
        ______|  _/   _\  _|       ______|  ______|   ____/     _|

"""
#
# Used till 0.9.0
# BANNER_ART = """                             __   __      _ _       _
#                             \\ \\ / /     | (_)     | |
#                          ___ \\ V / _ __ | |_  ___ | |_
#                         / _ \\/   \\| '_ \\| | |/ _ \\| __|
#                         | __/ /^\\ \\ |_) | | | (_) | |_
#                         \\___\\/   \\/ .__/|_|_|\\___/ \\__|
#                                   | |
#                                   |_|
# """

BANNER = """{banner_art}\n{description}\n{version}\n{url}\n{docs}\n\n{by}""".format(
    banner_art=BANNER_ART.center(100),
    version="Version: {} - {}".format(__version__, VERSION_NAME).center(80),
    url="Web: {}".format(URL).center(80),
    docs="Documentation: {}".format(DOCS).center(80),
    description=DESCRIPTION.center(80),
    by="by the {} developers".format(NAME).center(80),
)
