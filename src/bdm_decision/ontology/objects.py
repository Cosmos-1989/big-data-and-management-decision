from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BusinessObject:
    object_id: str
    object_type: str
    properties: dict[str, Any]

