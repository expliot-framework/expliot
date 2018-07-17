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
from expliot.core.protocols.internet.mqtt import SimpleMqttClient

class MqttPub(Test):

    def __init__(self):
        super().__init__(name     = "MQTT Publish",
                         summary  = "Publish a message on a MQTT Topic.",
                         descr    = """This test case publishes a message on a topic to a specified
                                        MQTT broker on a specified port.""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html"],
                         category = TCategory(TCategory.MQTT, TCategory.SW, TCategory.RECON),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-r", "--rhost", required=True,
                                    help="Hostname/IP address of the target MQTT broker")
        self.argparser.add_argument("-p", "--rport", default=1883, type=int,
                                    help="Port number of the target MQTT broker. Default is 1883")
        self.argparser.add_argument("-t", "--topic", required=True,
                                    help="Topic name on which message has to be published")
        self.argparser.add_argument("-m", "--msg", required=True,
                                    help="Message to be published on the specified topic")
        self.argparser.add_argument("-i", "--id",
                                    help="The client ID to be used for the connection. Default is random client ID")
        self.argparser.add_argument('-u', '--user',
                                    help="Specify the user name to be used. If not specified, it connects without authentication")
        self.argparser.add_argument('-w', '--passwd',
                                    help="Specify the password to be used. If not specified, it connects with without authentication")


    def execute(self):
        TLog.generic("Publishing message on topic ({}) to MQTT Broker ({}) on port ({})".format(self.args.rhost,
                                                                                                self.args.topic,
                                                                                                self.args.rport))
        creds = None
        if self.args.user and self.args.passwd:
            creds = {'username': self.args.user, 'password': self.args.passwd}
            TLog.trydo("Using authentication (username={})(password={})".format(self.args.user,
                                                                                     self.args.passwd))
        try:
            SimpleMqttClient.pub(self.args.topic, payload=self.args.msg, hostname=self.args.rhost,
                                 port=self.args.rport, auth=creds, client_id=self.args.id)
            TLog.success("Done")
        except:
            self.result.exception()
