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
from expliot.core.protocols.internet.dicom import AE, VerificationPresentationContexts

class CEcho(Test):

    def __init__(self):
        super().__init__(name     = "c-echo",
                         summary  = "DICOM Connection Checker",
                         descr    = """This test case sends a C-ECHO command i.e. attempts to associate with the
                                       DICOM server (SCP - Service class Provider) and checks if we get a response
                                       from the server. It is a good way to identify if the server is running
                                    and we can connect with it i.e. the first step in pen testing DICOM.""",
                         author   = "Aseem Jakhar",
                         email    = "aseemjakhar@gmail.com",
                         ref      = ["https://www.dicomstandard.org/current/",
                                     "http://dicom.nema.org/MEDICAL/dicom/2016a/output/chtml/part07/sect_9.3.5.html"],
                         category = TCategory(TCategory.DICOM, TCategory.SW, TCategory.RECON),
                         target   = TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC))

        self.argparser.add_argument('-r', '--rhost', required=True,
                                    help="Hostname/IP address of the target DICOM Server (SCP)")
        self.argparser.add_argument('-p', '--rport', default=104, type=int,
                                    help="Port number of the target DICOM Server (SCP). Default is 104")
        self.argparser.add_argument('-c', '--aetscu', default="ANY-SCU",
                                    help="""Application Entity Title (AET) of Service Class User (SCU) i.e. the 
                                            calling AET(client/expliot). Default is \"ANY-SCU\" string.""")
        self.argparser.add_argument('-s', '--aetscp', default="ANY-SCP",
                                    help="""Application Entity Title (AET) of Service Class Provider (SCU) i.e. the 
                                            called AET(DICOM server). Default is \"ANY-SCP\" string.""")
    def execute(self):

        TLog.generic("Attempting to connect with DICOM server ({}) on port ({})".format(self.args.rhost,
                                                                                        self.args.rport))
        TLog.generic("Using Calling AET ({}) Called AET ({})".format(self.args.aetscu, self.args.aetscp))

        assoc = None
        try:
            ae = AE(ae_title=self.args.aetscu)
            ae.requested_contexts = VerificationPresentationContexts

            assoc = ae.associate(self.args.rhost, self.args.rport, ae_title=self.args.aetscp)
            TLog.trydo("Server implementation version name ({})".format(assoc.acceptor.implementation_version_name))
            TLog.trydo("Server implementation class UID ({})".format(assoc.acceptor.implementation_class_uid))
            if assoc.is_established:
                ds = assoc.send_c_echo()
                if ds:
                    TLog.success("C-ECHO response status (0x{0:04x})".format(ds.Status))
            else:
                self.result.setstatus(passed=False, reason="Could not establish association with the server")

        except:
            self.result.exception()
        finally:
            if assoc:
                assoc.release()
