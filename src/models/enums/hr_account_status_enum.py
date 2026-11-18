from enum import Enum


class HRAccountStatus(str, Enum):
    """Lifecycle of an HR account.

    PENDING  -> created by the HR Admin, waiting for approval (cannot log in)
    ACTIVE   -> approved, can log in
    DECLINED -> rejected by the HR Admin (cannot log in)
    DISABLED -> was active, switched off by the HR Admin (cannot log in)
    """

    PENDING = "pending"
    ACTIVE = "active"
    DECLINED = "declined"
    DISABLED = "disabled"
