from bdm_decision.ontology.actions import BusinessAction
from bdm_decision.ontology.objects import BusinessObject
from bdm_decision.ontology.scenarios import Scenario


def test_business_object_and_scenario_can_be_created() -> None:
    order = BusinessObject(
        object_id="ORD-001",
        object_type="Order",
        properties={"delay_risk": 0.82},
    )
    action = BusinessAction(
        action_id="ACT-001",
        name="expedite_delivery",
        target_object_id=order.object_id,
        parameters={"extra_cost": 300},
        expected_effect={"delay_probability_reduction": 0.35},
        cost=300.0,
    )
    scenario = Scenario(
        scenario_id="SCN-001",
        base_state_id="STATE-001",
        actions=[action],
        predicted_kpis={"on_time_delivery_rate": 0.94},
    )

    assert scenario.actions[0].target_object_id == "ORD-001"

