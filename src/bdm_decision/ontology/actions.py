from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BusinessAction:
    action_id: str
    name: str
    target_object_id: str
    parameters: dict[str, Any]
    expected_effect: dict[str, Any]
    cost: float

