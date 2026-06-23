from dataclasses import dataclass

from bdm_decision.ontology.actions import BusinessAction


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    base_state_id: str
    actions: list[BusinessAction]
    predicted_kpis: dict[str, float]

