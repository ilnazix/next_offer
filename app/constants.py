from enum import StrEnum


class OfferStatus(StrEnum):
    PENDING = "pending"
    SHOWN = "shown"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    DISMISSED = "dismissed"


class EventType(StrEnum):
    SALARY = "salary"
    SALARY_RECEIVED = "salary_received"
    PURCHASE = "purchase"
    DEPOSIT_VIEW = "deposit_view"
    HIGH_BALANCE = "high_balance"


OFFER_STATUS_VALUES = tuple(status.value for status in OfferStatus)
ACTIVE_OFFER_STATUSES = (OfferStatus.PENDING.value, OfferStatus.SHOWN.value)
FEEDBACK_ACTION_VALUES = (
    OfferStatus.ACCEPTED.value,
    OfferStatus.DECLINED.value,
    OfferStatus.DISMISSED.value,
)

SUPPORTED_EVENT_TYPES = frozenset(event.value for event in EventType)
