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

import argparse
import pyparsing
from cmd2 import Cmd, with_argument_list
from expliot.core.tests.testsuite import TestSuite


class Cli(Cmd):
    """
    Cli - The main command line interpreter for Expliot console. It inherits Cmd2 package for commandline functionality
          and adds expliot specific commands. It also initializes the plugins for execution.
          Current Expliot commmands defined are:
          1. list - to list available plugins (test cases)
          2. run - Execute a specific plugin (test case)
          3. exit - An alias for Cmd2 quit command
    """
    # Add exit command as an alias for quit
    Cmd.do_exit = Cmd.do_quit

    def __init__(self, prompt=None, intro=None):
        # Initialize Cmd members
        super().__init__()
        self.prompt = prompt
        self.intro = intro
        self.commentGrammars = pyparsing.Or([])  # No C or python comment parsing please
        self.redirector = "\x01"
        self.allow_cli_args = False
        self.allow_redirection = False
        self.locals_in_py = False
        # set_use_arg_list(True)
        # set_strip_quotes(True)
        self.del_defaultcmds()

        # Initialize Cli members
        self.tsuite = TestSuite()
        self.subcmds = list(self.tsuite.keys())
        self.subcmds.sort()
        self.runp = argparse.ArgumentParser(prog="run", description="Executes a plugin (test case)", add_help=False)
        self.runp.add_argument("plugin", help="The test case to execute along with its options")

    def del_defaultcmds(self):
        """
        Delete/remove the default commands from cmd2 which are not required for expliot

        :return:
        """
        del [Cmd.do_edit, Cmd.do_py, Cmd.do_pyscript, Cmd.do_load, Cmd.do_shell, Cmd.do_shortcuts]  # , Cmd.do_set]

    def do_list(self, args):
        """
        List the available test cases
        """
        print("Total plugins: {}\n".format(len(self.subcmds)))
        print("{:<25} {}".format("PLUGIN", "SUMMARY"))
        print("{:<25} {}\n".format("======", "======="))

        for test in self.subcmds:
            print("{:<25} {}".format(test, self.tsuite[test]["summary"]))

    @with_argument_list
    def do_run(self, arglist):
        """
        Execute a specific test case
        :param arglist: Argument list (array) passed from the console
        :return:
        """
        alen  = len(arglist)
        if alen == 0:
            self.runp.print_help()
            return
        elif alen == 1 and ('-h' in arglist or '--help' in arglist):
            self.runp.print_help()
            return
        ns, subarglist = self.runp.parse_known_args(arglist)
        self.runtest(ns.plugin, subarglist)

    def complete_run(self, text, line, start_index, end_index):
        """
        Tab completion method for run command. It shows the list of available plugins that match the subcommand
        specified by the user

        :param text: run subcommand string specified by the user
        :param line: The whole run command string typed by the user
        :param start_index: Start index subcommand in the line
        :param end_index: End index of the subcommand in the line
        :return: List of matching subcommands(plugins)
        """
        #print("complete_run text ({}), line ({}), start_index ({}), end_index ({})".format(text, line, start_index, end_index))
        if text:
            return [c for c in self.subcmds if c.startswith(text)]
        else:
            return self.subcmds

    def runtest(self, name, arglist):
        """
        Runs a single test case from the TestSuite if it exists
        :param name: Name of the test case to run
        :param arglist: Argument list to be passed to the test for parsing
        :return: void
        """
        if name in self.tsuite.keys():
            tobj = self.tsuite[name]["class"]()
            tobj.run(arglist)
        else:
            print("Error: test ({}) not found.".format(name))
