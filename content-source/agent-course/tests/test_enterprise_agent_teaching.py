"""逐一复算案例包 40 组标准样本，并验证四个实验片段可执行。"""

from __future__ import annotations

import json
import re
from contextlib import redirect_stdout
from io import StringIO
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from bdm_decision.cases.week14_enterprise_agents import (  # noqa: E402
    answer_policy, approve_meeting, handle_production_event,
    propose_meeting, research_answer, route_customer,
)

PASSED = 0
FAILED: list[str] = []


def check(name: str, function: Callable[[], dict[str, Any]],
          expected: dict[str, Any]) -> None:
    """期望字段逐项比较，允许结果保留更多供教学解释的信息。"""
    global PASSED
    try:
        actual = function()
        for key, value in expected.items():
            assert actual.get(key) == value, (
                f'{key}: expected {value!r}, got {actual.get(key)!r}; full={actual!r}'
            )
        PASSED += 1
    except Exception as exc:
        FAILED.append(f'{name}: {exc}')


def test_policy() -> None:
    """制度问答九组：日期边界、金额边界、权限与多意图。"""
    cases = [
        ('P1', lambda: answer_policy('住宿', amount_yuan=380),
         {'decision': 'eligible', 'evidence_ids': ['HOTEL-v3'], 'state': 'answered'}),
        ('P2', lambda: answer_policy('酒店', amount_yuan=450),
         {'decision': 'manager_preapproval', 'evidence_ids': ['HOTEL-v3'],
          'state': 'pending_review'}),
        ('P3', lambda: answer_policy('住宿', amount_yuan=700),
         {'decision': 'outside_policy', 'evidence_ids': ['HOTEL-v3'],
          'state': 'pending_review'}),
        ('P4', lambda: answer_policy('住宿', as_of='2026-09-15', amount_yuan=380),
         {'decision': 'manager_preapproval', 'evidence_ids': ['HOTEL-v2'],
          'state': 'pending_review'}),
        ('P5', lambda: answer_policy('发票', days_after_trip=20),
         {'decision': 'within_window', 'evidence_ids': ['INVOICE-v1'],
          'state': 'answered'}),
        ('P6', lambda: answer_policy('发票', days_after_trip=45),
         {'decision': 'late_review', 'evidence_ids': ['INVOICE-v1'],
          'state': 'pending_review'}),
        ('P7', lambda: answer_policy('工资', role='employee'),
         {'decision': 'restricted_transfer', 'evidence_ids': [],
          'state': 'restricted'}),
        ('P8', lambda: answer_policy('住宿', region='international', amount_yuan=380),
         {'decision': 'no_evidence', 'evidence_ids': [], 'state': 'clarify'}),
        ('P9', lambda: answer_policy('发票和酒店'),
         {'decision': 'clarify', 'evidence_ids': [], 'state': 'clarify'}),
    ]
    for name, fn, expected in cases:
        check(name, fn, expected)


def approved_meeting() -> dict[str, Any]:
    ledger: dict[str, dict[str, Any]] = {}
    propose_meeting(['李', '王'], event_id='M5', ledger=ledger)
    return approve_meeting('M5', approval_id='ORG-1',
                           organizer_authenticated=True, ledger=ledger)


def test_office() -> None:
    """办公室九组：集合交集、人工批准、资料版本及访问角色。"""
    cases = [
        ('O1', lambda: propose_meeting(['李', '王'], event_id='M1'),
         {'proposal_slot': 'S2', 'state': 'proposed'}),
        ('O2', lambda: propose_meeting(['李', '赵'], event_id='M2'),
         {'proposal_slot': 'S1', 'state': 'proposed'}),
        ('O3', lambda: propose_meeting(['王', '赵'], event_id='M3'),
         {'proposal_slot': 'S3', 'state': 'proposed'}),
        ('O4', lambda: propose_meeting(['李', '王', '赵'], event_id='M4'),
         {'decision': 'conflict', 'proposal_slot': None, 'state': 'conflict'}),
        ('O5', approved_meeting,
         {'decision': 'slot_committed_local', 'proposal_slot': 'S2',
          'state': 'committed'}),
        ('O6', lambda: research_answer('泵振动', role='employee'),
         {'decision': 'answered', 'evidence_ids': ['R-VIB-v2'],
          'answer_fact': '先核对传感器校准与轴承检查记录。'}),
        ('O7', lambda: research_answer('芯片接口', role='employee'),
         {'decision': 'access_denied', 'answer_fact': None, 'evidence_ids': []}),
        ('O8', lambda: research_answer('芯片接口', role='engineer'),
         {'decision': 'answered', 'evidence_ids': ['R-CHIP-v1'],
          'answer_fact': '接口额定电压 3.3 V。'}),
        ('O9', lambda: research_answer('未知电路', role='engineer'),
         {'decision': 'no_evidence', 'answer_fact': None, 'evidence_ids': []}),
    ]
    for name, fn, expected in cases:
        check(name, fn, expected)


def test_routing() -> None:
    """客服十组：安全优先、身份、归属、退货人工分流、产品资料。"""
    cases = [
        ('C1', lambda: route_customer('C1', customer_id='U1', verified=True,
                                      message='物流', order_id='O100'),
         {'route': 'order_status', 'visible_fact': '已发货', 'state': 'answered'}),
        ('C2', lambda: route_customer('C2', customer_id='U2', verified=True,
                                      message='订单', order_id='O101'),
         {'route': 'order_status', 'visible_fact': '待发货', 'state': 'answered'}),
        ('C3', lambda: route_customer('C3', customer_id='U1', verified=False,
                                      message='物流', order_id='O100'),
         {'route': 'verify_identity', 'visible_fact': None}),
        ('C4', lambda: route_customer('C4', customer_id='U2', verified=True,
                                      message='物流', order_id='O100'),
         {'route': 'privacy_block', 'visible_fact': None, 'state': 'restricted'}),
        ('C5', lambda: route_customer('C5', customer_id='U1', verified=True,
                                      message='退款', days_since_purchase=5,
                                      unopened=True),
         {'route': 'refund_review', 'state': 'pending_human'}),
        ('C6', lambda: route_customer('C6', customer_id='U1', verified=True,
                                      message='退货', days_since_purchase=20,
                                      unopened=True),
         {'route': 'exception_review', 'state': 'pending_human'}),
        ('C7', lambda: route_customer('C7', customer_id='U1', verified=True,
                                      message='退款', days_since_purchase=5,
                                      unopened=False),
         {'route': 'exception_review', 'state': 'pending_human'}),
        ('C8', lambda: route_customer('C8', customer_id='U1', verified=False,
                                      message='设备冒烟，O100物流', order_id='O100'),
         {'route': 'safety_escalate', 'state': 'pending_human',
          'next_actor': '安全值班组'}),
        ('C9', lambda: route_customer('C9', message='规格', product_id='P1'),
         {'route': 'product_fact', 'visible_fact': '额定功率 500 W',
          'evidence_ids': ['P1']}),
        ('C10', lambda: route_customer('C10', message='安装方法'),
         {'route': 'clarify', 'visible_fact': None}),
    ]
    for name, fn, expected in cases:
        check(name, fn, expected)


def production_call(event_id: str, *, ledger=None, **overrides: Any) -> dict[str, Any]:
    data = dict(vibration_mm_s=7.0, temperature_c=75.0, sensor_age_s=20,
                quality_flag='good', interlock_trip=False)
    data.update(overrides)
    return handle_production_event(event_id, ledger=ledger, **data)


def duplicate_safety() -> dict[str, Any]:
    ledger: dict[str, dict[str, Any]] = {}
    production_call('E07', ledger=ledger, interlock_trip=True)
    return production_call('E07', ledger=ledger, interlock_trip=True)


def approved_production(ledger: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return production_call('E08', ledger=ledger, vibration_mm_s=8.0,
                           temperature_c=79.0, approval_by='maintenance_lead')


def duplicate_ticket() -> dict[str, Any]:
    ledger: dict[str, dict[str, Any]] = {}
    approved_production(ledger)
    return approved_production(ledger)


def test_production() -> None:
    """产线十二组：阈值等号、坏数据、联锁优先、审批与幂等。"""
    cases = [
        ('L1', lambda: production_call('E01', vibration_mm_s=7.9,
                                       temperature_c=79.0),
         {'risk_score': 0, 'route': 'monitor', 'state': 'closed',
          'control_commands': []}),
        ('L2', lambda: production_call('E02', vibration_mm_s=8.0,
                                       temperature_c=79.0),
         {'risk_score': 1, 'route': 'warning_review', 'state': 'proposed'}),
        ('L3', lambda: production_call('E03', vibration_mm_s=7.9,
                                       temperature_c=80.0),
         {'risk_score': 1, 'route': 'warning_review', 'state': 'proposed'}),
        ('L4', lambda: production_call('E04', vibration_mm_s=8.2,
                                       temperature_c=81.0),
         {'risk_score': 2, 'route': 'high_review', 'state': 'proposed'}),
        ('L5', lambda: production_call('E05', quality_flag='bad'),
         {'risk_score': 1, 'route': 'warning_review',
          'matched_signals': ['quality']}),
        ('L6', lambda: production_call('E06', sensor_age_s=61),
         {'risk_score': None, 'route': 'data_quality_hold',
          'state': 'data_quality_hold'}),
        ('L7', lambda: production_call('E07', interlock_trip=True),
         {'route': 'interlock_escalate', 'state': 'human_safety_response',
          'control_commands': []}),
        ('L8', duplicate_safety,
         {'route': 'interlock_escalate', 'replayed': True,
          'new_ticket_count': 0}),
        ('L9', lambda: approved_production({}),
         {'risk_score': 1, 'route': 'warning_review',
          'state': 'ticketed_local', 'ticket_id': 'T-E08',
          'new_ticket_count': 1, 'control_commands': []}),
        ('L10', lambda: production_call('E09', temperature_c=None),
         {'risk_score': None, 'route': 'data_quality_hold'}),
        ('L11', lambda: production_call('E10', vibration_mm_s=8.0,
                                        temperature_c=80.0,
                                        interlock_trip=True, sensor_age_s=61),
         {'route': 'interlock_escalate', 'state': 'human_safety_response',
          'control_commands': []}),
        ('L12', duplicate_ticket,
         {'ticket_id': 'T-E08', 'new_ticket_count': 0,
          'replayed': True, 'control_commands': []}),
    ]
    for name, fn, expected in cases:
        check(name, fn, expected)


def run_experiment_snippet(entry: dict[str, Any], replacements: dict[str, str]) -> list:
    """用与网站滑块等价的赋值替换执行示例，收集 display 结果。"""
    source = entry['code']
    for name, value in replacements.items():
        source, count = re.subn(rf'^{re.escape(name)} = .+$', f'{name} = {value}',
                                source, count=1, flags=re.MULTILINE)
        assert count == 1, (entry['id'], name)
    shown: list[tuple[str, Any]] = []

    def display(data: Any, title: str = '', **_options: Any) -> None:
        shown.append((title, data))

    # 教学示例可以 print 解释；测试收集它而不污染最终通过数输出。
    with redirect_stdout(StringIO()):
        exec(compile(source, entry['id'], 'exec'), {'display': display})
    assert shown, entry['id']
    return shown


def test_snippets() -> None:
    """四个默认代码和四个关键参数切换，检查实际可视输出。"""
    entries = {entry['id']: entry for entry in json.loads(
        (ROOT / 'website/content-source/agent-course/experiments.json').read_text())}
    defaults = [
        ('S1', 'agent-rag', 'manager_preapproval'),
        ('S2', 'agent-office', 'slot_proposed'),
        ('S3', 'agent-routing', 'verify_identity'),
        ('S4', 'agent-production', 'warning_review'),
    ]
    for name, exp_id, decision in defaults:
        def go(exp_id=exp_id) -> dict[str, Any]:
            shown = run_experiment_snippet(entries[exp_id], {})
            rows = shown[0][1]
            actual = rows[0]
            return {'decision': actual.get('判定') or actual.get('路由')}
        check(name, go, {'decision': decision})
    switched = [
        ('S5', 'agent-rag', {'employee_access': 'False'}, 'restricted_transfer'),
        ('S6', 'agent-office', {'approve': 'True'}, 'slot_committed_local'),
        ('S7', 'agent-routing', {'safety_message': 'True'}, 'safety_escalate'),
        ('S8', 'agent-production', {'interlock_trip': 'True'}, 'interlock_escalate'),
    ]
    for name, exp_id, replacements, decision in switched:
        def go(exp_id=exp_id, replacements=replacements) -> dict[str, Any]:
            shown = run_experiment_snippet(entries[exp_id], replacements)
            rows = shown[0][1]
            actual = rows[0]
            return {'decision': actual.get('判定') or actual.get('路由')}
        check(name, go, {'decision': decision})


def main() -> int:
    test_policy()
    test_office()
    test_routing()
    test_production()
    test_snippets()
    total = PASSED + len(FAILED)
    for failure in FAILED:
        print('FAIL', failure)
    print(f'教学标准样本：40 组；交互代码检查：8 组；通过 {PASSED}/{total}')
    return 0 if not FAILED and total == 48 else 1


if __name__ == '__main__':
    raise SystemExit(main())
