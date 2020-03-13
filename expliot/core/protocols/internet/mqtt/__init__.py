"""Wrapper for the MQTT features."""
from paho.mqtt import publish, subscribe
from paho.mqtt.client import \
    Client, MQTTv31, MQTTv311, \
    MQTT_ERR_SUCCESS, connack_string

DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_TIMEOUT = 5


class SimpleMqttClient:
    """
    A wrapper around simple publish and subscribe methods in paho mqtt. It
    also few implements helper methods.
    """

    @staticmethod
    def sub(topics, **kwargs):
        """
        Wrapper around paho-mqtt subscribe.simple() method. For details on
        arguments. Please refer paho/mqtt/subscribe.py in paho-mqtt project
        (https://pypi.org/project/paho-mqtt/).

        :param topics: Either a string containing a single topic or a list
                       containing multiple topics
        :param kwargs: subscribe.simple() keyword arguments
        :return: List of msg_count messages (from the topics subscribed to)
                 received from the broker.
                 msg_count subscribe.simple() argument is the count of
                 messages to retrieve.
        """
        msgs = subscribe.simple(topics, **kwargs)
        if msgs.__class__ is not list:
            msgs = [msgs]
        return msgs

    @staticmethod
    def pub(topic, **kwargs):
        """
        Wrapper around paho-mqtt publish.single() method. For details on
        arguments, please refer paho/mqtt/publish.py in paho-mqtt project
        (https://pypi.org/project/paho-mqtt/).

        :param topic: Topic to which the messahed will be published.
        :param kwargs: publish.single() keyword arguments
        :return:
        """
        publish.single(topic, **kwargs)

    @staticmethod
    def pubmultiple(msgs, **kwargs):
        """
        Wrapper around paho-mqtt publish.multiple() method. For details on
        arguments, please refer paho/mqtt/publish.py in paho-mqtt project
        (https://pypi.org/project/paho-mqtt/).

        :param msgs: List of messages to publish. Based on paho-mqtt doc,
                     each message can either be:
          1. dict: msg = {'topic':"<topic>", 'payload':"<payload>", 'qos':<qos>
          2. tuple: ("<topic>", "<payload>", qos, retain)
        :param kwargs: publish.multiple() keyword arguments
        :return:
        """
        publish.multiple(msgs, **kwargs)

    @staticmethod
    def connauth(host, client_id=None, user=None, passwd=None, **kw):
        """
        Helper to check if a client can connect to a broker with specific
        client ID and/or credentials.

        :param host: Host to connect to
        :param client_id: Client ID to use. If not specified paho-mqtt
                        generates a random id.
        :param user: User name of the client. If None or empty, connection is
                     attempted without username and password
        :param passwd: Password of the client. If None, only user name is sent
        :param kw: Client.connect() keyword arguments (excluding host)
        :return: Two comma separated values. The result code and its string
                 representation
        """
        return_code = {"rc": None}
        client = Client(client_id, userdata=return_code)
        if user is not None and user != "":
            client.username_pw_set(user, passwd)
        client.on_connect = SimpleMqttClient._on_connauth

        client.connect(host, **kw)
        client.loop_forever()
        return return_code["rc"], connack_string(return_code["rc"])

    @staticmethod
    def _on_connauth(client, userdata, flags, return_code):
        """
        Callback method for paho-mqtt Client. The arguments are passed by
        Client object. Details of the arguments are documented in
        paho/mqtt/client.py (https://pypi.org/project/paho-mqtt/.

        This method is internally used for connauth().

        :param client: The client instance for this callback
        :param userdata: The private user data as set in Client() or
                         userdata_set()
        :param flags: Response flags sent by the broker
        :param return_code: The connection result
        :return: None
        """
        userdata["rc"] = return_code
        client.disconnect()


class MqttClient(Client):
    """
    Wrapper on Paho MQTT Client class. For more details on
    the functionality check - https://github.com/eclipse/paho.mqtt.python
    """

    def __init__(
            self, client_id="", clean_session=True,
            userdata=None, protocol=MQTTv311, transport="tcp",
    ):
        """
        Wrapper on Client __init__() method. Also initialises
        some new members.

        Args:
            client_id (str): The client ID to use. If not specified,
                uses randomly generated ID.
            clean_session (bool): If True, broker will remove all
                information about this client else, it will retain.
            userdata (caller defined): Used to pass data to callbacks.
            protocol (int): Protocol version of the client
            transport (str): "tcp" is default. specify "websockets" to
                to use WebSockets.
        Returns:
             Nothing.
        """
        super().__init__(
            client_id=client_id, clean_session=clean_session,
            userdata=userdata, protocol=protocol, transport=transport
        )
        # Required for default on_connect and on_disconnect callbacks
        self.connect_rc = MQTT_ERR_SUCCESS
        self.disconnect_rc = MQTT_ERR_SUCCESS

    @classmethod
    def rcstr(cls, retcode):
        """
        Returns a string representation of the return code

        Args:
            retcode (int): MQTT Connection return code
        Returns:
            A string representation of the return code
        """
        return connack_string(retcode)

    def on_connectcb(self, client, userdata, flags, retcode):
        """
        Default on_connect callback. It sets the member with connection
        return code and disconnects on error. Used by pub and sub plugins

        Args:
            client (MqttClient) - The MQTT client object. This is not
                used as it is the same as self.
            userdata (caller defined): Callback specific data passed in
                __init__(). This is not used as we use self members to
                pass information.
            flags (dict): A dict that contains response flags from the broker.
            retcode (int): MQTT Connection return code.

        Returns:
            Nothing.
        """
        self.connect_rc = retcode
        if retcode != MQTT_ERR_SUCCESS:
            self.disconnect()

    def on_publishcb(self, client, userdata, mid):
        """
        Default on_publish callback. It disconnects the connection assuming
        the message has been published. Don't use this if you want to send
        multiple messages in single conenction. Used by pub and sub plugins

        Args:
            client (MqttClient) - The MQTT client object. This is not
                used as it is the same as self.
            userdata (caller defined): Callback specific data passed in
                __init__(). This is not used as we use self members to
                pass information.
            mid (int): matches the mid variable returned from the corresponding
                publish() call

        Returns:
            Nothing.
        """
        self.disconnect()

    def on_disconnectcb(self, client, userdata, retcode):
        """
        Default on_disconnect callback. It sets the member with disconnection
        return code and disconnects on error. Used by pub and sub plugins.
        If the retiurn code is not zero i.e. MQTT_ERR_SUCCESS it means that
        this callback is called because of an unexpected disconnection from
        the broker. If it is zero, it is called as a result of self.disconnect()
        call. We call disconnect() to make sure the object stops looping in loop*()
        methods in the pub sub plugins.

        Args:
            client (MqttClient) - The MQTT client object. This is not
                used as it is the same as self.
            userdata (caller defined): Callback specific data passed in
                __init__(). This is not used as we use self members to
                pass information.
            retcode (int): MQTT Disconnection return code. This is not a correct
                indication of the error as it returns default connection error
                return code.

        Returns:
            Nothing.
        """
        self.disconnect_rc = retcode
        if retcode != MQTT_ERR_SUCCESS:
            self.disconnect()

    def easy_config(
            self, user=None, passwd=None, on_connect=None,
            on_publish=None, on_subscribe=None, on_message=None,
            on_disconnect=None,
    ):
        """
        Easy configuration for MqttClient. It sets the username,
        password and default callbacks required by the pub sub plugins.

        Args:
            user (str): MQTT Username
            passwd (str): MQTT Password
            on_connect (callback): On connect Callback to be set
            on_publish (callback): On publish Callback to be set
            on_subscribe (callback): On subscribe Callback to be set
            on_message (callback): On message Callback to be set
            on_disconnect (callback): On disconnect Callback to be set

        Returns:
            Nothing.
        """

        if user and passwd:
            self.username_pw_set(user, passwd)
        if on_connect:
            self.on_connect = on_connect
        if on_publish:
            self.on_publish = on_publish
        if on_subscribe:
            self.on_subscribe = on_subscribe
        if on_message:
            self.on_message = on_message
        if on_disconnect:
            self.on_disconnect = on_disconnect
