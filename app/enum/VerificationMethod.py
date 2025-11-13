from enum import Enum

class VerificationMethod(str, Enum):
    EMAIL = "email"
    PHONE = "phone"