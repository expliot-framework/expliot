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

from paho.mqtt.client import Client, connack_string, MQTTv31, MQTTv311
from paho.mqtt import publish
from paho.mqtt import subscribe

class SimpleMqttClient():
    """
    SimpleMqttClient

    A wrapper around simple publish and subscribe methods in paho mqtt. It also few implements helper methods
    """

    @staticmethod
    def sub(topics, **kwargs):
        """
        Wrapper around paho-mqtt subscribe.simple() method. For details on arguments. Please refer
        paho/mqtt/subscribe.py in paho-mqtt project (https://pypi.org/project/paho-mqtt/)

        :param topics: Either a string containing a single topic or a list containing multiple topics
        :param kwargs: subscribe.simple() keyword arguments
        :return: List of msg_count messages (from the topics subscribed to) received from the broker.
                 msg_count subscribe.simple() argument is the count of messages to retrieve.
        """
        msgs = subscribe.simple(topics, **kwargs)
        if msgs.__class__ != list:
            msgs = [msgs]
        return msgs

    @staticmethod
    def pub(topic, **kwargs):
        """
        Wrapper around paho-mqtt publish.single() method. For details on arguments, please refer
        paho/mqtt/publish.py in paho-mqtt project (https://pypi.org/project/paho-mqtt/)

        :param topic: Topic to which the messahed will be published.
        :param kwargs: publish.single() keyword arguments
        :return:
        """
        publish.single(topic, **kwargs)

    @staticmethod
    def pubmultiple(msgs, **kwargs):
        """
        Wrapper around paho-mqtt publish.multiple() method. For details on arguments, please refer
        paho/mqtt/publish.py in paho-mqtt project (https://pypi.org/project/paho-mqtt/)

        :param msgs: List of messages to publish. Based on paho-mqtt doc, each message can either be
          1. dict: msg = {'topic':"<topic>", 'payload':"<payload>", 'qos':<qos>
          2. tuple: ("<topic>", "<payload>", qos, retain)
        :param kwargs: publish.multiple() keyword arguments
        :return:
        """
        publish.multiple(msgs, **kwargs)

    @staticmethod
    def connauth(host, clientid=None, user=None, passwd=None, **kw):
        """
        connauth helps in checking if a client can connect to a broker with specific client id and/or credentials

        :param host:     Host to connect to
        :param clientid: Client ID to use. If not specified paho-mqtt generates a random id.
        :param user:     User name of the client. If None or empty, connection is attempted without user, pwd
        :param passwd:   Password of the client. If None, only user name is sent
        :param kw:       Client.connect() keyword arguments (excluding host)
        :return:         Two comma separated values - The result code and it's string representation
        """
        rc = {"rc":None}
        c = Client(clientid, userdata=rc)
        if user is not None and user is not "":
            c.username_pw_set(user,passwd)
        c.on_connect = SimpleMqttClient._on_connauth

        #print("connecting to ({})".format(host))
        r = c.connect(host,**kw)
        #print("connect() returned r.__class__ = ({}), r = ({})".format(r.__class__, r))

        r = c.loop_forever()
        return rc["rc"], connack_string(rc["rc"])


    @staticmethod
    def _on_connauth(client, userdata, flags, rc):
        """
        on_connect callback method for paho-mqtt Client. The arguments are passed by Client object. Details
        of the arguments are documented in paho/mqtt/client.py (https://pypi.org/project/paho-mqtt/
        This method is internally used for connauth().

        :param client:   The client instance for this callback
        :param userdata: The private user data as set in Client() or userdata_set()
        :param flags:    Response flags sent by the broker
        :param rc:       The connection result
        :return:         None
        """
        #print("on_connect() rc = ({})".format(rc))
        userdata["rc"] = rc
        client.disconnect()

class MqttClient(Client):
    pass
