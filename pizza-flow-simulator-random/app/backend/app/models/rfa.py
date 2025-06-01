''' Approvals models'''
from enum import StrEnum

class RFAStatus(StrEnum):
    ''' Possible RFA statuses'''
    approved = "approved"
    denied = "denied"
    pending = "pending"
    unknown = "unknown"
