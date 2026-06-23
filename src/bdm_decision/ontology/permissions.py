from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    role: str
    action_name: str
    allowed: bool

