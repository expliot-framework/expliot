"""Support for finding data on a DICOM instance."""
import os

from expliot.core.protocols.internet.dicom import (
    AE,
    BasicWorklistManagementPresentationContexts,
    Dataset,
    QueryRetrievePresentationContexts,
)
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.dicom import REFERENCE, DICOMPORT, MODELS, DEFAULTMODEL


# pylint: disable=bare-except, too-many-nested-blocks
class CFind(Test):
    """
    Test to find data on a DICOM instance.

    Output Format:
    [
        {
            "server_implementation_version_name": b"DicomObjects.NET",
            "server_implementation_class_uid": "1.2.826.0.1.3680043.1.2.100.8.40.120.0"
        },
        # Following may be zero or more depending on connection establishment
        # and response of the CFIND command received from the server
        {
            "cfind_query_status": "0xff00",
            "cfind_query_identifier": (0008, 0005) Specific Character Set              CS: ''
            (0008, 0052) Query/Retrieve Level                CS: 'PATIENT'
            (0008, 0054) Retrieve AE Title                   AE: 'ANY-SCP'
            (0010, 0010) Patient's Name                      PN: 'Johnson^John^^Mr'
        },
        # If the status is 0x0000 then identifier will be None. For example see below
        {
            "cfind_query_status": "0x0000",
            "cfind_query_identifier": None
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""

        super().__init__(
            name="c-find",
            summary="DICOM Data Finder",
            descr="This test case sends a C-FIND message i.e. sends a query for a "
            "patient name to the DICOM server (SCP - Service class Provider) "
            "and shows the retrieved details.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[
                REFERENCE,
                "http://dicom.nema.org/MEDICAL/dicom/2016a/output/chtml/part07/sect_9.3.2.html",
            ],
            category=TCategory(TCategory.DICOM, TCategory.SW, TCategory.ANALYSIS),
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
            "-q",
            "--lport",
            default=0,
            type=int,
            help="If specified use this as the source/local port number for EXPLIoT",
        )
        self.argparser.add_argument(
            "-n",
            "--name",
            default="*",
            help="Specify the patient name to search. Please note you "
                 "can use wild cards like * or ? as mentioned in "
                 "http://dicom.nema.org/MEDICAL/dicom/2016a/output/chtml/part04/sect_C.2.2.2.html",
        )
        self.argparser.add_argument(
            "-c",
            "--aetscu",
            default="ANY-SCU",
            help="Application Entity Title (AET) of Service Class User (SCU) i.e. "
                 "the calling AET(client/expliot). Default is 'ANY-SCU' string",
        )
        self.argparser.add_argument(
            "-s",
            "--aetscp",
            default="ANY-SCP",
            help="Application Entity Title (AET) of Service Class Provider (SCP) "
                 "i.e. the called AET(DICOM server). Default is 'ANY-SCP' string.",
        )
        # self.argparser.add_argument('-c', '--pcontext', default="1.2.840.10008.5.1.4.1.2.1.1",
        #                            help="Presentation Context SOP class UID to use for C-FIND. "
        #                            "Default is 1.2.840.10008.5.1.4.1.2.1.1 "
        #                            "(Ref: https://www.dicomlibrary.com/dicom/sop/) "
        #                            "(Patient Root Query/Retrieve Information Model UID - FIND). "
        #                            If the above doesn't work then try others from the Ref page "
        #                            "for example Study Root. (hint: search for FIND).")
        self.argparser.add_argument(
            "-m",
            "--model",
            default=DEFAULTMODEL,
            help="Specify the information model to use for C-FIND. "
                 "Options are P, S, W and O for patient root, study "
                 "root, modality worklist and patient/study only (retired) "
                 "respectively. Default is {}".format(DEFAULTMODEL),
        )

    def execute(self):
        """Execute the test."""

        if self.args.model not in MODELS:
            self.result.setstatus(
                passed=False,
                reason="Unknown model ({}) specified".format(self.args.model)
            )
            return
        TLog.generic(
            "Attempting to search for patient ({}) on DICOM server ({}) on port ({})".format(
                self.args.name, self.args.rhost, self.args.rport
            )
        )
        TLog.generic(
            "Using Calling AET ({}) Called AET ({}) Information model ({})".format(
                self.args.aetscu, self.args.aetscp, self.args.model
            )
        )
        assoc = None
        try:
            app_entity = AE(ae_title=self.args.aetscu)
            app_entity.requested_contexts = (
                QueryRetrievePresentationContexts
                + BasicWorklistManagementPresentationContexts
            )
            data_set = Dataset()
            data_set.PatientName = self.args.name
            # May need to move this as cmdline argument for other SOP Class UIDs
            data_set.QueryRetrieveLevel = "PATIENT"
            # 0 means assign random port in pynetdicom
            if self.args.lport != 0:
                TLog.generic("Using source port number ({})".format(self.args.lport))
                if (self.args.lport < 1024) and (os.geteuid() != 0):
                    TLog.fail("Oops! Need to run as root for privileged port")
                    raise ValueError(
                        "Using privileged port ({}) without root privileges".format(
                            self.args.lport
                        )
                    )
            assoc = app_entity.associate(
                self.args.rhost,
                self.args.rport,
                bind_address=("", self.args.lport),
                ae_title=self.args.aetscp,
            )
            self.output_handler(
                tlogtype=TLog.TRYDO,
                server_implementation_version_name=assoc.acceptor.implementation_version_name,
                server_implementation_class_uid=assoc.acceptor.implementation_class_uid,
            )
            if assoc.is_established:
                responses = assoc.send_c_find(data_set, MODELS[self.args.model])
                if responses:
                    for (status, identifier) in responses:
                        # As per pynetdicom if status is either of below, then responses contain valid identifier
                        # datasets, else None. Ref: pynetdicom/pynetdicom/apps/findscu/findscu.py
                        # if status.Status in (0xFF00, 0xFF01):
                        statdict = {"cfind_query_status": "0x{0:04x}".format(status.Status),
                                    "cfind_query_identifier": str(identifier)}
                        self.output_handler(**statdict)
                else:
                    reason = "Did not receive any response data sets"
                    TLog.fail(reason)
                    self.result.setstatus(passed=False, reason=reason)
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
