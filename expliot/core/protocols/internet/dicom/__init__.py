"""Wrapper for the DICOM integration."""
from pydicom import dcmread
from pydicom.dataset import Dataset as DS
from pynetdicom import (
    AE as AppEntity, BasicWorklistManagementPresentationContexts,
    QueryRetrievePresentationContexts, StoragePresentationContexts,
    VerificationPresentationContexts
)

# pylint is not able to find the below imports, because they are
# generated at run-time and stored in globals(), we should change
# this i.e. remove pylint disable if there is any other way to
# tell pylint that it is run-time.

# pylint: disable=no-name-in-module
from pynetdicom.sop_class import (
    ModalityWorklistInformationFind,
    PatientRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelFind,
    PatientStudyOnlyQueryRetrieveInformationModelFind,
)


class AE(AppEntity):
    """Wrapper for the DICOM app entity."""
    pass


class Dataset(DS):
    """Wrapper for the DICOM dataset."""
    pass
