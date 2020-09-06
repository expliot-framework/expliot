"""Support for DICOM."""

# from expliot.core.protocols.internet.dicom import *
from expliot.core.protocols.internet.dicom import (
    PatientRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelFind,
    PatientStudyOnlyQueryRetrieveInformationModelFind,
    ModalityWorklistInformationFind
)

REFERENCE = "https://www.dicomstandard.org/current/"
DICOMPORT = 104
DEFAULTMODEL = "P"
MODELS = {"P": PatientRootQueryRetrieveInformationModelFind,
          "S": StudyRootQueryRetrieveInformationModelFind,
          "O": PatientStudyOnlyQueryRetrieveInformationModelFind,
          "W": ModalityWorklistInformationFind}
