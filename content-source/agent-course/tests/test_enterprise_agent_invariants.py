"""Independent offline review: rule boundaries, adversarial replay, real parameter effects.

Run with Python 3.11+: PYTHONPATH=src python3 tests/test_enterprise_agent_invariants.py
Exit 1 means at least one expected safety/property check failed. No production files change.
The JSON records include exact inputs via the name and actual result; tests use no network.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/bdm_decision/cases/week14_enterprise_agents.py'
OUT = Path(__file__).with_name('agent-lab-invariant-results.json')
sys.path.insert(0, str(ROOT / 'src'))
spec = importlib.util.spec_from_file_location('independent_agent_module', SOURCE)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)
records = []


def check(group, name, fn, predicate, severity='regression'):
    try:
        actual = fn()
        passed = bool(predicate(actual))
        error = None
    except Exception as exc:
        actual, passed, error = None, False, f'{type(exc).__name__}: {exc}'
    records.append(dict(group=group, name=name, passed=passed, severity=severity,
                        actual=actual, error=error))


def policy(**kw):
    return m.answer_policy('住宿', amount_yuan=kw.pop('amount_yuan', 400), **kw)


def production(e='P', **kw):
    defaults = dict(vibration_mm_s=7.9, temperature_c=79, sensor_age_s=20)
    defaults.update(kw)
    return m.handle_production_event(e, **defaults)


def fields(**expected):
    return lambda actual: all(actual.get(k) == v for k, v in expected.items())


# 1. Boundaries are hand-derived from the policy, not copied from the implementation.
for asof, amount, decision, evidence in [
    ('2026-09-30', 350, 'eligible', 'HOTEL-v2'),
    ('2026-09-30', 350.01, 'manager_preapproval', 'HOTEL-v2'),
    ('2026-09-30', 500, 'manager_preapproval', 'HOTEL-v2'),
    ('2026-09-30', 500.01, 'outside_policy', 'HOTEL-v2'),
    ('2026-10-01', 400, 'eligible', 'HOTEL-v3'),
    ('2026-10-01', 400.01, 'manager_preapproval', 'HOTEL-v3'),
    ('2026-10-01', 600, 'manager_preapproval', 'HOTEL-v3'),
    ('2026-10-01', 600.01, 'outside_policy', 'HOTEL-v3'),
]:
    check('policy boundaries', f'{asof}; amount={amount}',
          lambda a=asof, v=amount: policy(as_of=a, amount_yuan=v),
          fields(decision=decision, evidence_ids=[evidence]))
for amount in [None, True, -1, float('nan'), float('inf')]:
    check('policy validation', f'invalid amount={amount!r}',
          lambda v=amount: policy(amount_yuan=v), fields(decision='clarify'))
for day, expected in [(30, 'within_window'), (31, 'late_review')]:
    check('policy boundaries', f'invoice days={day}',
          lambda v=day: m.answer_policy('发票', days_after_trip=v),
          fields(decision=expected))


# 2. Version/date/permission/conflicting evidence are independently injected.
duplicate = deepcopy(m.POLICY_DOCUMENTS[-3])  # HOTEL-v3
duplicate.update(id='HOTEL-v3-CONFLICT', automatic_limit=999)
check('evidence', 'conflicting highest-version hotel evidence',
      lambda: policy(documents=m.POLICY_DOCUMENTS + (duplicate,)),
      fields(decision='conflict_review', evidence_ids=[]))
for kw in [dict(role='guest'), dict(as_of='2025-12-31'), dict(region='international')]:
    check('evidence', f'inaccessible/absent evidence {kw}', lambda kw=kw: policy(**kw),
          lambda r: not r['evidence_ids'] and not r['clause_summary'])
check('evidence', 'salary never emits restricted fact even for HR',
      lambda: m.answer_policy('薪资', role='hr'),
      fields(decision='restricted_transfer', evidence_ids=[], clause_summary=''))
check('evidence', 'mixed intents require clarification',
      lambda: m.answer_policy('住宿和发票', amount_yuan=400, days_after_trip=3),
      fields(decision='clarify', evidence_ids=[]))


# 3. Approved material and permission are both required; draft v2 must not beat v1.
check('research', 'engineer reads approved chip v1, not draft v2',
      lambda: m.research_answer('芯片接口', role='engineer'),
      fields(evidence_ids=['R-CHIP-v1'], answer_fact='接口额定电压 3.3 V。'))
check('research', 'employee cannot read chip fact',
      lambda: m.research_answer('芯片接口', role='employee'),
      fields(decision='access_denied', evidence_ids=[], answer_fact=None))
rd = deepcopy(m.RESEARCH_DOCUMENTS[1]); rd.update(id='R-VIB-v2-CONFLICT', fact='相反事实')
check('research', 'conflicting approved highest versions stop answering',
      lambda: m.research_answer('泵振动', documents=m.RESEARCH_DOCUMENTS + (rd,)),
      fields(decision='conflict_review', evidence_ids=[], answer_fact=None))


# 4. Proposal approval must not transfer to a different participant set or event.
def meeting_approve(people, token, authenticated=True, event='MA'):
    ledger = {}
    m.propose_meeting(people, event_id=event, ledger=ledger)
    return m.approve_meeting(event, approval_id=token,
                            organizer_authenticated=authenticated, ledger=ledger)

for people, token, auth, expected in [
    (['李', '王'], 'ORG-1', False, 'proposed'),
    (['李', '赵'], 'ORG-1', True, 'proposed'),
    (['王', '赵'], 'ORG-1', True, 'proposed'),
    (['李', '王'], 'APPROVE:OTHER:S2', True, 'proposed'),
    (['李', '王'], 'APPROVE:MA:S2', True, 'committed'),
    (['李', '王', '赵'], 'APPROVE:MA:None', True, 'conflict'),
]:
    check('meeting binding', f'people={people}; token={token}; auth={auth}',
          lambda p=people,t=token,a=auth: meeting_approve(p,t,a), fields(state=expected))


# 5. Exact duplicate requests are safe, and returned dictionaries do not alias history.
def exact_ticket_replay():
    ledger = {}
    one = production('DUP', vibration_mm_s=8, ledger=ledger)
    assert one['state'] == 'proposed'
    approved = m.approve_production_event('DUP', approval_by='maintenance_lead', ledger=ledger)
    again = production('DUP', vibration_mm_s=8, ledger=ledger)
    return dict(first=approved, second=again)

check('idempotency', 'approved exact duplicate creates no second ticket', exact_ticket_replay,
      lambda r: r['first']['new_ticket_count'] == 1 and
                r['second']['new_ticket_count'] == 0 and
                r['first']['ticket_id'] == r['second']['ticket_id'])

def no_alias():
    ledger = {}
    result = production('ALIAS', vibration_mm_s=8, ledger=ledger)
    result['matched_signals'].clear()
    result['state'] = 'ticketed_local'
    return production('ALIAS', vibration_mm_s=8, ledger=ledger)

check('idempotency', 'return-value mutation does not mutate ledger', no_alias,
      fields(state='proposed', matched_signals=['vibration']))


# 6. Multi-intent priority is computed from the declared safety>refund>order>product order.
for text, route in [
    ('受伤，需要退款和物流，规格是什么', 'safety_escalate'),
    ('退货，订单物流，功率是什么', 'verify_identity'),
    ('订单物流及功率规格', 'order_status'),
    ('功率规格', 'product_fact'),
]:
    check('customer priority', text,
          lambda t=text: m.route_customer('C', message=t, verified=('退货' not in t),
                                           customer_id='U1', order_id='O100', product_id='P1'),
          fields(route=route))
check('customer privacy', 'verified different customer never reads O100',
      lambda: m.route_customer('PRIVATE', message='物流', verified=True,
                               customer_id='U2', order_id='O100'),
      fields(route='privacy_block', visible_fact=None, evidence_ids=[]))
for day, expected in [(14, 'refund_review'), (15, 'exception_review')]:
    check('customer priority', f'refund boundary days={day}',
          lambda d=day: m.route_customer('R', message='退款', verified=True,
                                         days_since_purchase=d, unopened=True),
          fields(route=expected, state='pending_human', visible_fact=None))


# 7. Exhaustively test threshold equality, freshness and read-only interlock precedence.
for vibration, temp, quality, age, trip in itertools.product(
        [7.9, 8.0, 8.1], [79, 80, 81], ['good', 'bad'], [60, 61], [False, True]):
    score = int(vibration >= 8) + int(temp >= 80) + int(quality == 'bad')
    expected = ('interlock_escalate' if trip else 'data_quality_hold' if age > 60 else
                'monitor' if score == 0 else 'warning_review' if score == 1 else 'high_review')
    check('production grid', f'v={vibration}; t={temp}; q={quality}; age={age}; trip={trip}',
          lambda v=vibration,t=temp,q=quality,a=age,i=trip:
              production(vibration_mm_s=v, temperature_c=t, quality_flag=q,
                         sensor_age_s=a, interlock_trip=i, approval_by='employee'),
          lambda r,e=expected,s=score,a=age,i=trip:
              r['route'] == e and r['control_commands'] == [] and
              r['new_ticket_count'] == 0 and r['ticket_id'] is None and
              (r['risk_score'] is None if i or a > 60 else r['risk_score'] == s))


# 8. Missing, stale, malformed and future data cannot imply normality.
for field, bad in [
    ('vibration_mm_s', None), ('temperature_c', float('nan')),
    ('temperature_c', float('inf')), ('sensor_age_s', True),
    ('sensor_age_s', -1), ('machine_id', 'M99'), ('quality_flag', 'unknown'),
    ('event_time', '2026-10-14T00:00:00'),
    ('event_time', '2026-10-13T19:00:00+08:00'),
]:
    check('production invalid data', f'{field}={bad!r}',
          lambda f=field,b=bad: production(**{f:b}),
          fields(route='data_quality_hold', risk_score=None, control_commands=[]))
check('production invalid data', 'true interlock outranks missing data and stale age',
      lambda: production(interlock_trip=True, temperature_c=None, sensor_age_s=100),
      fields(route='interlock_escalate', state='human_safety_response', control_commands=[]))


# 9. Adversarial cache reuse must not bypass current authorization or safety evidence.
def customer_changed_identity():
    ledger = {}
    m.route_customer('SAME', customer_id='U1', verified=True, message='物流',
                     order_id='O100', ledger=ledger)
    return m.route_customer('SAME', customer_id='U2', verified=True, message='物流',
                            order_id='O100', ledger=ledger)

check('adversarial replay', 'same event but changed customer must not expose cached order',
      customer_changed_identity, lambda r: not r.get('visible_fact'), 'blocker')

def customer_safety_update():
    ledger = {}
    m.route_customer('SAME', customer_id='U1', verified=True, message='物流',
                     order_id='O100', ledger=ledger)
    return m.route_customer('SAME', customer_id='U1', verified=True, message='设备冒烟和物流',
                            order_id='O100', ledger=ledger)

check('adversarial replay', 'changed same-id safety message must not replay order answer',
      customer_safety_update,
      lambda r: r.get('route') in ['safety_escalate', 'event_conflict'], 'blocker')

def production_safety_update():
    ledger = {}
    production('SAME', ledger=ledger)
    return production('SAME', ledger=ledger, interlock_trip=True)

check('adversarial replay', 'same-id new interlock must not replay monitor',
      production_safety_update,
      lambda r: r.get('route') in ['interlock_escalate', 'event_conflict'], 'blocker')

def cross_task_collision():
    ledger = {}
    m.propose_meeting(['李','王'], event_id='COLLIDE', ledger=ledger)
    return production('COLLIDE', interlock_trip=True, ledger=ledger)

check('adversarial replay', 'shared Harness ledger must isolate task kinds',
      cross_task_collision,
      lambda r: r.get('route') in ['interlock_escalate', 'event_conflict'], 'blocker')


# 10. JSON/API boundary: a truthy string is not an authenticated Boolean.
check('boolean validation', "verified='false' must not grant order access",
      lambda: m.route_customer('BOOL', customer_id='U1', verified='false',
                               message='物流', order_id='O100'),
      lambda r: r['route'] != 'order_status' and not r['visible_fact'], 'blocker')
check('boolean validation', "organizer_authenticated='false' must not approve",
      lambda: meeting_approve(['李','王'], 'ORG-1', authenticated='false'),
      lambda r: r['state'] != 'committed', 'blocker')
for value in [1, 'true', None]:
    check('boolean validation', f'invalid interlock_trip={value!r} must hold or escalate',
          lambda v=value: production(interlock_trip=v),
          lambda r: r['route'] == 'invalid_input' and r['control_commands'] == [], 'blocker')


# 10b. Revocation, altered evidence/version, and approvals on an already approved item.
def revoked_customer():
    ledger = {}
    m.route_customer('REVOKE', customer_id='U1', verified=True, message='物流', order_id='O100', ledger=ledger)
    return m.route_customer('REVOKE', customer_id='U1', verified=False, message='物流', order_id='O100', ledger=ledger)

check('approval and version binding', 'same-principal verification revoked cannot replay fact',
      revoked_customer, lambda r: not r.get('visible_fact') and r.get('route') != 'order_status')

def meeting_token_reuse():
    ledger = {}
    m.propose_meeting(['李','王'], event_id='ONE', ledger=ledger)
    m.approve_meeting('ONE', approval_id='ORG-1', organizer_authenticated=True, ledger=ledger)
    m.propose_meeting(['李','王'], event_id='TWO', ledger=ledger)
    return m.approve_meeting('TWO', approval_id='ORG-1', organizer_authenticated=True, ledger=ledger)

check('approval and version binding', 'one ORG-1 approval cannot approve two event IDs',
      meeting_token_reuse, lambda r: r['state'] != 'committed')

def meeting_payload_change():
    ledger = {}
    m.propose_meeting(['李','王'], event_id='MP', ledger=ledger)
    return m.propose_meeting(['李','赵'], event_id='MP', ledger=ledger)

check('approval and version binding', 'same meeting ID changed participants explicitly conflicts',
      meeting_payload_change, fields(decision='event_conflict', proposal_slot=None))

def meeting_revoked():
    ledger = {}
    m.propose_meeting(['李','王'], event_id='MR', ledger=ledger)
    m.approve_meeting('MR', approval_id='ORG-1', organizer_authenticated=True, ledger=ledger)
    return m.approve_meeting('MR', approval_id='ORG-1', organizer_authenticated=False, ledger=ledger)

check('approval and version binding', 'unauthenticated replay of committed meeting does not approve',
      meeting_revoked, lambda r: r['state'] != 'committed')

def production_wrong_approver():
    ledger = {}
    production('PA', vibration_mm_s=8, ledger=ledger)
    m.approve_production_event('PA', approval_by='maintenance_lead', ledger=ledger)
    return m.approve_production_event('PA', approval_by='employee', ledger=ledger)

check('approval and version binding', 'wrong approver cannot replay approved work order',
      production_wrong_approver,
      lambda r: r['state'] != 'ticketed_local' and r['new_ticket_count'] == 0)

def altered_order_version():
    ledger = {}
    m.route_customer('VERSION', customer_id='U1', verified=True, message='物流', order_id='O100', ledger=ledger)
    original = deepcopy(m.ORDERS)
    try:
        m.ORDERS['O100']['status'] = '已取消'
        return m.route_customer('VERSION', customer_id='U1', verified=True, message='物流', order_id='O100', ledger=ledger)
    finally:
        m.ORDERS.clear(); m.ORDERS.update(original)

check('approval and version binding', 'order-data version change cannot replay stale fact',
      altered_order_version, fields(route='event_conflict', visible_fact=None))

def altered_threshold():
    ledger = {}
    production('THRESHOLD', vibration_mm_s=8, ledger=ledger)
    original = m.TEACHING_VIBRATION_LIMIT
    try:
        m.TEACHING_VIBRATION_LIMIT = 9
        return m.approve_production_event('THRESHOLD', approval_by='maintenance_lead', ledger=ledger)
    finally:
        m.TEACHING_VIBRATION_LIMIT = original

check('approval and version binding', 'changed threshold version blocks old proposal approval',
      altered_threshold, fields(route='event_conflict', ticket_id=None, new_ticket_count=0))

def altered_calendar():
    ledger = {}
    m.propose_meeting(['李','王'], event_id='CALENDAR', ledger=ledger)
    original = m.MEETING_SLOTS['S2']
    try:
        m.MEETING_SLOTS['S2'] = '16:00'
        return m.approve_meeting('CALENDAR', approval_id='ORG-1', organizer_authenticated=True, ledger=ledger)
    finally:
        m.MEETING_SLOTS['S2'] = original

check('approval and version binding', 'changed calendar version blocks old proposal approval',
      altered_calendar, fields(decision='event_conflict', proposal_slot=None))

check('evidence', 'international invoice is outside the teaching policy scope',
      lambda: m.answer_policy('发票',region='international',days_after_trip=20),
      fields(decision='no_evidence',evidence_ids=[]))
check('evidence', 'policy experiment exposes no callable approval shortcut',
      lambda: hasattr(m,'approve_policy'),lambda exists: exists is False)
check('evidence', 'manager-preapproval remains pending rather than approved',
      lambda: policy(amount_yuan=450),fields(state='pending_review',decision='manager_preapproval'))
check('policy boundaries', 'fractional amount matches continuous-range policy summary',
      lambda: policy(amount_yuan=400.01),
      lambda result: result['decision']=='manager_preapproval' and '超过 400 且不超过 600' in result['clause_summary'])


def invalid_product_approval():
    previous = m.PRODUCTS['P1']['approved']
    try:
        m.PRODUCTS['P1']['approved'] = 'false'
        return m.route_customer('PRODUCTBOOL', message='规格', product_id='P1')
    finally:
        m.PRODUCTS['P1']['approved'] = previous

check('boolean validation', 'product approved string false cannot expose a formal fact',
      invalid_product_approval, fields(route='clarify', visible_fact=None))

check('production invalid data', 'missing lot identity must hold',
      lambda: production(lot_id=None), fields(route='data_quality_hold', risk_score=None))


# 11. Every exposed control must alter actual executed results for a suitable scenario.
entries = json.loads((ROOT/'website/content-source/agent-course/experiments.json').read_text())

def run_snippet(entry, changes):
    code = entry['code']
    for name, value in changes.items():
        code, n = re.subn(rf'^{re.escape(name)} = .+$', f'{name} = {value!r}',
                          code, count=1, flags=re.MULTILINE)
        assert n == 1, f'control has no editable assignment: {name}'
    displays = []
    def display(data, title='', **options):
        displays.append(dict(title=title,data=data,options=options))
    with redirect_stdout(StringIO()):
        exec(compile(code, entry['id'], 'exec'), {'display':display})
    return displays

alternatives = dict(amount_yuan=0, employee_access=False, approve=True,
                    engineer_access=True, verified=True, safety_message=True,
                    vibration_mm_s=0, stale_reading=True, interlock_trip=True,
                    approve_ticket=True)
for entry in entries:
    baseline = run_snippet(entry, {})
    for p in entry['params']:
        check('executed frontend controls', f"{entry['id']}:{p['name']}",
              lambda e=entry,p=p: run_snippet(e,{p['name']:alternatives[p['name']]}),
              lambda r,b=baseline: bool(r) and r != b)
    check('deterministic boundary', f"{entry['id']} repeat independent run",
          lambda e=entry: run_snippet(e,{}), lambda r,b=baseline: r == b)

def frontend_replay_output():
    entry = next(e for e in entries if e['id'] == 'agent-routing')
    captured = StringIO()
    with redirect_stdout(captured):
        exec(compile(entry['code'],entry['id'],'exec'),{'display':lambda *a,**k:None})
    return captured.getvalue()

check('executed frontend controls', 'customer exact replay genuinely reports True',
      frontend_replay_output, lambda text: 'True' in text and 'False' not in text)

result = dict(sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              checks=len(records), passed=sum(r['passed'] for r in records),
              failures=[r for r in records if not r['passed']], records=records)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str))
for r in result['failures']:
    print('FAIL',r['group'],r['name'],json.dumps(r['actual'],ensure_ascii=False),r['error'] or '')
print(f"Independent checks: {result['passed']}/{result['checks']}; groups={len(set(r['group'] for r in records))}; results={OUT}")
raise SystemExit(bool(result['failures']))
