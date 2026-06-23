from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    user_id: str
    action_id: str
    timestamp: datetime
    status: str

