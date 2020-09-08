"""Wrapper for AWSIoTPythonSDK MQTT functionality"""
# pylint: disable=unused-import
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, MQTTv3_1_1

DEFAULT_AWSIOT_PORT = 8883
DEFAULT_AWSIOT_TIMEOUT = 5


class AwsMqttClient(AWSIoTMQTTClient):
    """
    Wrapper on AWSIoTMQTTClient class. It implements easy configuration
    method, default callbacks and connection state check. If you need
    customized configuration and callbacks, directly use AWSIoTMQTTClient
    instead.
    """

    def __init__(self, clientID, protocolType=MQTTv3_1_1, useWebsocket=False, cleanSession=True):
        """
        Initialize the client and super class

        params:
        clientID     - MQTT Client ID
        protocolType - MQTT Protocol version
        useWebsocket - MQTT over Websocket or TCP?
        cleanSession - MQTT Clean session
        """
        super().__init__(
            clientID=clientID,
            protocolType=protocolType,
            useWebsocket=useWebsocket,
            cleanSession=cleanSession,
        )
        self.is_connected = False

    def _onlinecb(self):
        """
        A callback method that is called when the thing
           gets connected to the AWS IoT endpoint.
        """

        self.is_connected = True

    def _offlinecb(self):
        """
        A callback method that is called when the thing
           gets disconnected from the AWS IoT endpoint.
        """
        self.is_connected = False

    def easy_disconnect(self):
        """
        Wrapper on super.disconnect() with a check for valid connection
        before disconnecting. For resource cleanup we need to make sure
        and call disconnect() in finally clause in the plugins, however
        if it is not connected disconnect() raises an Exception, which
        we need to avoid. Hence, this implementation.
        """
        if self.is_connected:
            self.disconnect()

    def easy_config(self, **kwargs):
        """Wrapper on different configuration methods in one go
           and provides simple callbacks to monitor connection and subscribe

           Params:
           host          - The AWS endpoint hostname
           port          - The AWS endpoint port
           use_websocket - Use websocket or not
           rootca        - AWS Root CA file
           privatekey    - AWS Thing private key file
           cert          - AWS Thing certificate file
           user          - User Name
           passwd        - Password
           timeout       - Connection and MQTT operation timeout
           """

        timeout = kwargs["timeout"] if kwargs["timeout"] else DEFAULT_AWSIOT_TIMEOUT
        self.configureEndpoint(kwargs["host"], kwargs["port"])
        if kwargs["use_websocket"]:
            self.configureCredentials(kwargs["rootca"])
        else:
            self.configureCredentials(kwargs["rootca"], kwargs["privatekey"], kwargs["cert"])

        if kwargs["user"] and kwargs["passwd"]:
            self.configureUsernamePassword(kwargs["user"], kwargs["passwd"])

        # thing connection configuration, values taken from AWS sample
        # https://github.com/aws/aws-iot-device-sdk-python/blob/master/samples/basicPubSub/basicPubSub.py
        self.configureAutoReconnectBackoffTime(1, 32, 20)
        self.configureOfflinePublishQueueing(-1)
        self.configureDrainingFrequency(2)
        self.configureConnectDisconnectTimeout(timeout)
        self.configureMQTTOperationTimeout(timeout)

        # Set default Callbacks
        self.onOnline = self._onlinecb
        self.onOffline = self._offlinecb
