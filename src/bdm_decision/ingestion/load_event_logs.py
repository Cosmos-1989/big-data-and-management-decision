"""Load process event logs into the course workspace."""

from __future__ import annotations

from bdm_decision.process_mining.event_log import (
    DEFAULT_EVENT_LOG,
    EventRecord,
    load_event_log,
)

__all__ = ["DEFAULT_EVENT_LOG", "EventRecord", "load_event_log"]

