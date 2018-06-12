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

from expliot.core.tests.test import *
#from expliot.core.protocols.internet.coap import SimpleCoapClient

class CoapGet(Test):

    def __init__(self):
        super().__init__(name     = "CoAP GET",
                         summary  = "Send a GET request to a CoAP server",
                         descr    = """This test allows you to send a CoAP GET request (Message)
                                        to a CoAP server on a specified resource path""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://tools.ietf.org/html/rfc7252"],
                         category = TCategory(TCategory.COAP, TCategory.SW, TCategory.RECON),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument('-r', '--rhost', required=True,
                                    help="Hostname/IP address of the target CoAP Server")
        self.argparser.add_argument('-p', '--rport', default=5683, type=int,
                                    help="Port number of the target CoAP Server. Default is 5683")
        self.argparser.add_argument('-u', '--path', default="/.well-known/core",
                                    help="Resource URI path of the GET request. Default is discover URI path /.well-known/core")


    def execute(self):
        TLog.generic("Sending GET request for URI Path ({}) to CoAP Server {} on port {}".format(self.args.path,
                                                                                                 self.args.rhost,
                                                                                                 self.args.rport))
        #clnt = SimpleCoapClient(self.args.rhost, self.args.rport)
        #resp = clnt.get(self.args.path)

        #TLog("resp class {} resp pretty_print {}".format(resp.__class__.__name__, resp.pretty_print()))

        self.result.setstatus(passed=False, reason="CoAP not implemented yet")
