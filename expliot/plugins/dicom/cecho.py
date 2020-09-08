"""Plugin to check a connection to a DICOM instance."""
from expliot.core.protocols.internet.dicom import AE, VerificationPresentationContexts
from expliot.core.tests.test import TCategory, TTarget, Test, TLog
from expliot.plugins.dicom import REFERENCE, DICOMPORT


# pylint: disable=bare-except
class CEcho(Test):
    """
    Test to check a connection to a DICOM instance.

    Output Format:
    [
        {
            "server_implementation_version_name": b"DicomObjects.NET",
            "server_implementation_class_uid": "1.2.826.0.1.3680043.1.2.100.8.40.120.0"
        },
        {"cecho_response_status": "0x0000"} # This is present only if the connection
                                            # is established.
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="c-echo",
            summary="DICOM Connection Checker",
            descr="This test case sends a C-ECHO command i.e. attempts to associate "
            "with the DICOM server (SCP - Service class Provider) and checks "
            "if we get a response from the server. It is a good way to identify "
            "if the server is running and we can connect with it i.e. the "
            "first step in pen testing DICOM.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[
                REFERENCE,
                "http://dicom.nema.org/MEDICAL/dicom/2016a/output/chtml/part07/sect_9.3.5.html",
            ],
            category=TCategory(TCategory.DICOM, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="The hostname/IP address of the target DICOM Server (SCP)",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=DICOMPORT,
            type=int,
            help="The port number of the target DICOM Server (SCP). "
                 "Default is {}".format(DICOMPORT),
        )
        self.argparser.add_argument(
            "-c",
            "--aetscu",
            default="ANY-SCU",
            help="Application Entity Title (AET) of Service Class User (SCU) i.e. "
            "the calling AET (client/expliot). Default is 'ANY-SCU' string.",
        )
        self.argparser.add_argument(
            "-s",
            "--aetscp",
            default="ANY-SCP",
            help="Application Entity Title (AET) of Service Class Provider (SCP) i.e. "
            "the called AET (DICOM server). Default is 'ANY-SCP' string.",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            "Attempting to connect with DICOM server ({}) on port ({})".format(
                self.args.rhost, self.args.rport
            )
        )
        TLog.generic(
            "Using Calling AET ({}) Called AET ({})".format(
                self.args.aetscu, self.args.aetscp
            )
        )

        assoc = None
        try:
            app_entity = AE(ae_title=self.args.aetscu)
            app_entity.requested_contexts = VerificationPresentationContexts

            assoc = app_entity.associate(
                self.args.rhost, self.args.rport, ae_title=self.args.aetscp
            )
            self.output_handler(
                tlogtype=TLog.TRYDO,
                server_implementation_version_name=assoc.acceptor.implementation_version_name,
                server_implementation_class_uid=assoc.acceptor.implementation_class_uid,
            )
            if assoc.is_established:
                data_set = assoc.send_c_echo()
                if data_set:
                    self.output_handler(cecho_response_status="0x{0:04x}".format(data_set.Status))
            else:
                self.result.setstatus(
                    passed=False,
                    reason="Could not establish association with the server",
                )
        except:  # noqa: E722
            self.result.exception()
        finally:
            if assoc:
                assoc.release()
