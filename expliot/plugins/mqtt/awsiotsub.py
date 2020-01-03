"""Plugin to subscribe to a topic on an AWS IoT endpoint."""
from time import sleep
from expliot.core.protocols.internet.mqtt.aws import \
    AwsMqttClient, \
    DEFAULT_AWSIOT_PORT, \
    DEFAULT_AWSIOT_TIMEOUT
from expliot.core.tests.test import Test, TCategory, TTarget, TLog
from expliot.core.common.timer import Timer


# pylint: disable=bare-except
class AwsIotSub(Test):
    """Subscribe to a topic on an AWS IoT endpoint."""

    def __init__(self):
        """Initialize the plugin."""

        super().__init__(
            name="sub",
            summary="AWS IoT MQTT Subscriber",
            descr="This plugin allows you to subscribe to a topic on an AWS IoT "
            "endpoint i.e. cloud MQTT Broker and read messages being published on that topic.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html"],
            category=TCategory(TCategory.MQTT, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.AWS, TTarget.GENERIC, TTarget.AMAZON),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="Hostname/IP address of the endpoint i.e. AWS IoT MQTT broker",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=DEFAULT_AWSIOT_PORT,
            type=int,
            help="Port number of the endpoint i.e. AWS IoT MQTT broker. Default is 8883",
        )
        self.argparser.add_argument(
            "-t",
            "--topic",
            required=True,
            help="Topic name on which message has to be published",
        )
        self.argparser.add_argument(
            "-i",
            "--id",
            help="The client ID to be used for the connection. Default is "
            "random client ID",
        )
        self.argparser.add_argument(
            "-a",
            "--rootca",
            required=True,
            help="The Root CA file",
        )
        self.argparser.add_argument(
            "-k",
            "--privatekey",
            help="The private key file of the thing",
        )
        self.argparser.add_argument(
            "-c",
            "--cert",
            help="The certificate file of the thing",
        )
        self.argparser.add_argument(
            "-s",
            "--websocket",
            action="store_true",
            help="If specified, use MQTT over Websocket",
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
            default=DEFAULT_AWSIOT_TIMEOUT,
            type=int,
            help="Time, in seconds, it will keep waiting/reading messages. "
            "Default is {} secs".format(DEFAULT_AWSIOT_TIMEOUT),
        )

    @classmethod
    def subcb(cls, client, userdata, message):
        """
        A callback method that is called when the thing
        receives a message on the subscribed topic from
        an AWS IoT endpoint.
        """
        TLog.success("(topic={})(payload={})".format(message.topic, message.payload))

    def execute(self):
        """Execute the plugin."""

        TLog.generic(
            "Subscribing to topic ({}) on AWS IoT endpoint ({}) on port ({})".format(
                self.args.topic, self.args.rhost, self.args.rport
            )
        )
        if not self.args.websocket:
            # As of Christmas eve 2019, only two connection types are available
            # 1. TLSv1.2 Mutual Authentication
            #   - X.509 certificate-based secured MQTT connection to AWS IoT
            # 2. Websocket SigV4
            #   - IAM credential-based secured MQTT connection over Websocket
            #      to AWS IoT
            # Source: https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/html/index.html
            if not self.args.privatekey:
                raise FileNotFoundError("Thing Private Key file not specified")
            if not self.args.cert:
                raise FileNotFoundError("Thing Certificate file not specified")
        thing = None
        timer = Timer(self.args.timeout)
        try:
            thing = AwsMqttClient(self.args.id, useWebsocket=self.args.websocket)
            thing.easy_config(
                host=self.args.rhost,
                port=self.args.rport,
                use_websocket=self.args.websocket,
                rootca=self.args.rootca,
                privatekey=self.args.privatekey,
                cert=self.args.cert,
                user=self.args.user,
                passwd=self.args.passwd,
                timeout=self.args.timeout,
            )
            if self.args.user and self.args.passwd:
                TLog.trydo(
                    "Using authentication (username={})(password={})".format(
                        self.args.user, self.args.passwd
                    )
                )
            thing.connect()
            thing.subscribe(self.args.topic, 1, self.subcb)
            while not timer.is_timeout():
                sleep(1)
        except:  # noqa: E722
            self.result.exception()
        finally:
            if thing:
                thing.easy_disconnect()
