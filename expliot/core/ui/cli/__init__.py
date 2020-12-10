"""Command-line and console feature for EXPLIoT."""
# pylint: disable=invalid-name
import argparse

from cmd2 import Cmd, with_argument_list
import pyparsing

from expliot.core.tests.testsuite import TestSuite


class Cli(Cmd):
    """
    The main command line interpreter for EXPLIoT console. It inherits Cmd2
    package for commandline functionality and adds EXPLIoT specific commands.
    It also initializes the plugins for execution.

    Current EXPLIoT commands defined are:

    1. list: To list available plugins (test cases)
    2. run: Execute a specific plugin (test case)
    3. exit: An alias for Cmd2 quit command
    """

    # Add exit command as an alias for quit
    Cmd.do_exit = Cmd.do_quit

    def __init__(self, prompt=None, intro=None):
        """
        Initialize Cmd members.

        Args:
            prompt (str): The command-line prompt to display
            intro (str): The program introduction banner

        Returns:
            Nothing
        """
        super().__init__(allow_cli_args=False, allow_redirection=False)
        self.prompt = prompt
        self.intro = intro
        self.commentGrammars = pyparsing.Or([])  # No C or Python comment parsing please
        self.redirector = "\x01"
        self.allow_redirection = False
        self.locals_in_py = False
        # set_use_arg_list(True)
        # set_strip_quotes(True)
        self.del_defaultcmds()

        # Initialize Cli members
        self.tsuite = TestSuite()
        self.subcmds = list(self.tsuite.keys())
        self.subcmds.sort()
        self.runp = argparse.ArgumentParser(
            prog="run", description="Executes a plugin (test case)", add_help=False
        )
        self.runp.add_argument(
            "plugin", help="The plugin to execute along with its arguments"
        )

    def del_defaultcmds(self):  # pylint: disable=no-self-use
        """
        Delete/remove the default commands from cmd2.

        Args:
            None

        Returns:
            Nothing
        """
        del [
            Cmd.do_alias,
            Cmd.do_edit,
            Cmd.do_macro,
            Cmd.do_py,
            Cmd.do_run_pyscript,
            Cmd.do_run_script,
            # Cmd.do_set,
            Cmd.do_shell,
            Cmd.do_shortcuts,
        ]

    def do_list(self, args):
        """List the available plugins (test cases)"""
        print("Total plugins: {}\n".format(len(self.subcmds)))
        print("{:<28} {}".format("PLUGIN", "SUMMARY"))
        print("{:<28} {}\n".format("======", "======="))

        for test in self.subcmds:
            print("{:<28} {}".format(test, self.tsuite[test]["summary"]))

    @with_argument_list
    def do_run(self, arglist):
        """Execute a specific plugin (test case). For details: ef> run -h"""
        arguments_length = len(arglist)
        if arguments_length == 0:
            # For the case: ef> run
            self.runp.print_help()
            return

        if arguments_length == 1 and ("-h" in arglist or "--help" in arglist):
            # For the case: ef> run -h
            self.runp.print_help()
            return
        try:
            name_space, subarglist = self.runp.parse_known_args(arglist)
        except SystemExit:
            # Nothing to do here. SystemExit occurs in case of one or more wrong arguments for run command
            # For ex. ef> run -x assuming x is not a valid argument.
            # Cmd2 does not catch SystemExit from v1.0.2 - https://github.com/python-cmd2/cmd2/issues/932
            # returning instead of raising Cmd2ArgparseError so in future any post command hooks implemented can run
            return

        self.runtest(name_space.plugin, subarglist)

    def complete_run(self, text, line, start_index, end_index):
        """
        Tab completion method for run command. It shows the list of available
        plugins that match the subcommand specified by the user.

        Args:
            text (str): Run subcommand string specified by the user
            line (str): The whole run command string typed by the user
            start_index (int): Start index subcommand in the line
            end_index (int): End index of the subcommand in the line

        Returns:
            List of matching subcommands(plugins)
        """
        if text:
            return [c for c in self.subcmds if c.startswith(text)]

        return self.subcmds

    def runtest(self, name, arglist):
        """
        Run a single test case from the TestSuite if it exists.

        Args:
            name (str): Name of the plugin (test case) to run
            arglist (list): Argument list to be passed to the plugin for parsing

        Returns:
            Nothing
        """
        if name in self.tsuite.keys():
            tobj = self.tsuite[name]["class"]()
            tobj.run(arglist)
        else:
            print("Error: plugin ({}) not found.".format(name))
