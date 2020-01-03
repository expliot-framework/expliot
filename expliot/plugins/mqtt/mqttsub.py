"""Plugin to subscribe to a topic of a MQTT broker."""
from time import sleep
from expliot.core.protocols.internet.mqtt import \
    MqttClient, DEFAULT_MQTT_PORT, \
    DEFAULT_MQTT_TIMEOUT, MQTT_ERR_SUCCESS
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.plugins.mqtt import MQTT_REFERENCE
from expliot.core.common.timer import Timer


# pylint: disable=bare-except
class MqttSub(Test):
    """Subscribe to a topic of a MQTT broker."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="sub",
            summary="MQTT Subscriber",
            descr="This test allows you to subscribe to a topic on an MQTT "
            "broker and read messages being published on that topic.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[MQTT_REFERENCE],
            category=TCategory(TCategory.MQTT, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="Hostname/IP address of the target MQTT broker",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=DEFAULT_MQTT_PORT,
            type=int,
            help="Port number of the target MQTT broker. Default is 1883",
        )
        self.argparser.add_argument(
            "-t",
            "--topic",
            default="$SYS/#",
            help="Topic filter to subscribe on the MQTT broker. Default is " "$SYS/#",
        )
        self.argparser.add_argument(
            "-i",
            "--id",
            help="The client ID to be used for the connection. Default is "
            "random client ID",
        )
        self.argparser.add_argument(
            "-u",
            "--user",
            help="Specify the user name to be used. If not specified, it "
            "connects without authentication",
        )
        self.argparser.add_argument(
            "-w",
            "--passwd",
            help="Specify the password to be used. If not specified, it "
            "connects with without authentication",
        )
        self.argparser.add_argument(
            "-o",
            "--timeout",
            default=DEFAULT_MQTT_TIMEOUT,
            type=int,
            help="Time, in seconds, it will keep waiting/reading messages. "
            "Default is {} secs".format(DEFAULT_MQTT_TIMEOUT),
        )

    @staticmethod
    def on_msg(client, userdata, message):
        """
        Custom on_message callback for MqttClient. It just logs the topic
        and the message received.

        Args:
            client (MqttClient) - The MQTT client object. This is not
                used as it is the same as self.
            userdata (caller defined): Callback specific data passed in
                __init__(). This is not used as we use self members to
                pass information.
            message (MQTTMessage): Contains topic, payload, qos, retain
                for the message received from the broker.

        Returns:
            Nothing.
        """
        TLog.success(
            "(topic={})(payload={})".format(message.topic, message.payload)
        )

    def execute(self):
        """Execute the plugin."""
        TLog.generic(
            "Subscribing to topic ({}) on MQTT broker ({}) on port ({})".format(
                self.args.topic, self.args.rhost, self.args.rport
            )
        )
        timer = Timer(self.args.timeout)
        try:
            client = MqttClient(client_id=self.args.id)
            client.easy_config(
                user=self.args.user,
                passwd=self.args.passwd,
                on_connect=client.on_connectcb,
                on_message=MqttSub.on_msg,
                on_disconnect=client.on_disconnectcb
            )
            client.connect(self.args.rhost, self.args.rport)
            client.loop_start()
            client.subscribe(self.args.topic, qos=1)
            while not timer.is_timeout():
                sleep(0.1)
                if client.connect_rc != MQTT_ERR_SUCCESS:
                    self.result.setstatus(
                        passed=False,
                        reason=client.rcstr(client.connect_rc)
                    )
                    TLog.fail(
                        "MQTT Connection Failed. Return code ({}:{})".format(
                            client.connect_rc, client.rcstr(client.connect_rc)
                        )
                    )
                    return
                if client.disconnect_rc != MQTT_ERR_SUCCESS:
                    reason = "Unexpected disconnection. Return code = ({}:{})".format(
                        client.disconnect_rc, client.rcstr(client.disconnect_rc)
                    )
                    self.result.setstatus(
                        passed=False,
                        reason=reason,
                    )
                    TLog.fail(reason)
                    return
            client.loop_stop()
        except:  # noqa: E722
            self.result.exception()
