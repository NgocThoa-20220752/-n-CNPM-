from enum import Enum


class StatusAccountEnum(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    PENDING = "PENDING"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"