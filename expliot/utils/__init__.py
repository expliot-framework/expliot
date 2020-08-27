"""Utilities for EXPLIoT."""

from subprocess import Popen, PIPE
from shlex import split


class Tool():
    """
    The base class for any commandline tool that we need to instantiate
    and execute.
    """

    def __init__(self, path, default_args=""):
        """
        Initialize the Tool object

        Args:
            path(str): The full path of the tool (or just the tool name
                if its parent path is in the $PATH
            default_args(str): Any default args that should always be
                part of the command arguments. Default is empty string "".
        Raises:
            ValueError
        """
        if not path:
            raise ValueError("No path specified for Tool({})".format(self.__class__.__name__))
        self.path = path
        self.default_args = default_args if default_args else ""

    def run(self, args, timeout=None):
        """
        Run the command as a child with the specified arguments

        Args:
            args(str): The arguments to be supplied to the command.
            timeout(int): The timeout in seconds while waiting
                for the output. Default is None. For details check
                subprocess.Popen() timeout argument.
        Returns:
            tuple of bytes: Tuple of standard output and standard error
                (stdout,stderr). It returns bytes because encoding, error,
                text arguments of Popen are not specified.
        Raises:
            FileNotFoundError: In case the tool path/name cannot be found or
                executed. This is actually raised by subprocess.Popen
        """

        cmd = "{} {} {}".format(self.path, self.default_args, args)
        proc = None
        try:
            proc = Popen(split(cmd), stdout=PIPE, stderr=PIPE)
            (out, err) = proc.communicate(timeout=timeout)
        finally:
            if proc:
                proc.kill()
        return (out, err)
