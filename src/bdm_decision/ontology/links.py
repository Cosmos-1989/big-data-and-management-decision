from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BusinessLink:
    source_id: str
    target_id: str
    link_type: str
    properties: dict[str, Any]

