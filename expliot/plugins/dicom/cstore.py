#
#
# expliot - Internet Of Things Security Testing and Exploitation Framework
#
# Copyright (C) 2019  Aseem Jakhar
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
from expliot.core.protocols.internet.dicom import (
    AE,
    Dataset,
    StoragePresentationContexts,
    dcmread
)

class CStore(Test):

    def __init__(self):
        super().__init__(name     = "c-store",
                         summary  = "DICOM File Store",
                         descr    = """This test case sends a C-STORE message i.e. it sends a DICOM file to the DICOM 
                                       server (SCP - Service class Provider). It can be used to test storing wrong file
                                       for a patient or to fuzz test a server.""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://www.dicomstandard.org/current/",
                                     "XXX ADD C-STORE URL HERE XXX"],
                         category = TCategory(TCategory.DICOM, TCategory.SW, TCategory.ANALYSIS),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument('-r', '--rhost', required=True,
                                    help="Hostname/IP address of the target DICOM Server (SCP)")
        self.argparser.add_argument('-p', '--rport', default=104, type=int,
                                    help="Port number of the target DICOM Server (SCP). Default is 104")
        self.argparser.add_argument('-q', '--lport', default=0, type=int,
                                    help="If specified use this as the source/local port number for expliot")
        self.argparser.add_argument('-c', '--aetscu', default="ANY-SCU",
                                    help="""Application Entity Title (AET) of Service Class User (SCU) i.e. the 
                                            calling AET(client/expliot). Default is \"ANY-SCU\" string""")
        self.argparser.add_argument('-s', '--aetscp', default="ANY-SCP",
                                    help="""Application Entity Title (AET) of Service Class Provider (SCP) i.e. the 
                                            called AET(DICOM server). Default is \"ANY-SCP\" string.""")
        self.argparser.add_argument('-f', '--file',
                                    help="""Specify the DICOM file to read and send to the SCP.""")

    def execute(self):

        TLog.generic("Attempting to send file ({}) to DICOM server ({}) on port ({})".format(self.args.file,
                                                                                             self.args.rhost,
                                                                                             self.args.rport))
        TLog.generic("Using Calling AET ({}) Called AET ({})".format(self.args.aetscu,
                                                                    self.args.aetscp))
        file = None
        assoc = None
        try:
            ae = AE(ae_title=self.args.aetscu)
            ae.requested_contexts = (StoragePresentationContexts)
            file = open(self.args.file, "rb")
            dataset = dcmread(file, force=True)

            # 0 means assign random port in pynetdicom
            if self.args.lport != 0:
                TLog.generic("Using source port number ({})".format(self.args.lport))
                if (self.args.lport < 1024) and (geteuid() != 0):
                    TLog.fail("Oops! Need to run as root for privileged port")
                    raise ValueError("Using privileged port ({}) without root privileges".format(self.args.lport))
            assoc = ae.associate(self.args.rhost,
                                 self.args.rport,
                                 bind_address=('', self.args.lport),
                                 ae_title=self.args.aetscp)
            TLog.trydo("Server implementation version name ({})".format(assoc.acceptor.implementation_version_name))
            TLog.trydo("Server implementation class UID ({})".format(assoc.acceptor.implementation_class_uid))
            if assoc.is_established:
                status = assoc.send_c_store(dataset)
                if status.Status == 0x0000:
                    TLog.success("C-STORE Success (status=0x{0:04x})".format(status.Status))
                else:
                    rsn = "C-STORE Failed to store file (status=0x{0:04x})".format(status.Status)
                    TLog.fail(rsn)
                    self.result.setstatus(passed=False, reason=rsn)
            else:
                self.result.setstatus(passed=False, reason="Could not establish association with the server")
        except:
            self.result.exception()
        finally:
            if assoc:
                assoc.release()
            if file:
                file.close()