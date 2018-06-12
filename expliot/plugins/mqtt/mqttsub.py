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
from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.internet.mqtt import SimpleMqttClient

class MqttSub(Test):

    def __init__(self):
        super().__init__(name     = "MQTT Subscribe",
                         summary  = "Subscribe to an MQTT Topic.",
                         descr    = """This test allows you to subscribe to a topic on an MQTT
                                        broker and read messages being published on the same topic.""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html"],
                         category = TCategory(TCategory.MQTT, TCategory.SW, TCategory.RECON),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument("-r", "--rhost", required=True,
                                    help="Hostname/IP address of the target MQTT broker")
        self.argparser.add_argument("-p", "--rport", default=1883, type=int,
                                    help="Port number of the target MQTT broker. Default is 1883")
        self.argparser.add_argument("-t", "--topic", default="$SYS/#",
                                    help="Topic filter to subscribe on the MQTT broker. Default is $SYS/#")
        self.argparser.add_argument("-c", "--count", default=1, type=int,
                                    help="""Specify count of messages to read. It blocks till all the (count)
                                            messages are read. Default is 1""")
        self.argparser.add_argument("-i", "--id",
                                    help="The client ID to be used for the connection. Default is random client ID")




    def execute(self):
        TLog.generic("Susbcribing to topic ({}) to MQTT Broker ({}) on port ({})".format(self.args.topic,
                                                                                         self.args.rhost,
                                                                                         self.args.rport))
        try:
            msgs = SimpleMqttClient.sub(self.args.topic, hostname=self.args.rhost, port=self.args.rport,
                                 client_id=self.args.id, msg_count=self.args.count)
            for m in msgs:
                TLog.success("(topic={})(payload={})".format(m.topic, str(m.payload)))
        except:
            self.result.setstatus(passed=False, reason="Exception caught: {}".format(sysexcinfo()))