#
#
# expliot - Internet Of Things Exploitation Framework
# 
# Copyright (C) 2018  Aseem Jakhar
#
# Email:   aseemjakhar@gmail.com
# Twitter: @aseemjakhar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
from expliot.core.tests.test import Test, TCategory, TTarget, TLog

class Sample(Test):

    def __init__(self):
        super().__init__(name     = "Sample name",
                         summary  = "Sample Summary",
                         descr    = "Sample Description",
                         author   = "Sample author",
                         email    = "email@example.com",
                         ref      = ["https://example.com", "https://example.dom"],
                         category = TCategory(TCategory.COAP, TCategory.SW, TCategory.EXPLOIT),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument('-r', '--rhost', required=True, help="IP address of the target")
        self.argparser.add_argument('-p', '--rport', default=80, type=int, help="Port number of the target. Default is 80")
        self.argparser.add_argument('-v', '--verbose', action="store_true", help="show verbose output")

    def pre(self):
        TLog.generic("Enter {}.pre()".format(self.id))
        # Only implement this if you need to do some setup etc.
        TLog.generic("Exit {}.pre()".format(self.id))

    def post(self):
        TLog.generic("Enter {}.post()".format(self.id))
        # Only implement this if you need to do some cleanup etc.
        TLog.generic("Exit {}.post()".format(self.id))

    def execute(self):
        TLog.generic("Executing Test ID {}".format(self.id))
        TLog.trydo("Searching imaginary database")
        TLog.success("Found matching entry in db - ({})".format("FooEntry"))
        snd = "GET / HTTP/1.1"
        TLog.generic("Sending command to server ({}) on port ({})".format(self.args.rhost, self.args.rport))
        if self.args.verbose is True:
            TLog.generic("More verbose output. sending payload ({})".format(snd))
        TLog.fail("No response received")
        TLog.generic("Re-sending command")
        rcv = "Response received from the server"
        self.result.setstatus(passed=True)
        # or in case of failure
        # self.result.setstatus(passed=False, reason="Server is not vulnerable")

