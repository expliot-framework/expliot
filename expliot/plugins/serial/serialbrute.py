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

from expliot.core.tests.test import *
from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.hardware.serial import Serial
import itertools
import time

class SerialBrute(Test):

    def __init__(self):
        super().__init__(name     = "Serial Brute-force",
                         summary  = "Brute-force over serial connection to find hidden UART commands",
                         descr    = """This test helps in finding hidden commands/back doors in custom consoles, of
                                        devices exposed over the UART port on the board. It sends random words as
                                        specified over the serial connection and matches the response to a specified
                                        string (case insensitive). Based on match or nomatch criteria it decides
                                        whether the word is a valid or invalid command""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter"],
                         category = TCategory(TCategory.UART, TCategory.HW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-b", "--baud", type=int, default=115200,
                                    help="The Baud rate of the serial device. Default is 115200")
        self.argparser.add_argument("-p", "--port", default="/dev/ttyUSB0", required=True,
                                    help="The device port on the system. Default is /dev/ttyUSB0")
        self.argparser.add_argument("-c", "--chars", default="abcdefghijklmnopqrstuvwxyz",
                                    help="""The characters to use for generating random words.
                                         Default is abcdefghijklmnopqrstuvwxyz""")
        self.argparser.add_argument("-l", "--length", type=int, default=3,
                                    help="Specify the character length for each generated word. Default is 3 characters")
        self.argparser.add_argument("-x", "--prefix", default="",
                                    help="Prefix a string to the generated word")
        self.argparser.add_argument("-a", "--append", default="\r\n",
                                    help="Append a string to the generated word. Default is \"\\r\\n\"")
        self.argparser.add_argument("-m", "--match",
                                    help="""Specify a match criteria string. If the response contains this thring, then
                                            the word is a valid command. Assumption is based on different responses
                                            for valid and invalid commands. Must not be used along with --nomatch""")
        self.argparser.add_argument("-n", "--nomatch",
                                    help="""Specify a nomatch criteria string. If the response doesn't contain this
                                            string, then the word is a valid command. Assumption is based on different
                                            responses for valid and invalid commands. Must not used along with --match""")
        self.argparser.add_argument("-s", "--stop", action="store_true",
                                    help="Stop after finding one valid command")
        self.argparser.add_argument("-t", "--timeout", type=float, default=0.5,
                                    help="Read timeout, in secs, for the serial device. Default is 0.5")
        self.argparser.add_argument("-z", "--buffsize", type=int, default=1,
                                    help="Read buffer size. change this and timeout to increase efficiency. Default is 1")
        self.argparser.add_argument("-v", "--verbose", action="store_true",
                                    help="Show verbose output i.e. each word")

    def pre(self):
        if self.args.match is None:
            if self.args.nomatch is None:
                raise AttributeError("Specify either --match or --nomatch")
        elif self.args.nomatch is not None:
            raise AttributeError("Can't specify both --match and --nomatch")

    def execute(self):
        TLog.generic("Connecting to the the serial port ({}) with baud ({})".format(self.args.port, self.args.baud))
        TLog.generic("Using chars({}) and length({})".format(self.args.chars, self.args.length))
        found = False
        rsn = "Couldn't find a valid command"
        cmds = []
        i = 0
        s = None
        try:
            s = Serial(self.args.port, self.args.baud, timeout=self.args.timeout)
            for word in itertools.product(self.args.chars, repeat=self.args.length):
                cmd = self.args.prefix + "".join(word) + self.args.append
                s.write(cmd.encode())
                r = s.readfull(self.args.buffsize)
                s.flush()
                i += 1
                if i % 20 is 0:
                    # Print something to engage the user :)
                    TLog.generic("Tried {} commands till now".format(i))
                if self.args.verbose is True:
                    TLog.trydo("Command=({}) response({})".format(cmd.rstrip(), r))
                if self.args.match is not None:
                    if self.args.match.lower() in r.decode().lower():
                        TLog.success("Command=({}) found. --match criteria in Response=({})".format(cmd.rstrip(), r))
                        found = True
                        cmds.append(cmd.rstrip())
                        if self.args.stop is True:
                            break
                elif self.args.nomatch is not None:
                    if self.args.nomatch.lower() not in r.decode().lower():
                        TLog.success("Command=({}) found. --nomatch criteria in response=({})".format(cmd.rstrip(), r))
                        found = True
                        cmds.append(cmd.rstrip())
                        if self.args.stop is True:
                            break
        except:
            rsn = "Exception caught: {}".format(sysexcinfo())
        finally:
            if s:
                s.close()
        if found is True:
            TLog.success("Valid Commands found: ({})".format(cmds))
        else:
            self.result.setstatus(passed=False, reason=rsn)
