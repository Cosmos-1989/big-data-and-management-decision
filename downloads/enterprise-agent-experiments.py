"""第 14 章：四个完全离线、确定性的企业 Agent 教学实验。

本模块只处理虚构的制度、日历、客服记录和设备事件。所有状态均保存在调用方传入
的内存字典中；不调用模型、网络、日历、客服系统或工业控制系统。规则透明，便于
学生手算、修改输入并检查权限、证据、审批、幂等和失败分支。
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
import hashlib
import json
from math import isfinite
from typing import Any, MutableMapping


# 制度日期、金额和天数只用于教学，不代表真实企业制度或法律要求。
POLICY_DOCUMENTS: tuple[dict[str, Any], ...] = (
    {
        "id": "HOTEL-v2", "intent": "hotel", "version": 2,
        "valid_from": "2026-01-01", "valid_to": "2026-09-30",
        "region": "domestic", "roles": ("employee", "manager"),
        "automatic_limit": 350, "review_limit": 500,
        "summary": "国内住宿每晚不超过 350 元；超过 350 且不超过 500 元须预先由部门经理批准。",
    },
    {
        "id": "HOTEL-v3", "intent": "hotel", "version": 3,
        "valid_from": "2026-10-01", "valid_to": None,
        "region": "domestic", "roles": ("employee", "manager"),
        "automatic_limit": 400, "review_limit": 600,
        "summary": "国内住宿每晚不超过 400 元；超过 400 且不超过 600 元须预先由部门经理批准。",
    },
    {
        "id": "INVOICE-v1", "intent": "invoice", "version": 1,
        "valid_from": "2026-01-01", "valid_to": None,
        "region": "domestic", "roles": ("employee", "manager"),
        "days_limit": 30,
        "summary": "教学设定：出差结束后 30 个自然日内提交合规发票。",
    },
    {
        "id": "PAYROLL-v1", "intent": "salary", "version": 1,
        "valid_from": "2026-01-01", "valid_to": None,
        "region": "all", "roles": ("hr",),
        "summary": "薪资明细仅由受控的人力资源系统处理。",
    },
)


# 固定词典替代自然语言模型。多意图或无匹配时应让用户澄清。
POLICY_KEYWORDS = {
    "hotel": ("住宿", "酒店"),
    "invoice": ("发票",),
    "salary": ("工资", "薪资"),
}


def _policy_result(decision: str, *, evidence_ids: list[str] | None = None,
                   clause_summary: str = "", reason: str = "",
                   next_actor: str = "", state: str = "clarify") -> dict[str, Any]:
    """统一问答输出结构，让页面和测试都能检查证据与待办人。"""
    return {
        "decision": decision, "evidence_ids": evidence_ids or [],
        "clause_summary": clause_summary, "reason": reason,
        "next_actor": next_actor, "state": state,
    }


def answer_policy(question: str, *, role: str = "employee",
                  as_of: str = "2026-10-10", region: str = "domestic",
                  amount_yuan: float | None = None,
                  days_after_trip: int | None = None,
                  documents: tuple[dict[str, Any], ...] = POLICY_DOCUMENTS,
                  ) -> dict[str, Any]:
    """先检查权限和有效期，再按固定条款回答；没有证据时明确拒答。"""
    if not isinstance(question, str) or not question.strip():
        return _policy_result("clarify", reason="请说明要询问的制度主题。")

    # 关键词的出现只表示候选意图，不证明系统理解了任意自然语言。
    hits = [intent for intent, words in POLICY_KEYWORDS.items()
            if any(word in question for word in words)]
    if len(hits) != 1:
        reason = "问题同时涉及多个制度主题，请拆开提问。" if hits else "资料库中没有对应的制度主题。"
        return _policy_result("clarify", reason=reason)
    intent = hits[0]

    # 薪资明细即使有受限文件，也不在教学页面检索或显示正文。
    if intent == "salary":
        return _policy_result("restricted_transfer", reason="个人薪资不在本实验的可答范围。",
                              next_actor="受控 HR 系统", state="restricted")
    if role not in ("employee", "manager"):
        return _policy_result("restricted_transfer", reason="当前角色不可读取员工制度。",
                              next_actor="制度负责人", state="restricted")

    try:
        query_day = date.fromisoformat(as_of)
    except (TypeError, ValueError):
        return _policy_result("clarify", reason="请使用 YYYY-MM-DD 日期。")

    # 只从询问日期有效、地区适用、角色可见的文件中取证。
    candidates = []
    for doc in documents:
        if doc.get("intent") != intent or role not in doc.get("roles", ()):
            continue
        if doc.get("region") not in (region, "all"):
            continue
        try:
            start = date.fromisoformat(doc["valid_from"])
            end = date.fromisoformat(doc["valid_to"]) if doc.get("valid_to") else None
        except (KeyError, TypeError, ValueError):
            continue
        if start <= query_day and (end is None or query_day <= end):
            candidates.append(doc)
    if not candidates:
        return _policy_result("no_evidence", reason="指定日期或地区没有有效且可见的条款。",
                              next_actor="制度负责人")

    # 同版本文件若相互冲突，停止自动回答，不能任意挑选一份。
    newest = max(doc["version"] for doc in candidates)
    top = [doc for doc in candidates if doc["version"] == newest]
    if len(top) != 1:
        return _policy_result("conflict_review", reason="同一版本出现多个有效条款，需人工核对。",
                              next_actor="制度负责人", state="pending_review")
    doc = top[0]
    common = {"evidence_ids": [doc["id"]], "clause_summary": doc["summary"]}

    if intent == "hotel":
        if isinstance(amount_yuan, bool) or not isinstance(amount_yuan, (int, float)) \
                or not isfinite(amount_yuan) or amount_yuan < 0:
            return _policy_result("clarify", reason="请填写非负的每晚住宿金额。")
        if amount_yuan <= doc["automatic_limit"]:
            return _policy_result("eligible", reason="金额在该版条款的自动范围内。",
                                  state="answered", **common)
        if amount_yuan <= doc["review_limit"]:
            return _policy_result("manager_preapproval", reason="须在预订前由部门经理审批。",
                                  next_actor="部门经理", state="pending_review", **common)
        return _policy_result("outside_policy", reason="超出本条款支持范围，转人工核对例外。",
                              next_actor="制度负责人", state="pending_review", **common)

    # 发票逾期只进入人工例外复核；没有自动拒付动作。
    if isinstance(days_after_trip, bool) or not isinstance(days_after_trip, int) \
            or days_after_trip < 0:
        return _policy_result("clarify", reason="请填写非负的出差结束后自然日数。")
    if days_after_trip <= doc["days_limit"]:
        return _policy_result("within_window", reason="尚在教学条款规定的提交窗口内。",
                              state="answered", **common)
    return _policy_result("late_review", reason="超过普通提交窗口，交人工检查例外。",
                          next_actor="财务制度负责人", state="pending_review", **common)


def policy_threshold_rows() -> list[dict[str, Any]]:
    """供已授权页面绘制金额阈值图，避免把制度版本当作连续趋势。"""
    return [{"版本": doc["id"], "自动额度": doc["automatic_limit"],
             "预审上限": doc["review_limit"]}
            for doc in POLICY_DOCUMENTS if doc["intent"] == "hotel"]


# 会议日历与研发文档均为固定教学样例，不连接真实办公服务。
MEETING_SLOTS = {"S1": "09:00", "S2": "10:00", "S3": "14:00"}
AVAILABILITY = {
    "李": frozenset(("S1", "S2")),
    "王": frozenset(("S2", "S3")),
    "赵": frozenset(("S1", "S3")),
}
RESEARCH_DOCUMENTS: tuple[dict[str, Any], ...] = (
    {"id": "R-VIB-v1", "topic": "pump_vibration", "version": 1,
     "status": "superseded", "roles": ("employee", "engineer"),
     "fact": "旧版振动记录。"},
    {"id": "R-VIB-v2", "topic": "pump_vibration", "version": 2,
     "status": "approved", "roles": ("employee", "engineer"),
     "fact": "先核对传感器校准与轴承检查记录。"},
    {"id": "R-CHIP-v1", "topic": "chip_interface", "version": 1,
     "status": "approved", "roles": ("engineer",),
     "fact": "接口额定电压 3.3 V。"},
    {"id": "R-CHIP-draft", "topic": "chip_interface", "version": 2,
     "status": "draft", "roles": ("engineer",),
     "fact": "未发布的设计草稿，不可引用。"},
)


# 指纹绑定教学规则版本。它证明同次模拟输入未改变，不是密码学身份认证。
RULES_VERSION = "enterprise-agents-20261012-v2"


def _ledger_key(task: str, principal: str, event_id: str) -> str:
    """任务、调用身份、事件号三者共同确定去重范围，禁止跨任务复用结果。"""
    return json.dumps([task, principal, event_id], ensure_ascii=False)


def _typed_value(value: Any) -> Any:
    """保留类型以区分 True/1；非有限读数也可留痕，但不会被认定为有效数据。"""
    if isinstance(value, dict):
        return {key: _typed_value(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [type(value).__name__, [_typed_value(item) for item in value]]
    return [type(value).__name__, repr(value)]


def _fingerprint(request: dict[str, Any]) -> str:
    canonical = json.dumps(_typed_value(request), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _calendar_version() -> str:
    """时段或任一参与人的空档变化，都会使旧提案失效。"""
    return _fingerprint({
        "slots": MEETING_SLOTS,
        "availability": {name: sorted(slots) for name, slots in AVAILABILITY.items()},
    })


def _event_conflict(reason: str = "同一事件号的身份、载荷或规则版本不一致，请人工核对。") -> dict[str, Any]:
    """冲突不返回旧敏感事实、旧批准状态或设备指令。"""
    return {"decision": "event_conflict", "route": "event_conflict", "state": "conflict",
            "visible_fact": None, "answer_fact": None, "evidence_ids": [],
            "risk_score": None, "matched_signals": [], "matched_keywords": [],
            "ticket_id": None, "new_ticket_count": 0, "control_commands": [],
            "proposal_slot": None, "next_actor": "人工责任人", "reason": reason}


def _record_valid(record: dict[str, Any], task: str, principal: str, event_id: str) -> bool:
    """审批前再次核查记录结构、请求指纹和教学规则版本。内存账本须由 Harness 管理。"""
    if not isinstance(record, dict):
        return False
    request = record.get("request")
    return (record.get("task") == task and record.get("principal") == principal and
            record.get("event_id") == event_id and record.get("rules_version") == RULES_VERSION and
            isinstance(request, dict) and record.get("fingerprint") == _fingerprint(request) and
            isinstance(record.get("result"), dict) and
            record.get("result_fingerprint") == _fingerprint(record["result"]))


def _replayed(ledger: MutableMapping[str, dict[str, Any]] | None,
              event_id: str, *, task: str, principal: str,
              request: dict[str, Any]) -> dict[str, Any] | None:
    """只有任务、身份、事件及完整请求相同才回放；载荷变化必须显式报冲突。"""
    key = _ledger_key(task, principal, event_id)
    if ledger is not None and key in ledger:
        record = ledger[key]
        if not _record_valid(record, task, principal, event_id) or \
                record["fingerprint"] != _fingerprint(request):
            return _event_conflict()
        result = deepcopy(record["result"])
        result["replayed"] = True
        if "new_ticket_count" in result:
            result["new_ticket_count"] = 0
        return result
    return None


def _remember(ledger: MutableMapping[str, dict[str, Any]] | None,
              event_id: str, result: dict[str, Any], *, task: str,
              principal: str, request: dict[str, Any]) -> dict[str, Any]:
    """保存请求和结果副本。审批仅推进同一提案，不改变原请求指纹。"""
    if ledger is not None:
        ledger[_ledger_key(task, principal, event_id)] = {
            "task": task, "principal": principal, "event_id": event_id,
            "rules_version": RULES_VERSION, "request": deepcopy(request),
            "fingerprint": _fingerprint(request), "result": deepcopy(result),
            "result_fingerprint": _fingerprint(result),
        }
    return result


def propose_meeting(participants: list[str] | tuple[str, ...], *, event_id: str,
                    organizer_id: str = "teaching-organizer",
                    ledger: MutableMapping[str, dict[str, Any]] | None = None,
                    ) -> dict[str, Any]:
    """求共同空档并提出建议，不发送邀请。"""
    if not isinstance(event_id, str) or not event_id.strip() or \
            not isinstance(organizer_id, str) or not organizer_id.strip() or \
            not isinstance(participants, (tuple, list)) or \
            any(not isinstance(name, str) for name in participants):
        return {"decision": "invalid_input", "proposal_slot": None, "state": "clarify",
                "reason": "事件号、组织者和参与人必须具有规定类型。"}
    unique = tuple(sorted(set(participants)))
    request = {"participants": unique, "calendar_version": _calendar_version()}
    previous = _replayed(ledger, event_id, task="meeting", principal=organizer_id, request=request)
    if previous is not None:
        return previous
    if not event_id or not unique or any(name not in AVAILABILITY for name in unique):
        result = {"decision": "invalid_input", "proposal_slot": None,
                  "reason": "请提供事件号和已知参与人。", "state": "clarify",
                  "next_actor": "会议组织者", "participants": list(unique)}
        return _remember(ledger, event_id, result, task="meeting",
                         principal=organizer_id, request=request)

    # 集合交集保证每位参会人均可用；按 S1、S2、S3 顺序取最早。
    common = set(MEETING_SLOTS)
    for name in unique:
        common &= AVAILABILITY[name]
    slot = next((key for key in MEETING_SLOTS if key in common), None)
    if slot is None:
        result = {"decision": "conflict", "proposal_slot": None,
                  "reason": "没有所有参与人的共同空档。", "state": "conflict",
                  "next_actor": "会议组织者", "participants": list(unique)}
    else:
        result = {"decision": "slot_proposed", "proposal_slot": slot,
                  "proposal_time": MEETING_SLOTS[slot],
                  "reason": "取所有参与人共同可用的最早时段。", "state": "proposed",
                  "next_actor": "会议组织者", "participants": list(unique)}
    return _remember(ledger, event_id, result, task="meeting",
                     principal=organizer_id, request=request)


def approve_meeting(event_id: str, *, approval_id: str,
                    organizer_authenticated: bool,
                    organizer_id: str = "teaching-organizer",
                    ledger: MutableMapping[str, dict[str, Any]],
                    ) -> dict[str, Any]:
    """只将本地提案转为模拟提交；审批号必须与提案匹配。"""
    if not isinstance(organizer_authenticated, bool) or organizer_authenticated is not True:
        return {"decision": "approval_denied", "state": "proposed", "proposal_slot": None,
                "reason": "组织者身份必须以明确的布尔值 True 表示；未通过身份核验。"}
    key = _ledger_key("meeting", organizer_id, event_id)
    if key not in ledger:
        return {"decision": "missing_proposal", "state": "clarify",
                "reason": "请先生成会议提案。", "proposal_slot": None}
    record = ledger[key]
    if not _record_valid(record, "meeting", organizer_id, event_id):
        return _event_conflict("会议提案版本或请求指纹不一致，不能审批。")
    if record["request"].get("calendar_version") != _calendar_version():
        return _event_conflict("日历版本已经变化，请重新生成并审核会议提案。")
    saved = deepcopy(record["result"])
    slot = saved.get("proposal_slot")
    participants = frozenset(saved.get("participants", []))
    standard_approval = (approval_id == "ORG-1" and
                         participants == frozenset(("李", "王")) and slot == "S2")
    local_approval = approval_id == f"APPROVE:{event_id}:{slot}"
    approval_key = _ledger_key("meeting-approval", organizer_id, approval_id)
    binding = {"proposal_key": key, "fingerprint": record["fingerprint"]}
    prior_approval = ledger.get(approval_key)
    if not isinstance(approval_id, str) or not (standard_approval or local_approval) or \
            frozenset(record["request"]["participants"]) != participants or \
            (prior_approval is not None and prior_approval != binding) or \
            saved.get("state") not in ("proposed", "committed"):
        denied_state = saved.get("state") if saved.get("state") != "committed" else "restricted"
        return {"decision": "approval_denied", "state": denied_state,
                "proposal_slot": None,
                "approval_error": "组织者身份或审批号不匹配，不能批准或回放已批准状态。",
                "reason": "审批必须绑定同一身份、事件、参与人、时段和日历版本。"}
    if saved.get("state") == "committed":
        if saved.get("approval_id") != approval_id:
            return _event_conflict("已批准会议的审批标识发生变化。")
        saved["replayed"] = True
        return saved
    saved.update(decision="slot_committed_local", state="committed",
                 approval_id=approval_id, next_actor="参会人",
                 reason="仅在浏览器内记录了经组织者确认的模拟会议。")
    record["result"] = deepcopy(saved)
    record["result_fingerprint"] = _fingerprint(saved)
    ledger[approval_key] = binding
    return saved


def research_answer(topic: str, *, role: str = "employee",
                    documents: tuple[dict[str, Any], ...] = RESEARCH_DOCUMENTS,
                    ) -> dict[str, Any]:
    """只引用已批准且当前角色可读的最新版研发资料。"""
    if not isinstance(topic, str):
        topic = ""
    matches = []
    if "泵振动" in topic:
        matches.append("pump_vibration")
    if "芯片接口" in topic:
        matches.append("chip_interface")
    if len(matches) != 1:
        return {"decision": "no_evidence", "answer_fact": None,
                "evidence_ids": [], "state": "clarify",
                "reason": "没有唯一匹配的已发布资料主题。"}
    approved = [doc for doc in documents if doc.get("topic") == matches[0]
                and doc.get("status") == "approved"]
    visible = [doc for doc in approved if role in doc.get("roles", ())]
    if not visible:
        decision = "access_denied" if approved else "no_evidence"
        return {"decision": decision, "answer_fact": None,
                "evidence_ids": [], "state": "restricted" if approved else "clarify",
                "reason": "当前角色无权查看该主题资料。" if approved else "没有已批准资料。"}
    version = max(doc["version"] for doc in visible)
    latest = [doc for doc in visible if doc["version"] == version]
    if len(latest) != 1:
        return {"decision": "conflict_review", "answer_fact": None,
                "evidence_ids": [], "state": "pending_review",
                "reason": "同版本资料冲突，需研发负责人核对。"}
    chosen = latest[0]
    return {"decision": "answered", "answer_fact": chosen["fact"],
            "evidence_ids": [chosen["id"]], "state": "answered",
            "reason": "已按批准状态、访问角色和版本筛选。"}


def office_assist(task: str, *, event_id: str = "OFFICE-1",
                  participants: list[str] | tuple[str, ...] = (),
                  topic: str = "", role: str = "employee",
                  organizer_id: str = "teaching-organizer",
                  ledger: MutableMapping[str, dict[str, Any]] | None = None,
                  ) -> dict[str, Any]:
    """用明确任务类型选择 Skill；这里没有模型规划或外部工具。"""
    if task == "meeting":
        return propose_meeting(participants, event_id=event_id,
                               organizer_id=organizer_id, ledger=ledger)
    if task == "research":
        return research_answer(topic, role=role)
    return {"decision": "clarify", "state": "clarify",
            "reason": "请选择排期或研发资料检索。"}


# 客服样例的个人与订单标识完全虚构。14 天规则是课堂参数。
ORDERS = {"O100": {"owner": "U1", "status": "已发货"},
          "O101": {"owner": "U2", "status": "待发货"}}
PRODUCTS = {"P1": {"fact": "额定功率 500 W", "approved": True}}
ROUTE_KEYWORDS = {
    "safety": ("受伤", "冒烟"),
    "refund": ("退款", "退货"),
    "order": ("物流", "订单"),
    "product": ("规格", "功率"),
}


def route_customer(event_id: str, *, customer_id: str = "U1",
                   verified: bool = False, message: str = "",
                   order_id: str | None = None,
                   days_since_purchase: int | None = None,
                   unopened: bool | None = None,
                   product_id: str | None = None,
                   ledger: MutableMapping[str, dict[str, Any]] | None = None,
                   ) -> dict[str, Any]:
    """按安全、退货、订单、产品的优先级路由，不支付或修改订单。"""
    if not isinstance(event_id, str) or not event_id.strip() or \
            not isinstance(customer_id, str) or not customer_id.strip() or \
            not isinstance(verified, bool):
        return {"route": "invalid_input", "visible_fact": None, "state": "clarify",
                "reason": "事件号、客户身份及核验标志必须具有规定类型。",
                "matched_keywords": [], "evidence_ids": [], "next_actor": "客户"}
    request = {"verified": verified, "message": message, "order_id": order_id,
               "days_since_purchase": days_since_purchase, "unopened": unopened,
               "product_id": product_id,
               "data_version": _fingerprint({"orders": ORDERS, "products": PRODUCTS})}
    previous = _replayed(ledger, event_id, task="customer", principal=customer_id, request=request)
    if previous is not None:
        return previous
    if not event_id or not isinstance(message, str):
        return _remember(ledger, event_id, {"route": "clarify", "visible_fact": None,
                         "state": "clarify", "reason": "请提供事件号与咨询内容。",
                         "matched_keywords": [], "evidence_ids": [], "next_actor": "客户"},
                         task="customer", principal=customer_id, request=request)
    hits = [intent for intent, words in ROUTE_KEYWORDS.items()
            if any(word in message for word in words)]
    base: dict[str, Any] = {"visible_fact": None, "matched_keywords": hits,
                            "evidence_ids": []}

    # 安全消息先交人工；这里仅显示通用提示，不诊断故障、不指导拆机。
    if "safety" in hits:
        result = {**base, "route": "safety_escalate",
                  "visible_fact": "请停止使用并联系人工安全值班组。",
                  "state": "pending_human", "next_actor": "安全值班组",
                  "reason": "命中安全词，优先于其他意图。"}
    elif "refund" in hits:
        if not verified:
            result = {**base, "route": "verify_identity", "state": "clarify",
                      "next_actor": "客户", "reason": "退货申请需要先核验客户身份。"}
        elif isinstance(days_since_purchase, bool) or not isinstance(days_since_purchase, int) \
                or days_since_purchase < 0 or not isinstance(unopened, bool):
            result = {**base, "route": "clarify", "state": "clarify",
                      "next_actor": "客户", "reason": "请补充购买后天数与商品是否未开封。"}
        elif days_since_purchase <= 14 and unopened:
            result = {**base, "route": "refund_review", "state": "pending_human",
                      "next_actor": "人工客服", "reason": "符合教学规则的普通审核入口；不会自动退款。"}
        else:
            result = {**base, "route": "exception_review", "state": "pending_human",
                      "next_actor": "人工客服", "reason": "进入例外复核，不自动拒绝或退款。"}
    elif "order" in hits:
        if not verified:
            result = {**base, "route": "verify_identity", "state": "clarify",
                      "next_actor": "客户", "reason": "查看订单前须先核验身份。"}
        elif order_id not in ORDERS:
            result = {**base, "route": "clarify", "state": "clarify",
                      "next_actor": "客户", "reason": "请核对订单编号。"}
        elif ORDERS[order_id]["owner"] != customer_id:
            result = {**base, "route": "privacy_block", "state": "restricted",
                      "next_actor": "人工客服", "reason": "订单与当前客户不匹配。"}
        else:
            result = {**base, "route": "order_status", "state": "answered",
                      "visible_fact": ORDERS[order_id]["status"],
                      "evidence_ids": [order_id], "next_actor": "客户",
                      "reason": "身份及订单归属均已在教学数据中核对。"}
    elif "product" in hits:
        product = PRODUCTS.get(product_id or "")
        if not product or product["approved"] is not True:
            result = {**base, "route": "clarify", "state": "clarify",
                      "next_actor": "客户", "reason": "没有该产品的已批准规格。"}
        else:
            result = {**base, "route": "product_fact", "state": "answered",
                      "visible_fact": product["fact"], "evidence_ids": [product_id],
                      "next_actor": "客户", "reason": "仅引用已批准的虚构产品资料。"}
    else:
        result = {**base, "route": "clarify", "state": "clarify",
                  "next_actor": "客户", "reason": "词典中没有该咨询主题。"}
    return _remember(ledger, event_id, result, task="customer",
                     principal=customer_id, request=request)


# 以下阈值只用于教学规则。真实设备的停启与联锁不受本模块控制。
TEACHING_VIBRATION_LIMIT = 8.0
TEACHING_TEMPERATURE_LIMIT = 80.0
TEACHING_SENSOR_AGE_LIMIT = 60
TEACHING_NOW = datetime(2026, 10, 13, 18, 0)


def _valid_nonnegative_number(value: Any) -> bool:
    """排除布尔值、缺失、非数及非有限值，避免把坏传感器读数判成正常。"""
    return isinstance(value, (int, float)) and not isinstance(value, bool) \
        and isfinite(value) and value >= 0


def handle_production_event(event_id: str, *, line_id: str = "L1",
                            machine_id: str = "M01", lot_id: str = "LOT-001",
                            vibration_mm_s: float | None = None,
                            temperature_c: float | None = None,
                            sensor_age_s: float | None = None,
                            quality_flag: str = "good",
                            interlock_trip: bool = False,
                            event_time: str | None = None,
                            approval_by: str | None = None,
                            observer_id: str = "teaching-observer",
                            ledger: MutableMapping[str, dict[str, Any]] | None = None,
                            ) -> dict[str, Any]:
    """只读分析传感器与联锁状态；绝无设备停启、复位或调参代码。"""
    if not isinstance(interlock_trip, bool) or not isinstance(event_id, str) or \
            not event_id.strip() or not isinstance(observer_id, str) or not observer_id.strip():
        return {"route": "invalid_input", "state": "clarify", "risk_score": None,
                "matched_signals": [], "evidence_event_id": None, "ticket_id": None,
                "new_ticket_count": 0, "control_commands": [],
                "next_actor": "数据与现场负责人",
                "reason": "事件号、观察身份或 PLC 联锁标志类型不合法；不能据此判断正常。"}
    request = {"line_id": line_id, "machine_id": machine_id, "lot_id": lot_id,
               "vibration_mm_s": vibration_mm_s, "temperature_c": temperature_c,
               "sensor_age_s": sensor_age_s, "quality_flag": quality_flag,
               "interlock_trip": interlock_trip, "event_time": event_time,
               "approval_by": approval_by,
               "thresholds": [TEACHING_VIBRATION_LIMIT, TEACHING_TEMPERATURE_LIMIT,
                              TEACHING_SENSOR_AGE_LIMIT]}
    previous = _replayed(ledger, event_id, task="production",
                         principal=observer_id, request=request)
    if previous is not None:
        if previous.get("route") == "event_conflict" and interlock_trip is True:
            previous.update(next_actor="现场值班工程师",
                            proposed_action="核对同号事件冲突，并按现场既有安全程序处置当前联锁上报。")
        return previous
    def remember(result: dict[str, Any]) -> dict[str, Any]:
        return _remember(ledger, event_id, result, task="production",
                         principal=observer_id, request=request)
    base: dict[str, Any] = {
        "event_id": event_id, "line_id": line_id, "machine_id": machine_id,
        "lot_id": lot_id, "risk_score": None, "matched_signals": [],
        "ticket_id": None, "new_ticket_count": 0, "control_commands": [],
        "evidence_event_id": event_id,
    }

    # PLC 联锁先于数据质量检查处理；它是只读输入，不是模型发出的命令。
    if interlock_trip is True:
        result = {**base, "route": "interlock_escalate",
                  "state": "human_safety_response", "next_actor": "现场值班工程师",
                  "proposed_action": "按现场既有安全程序人工处置。",
                  "reason": "PLC 已上报联锁，模型不发送任何设备控制命令。"}
        return remember(result)

    # 缺失、过期、非法设备或未来事件都应进入数据质量复核，而非正常分支。
    bad_time = False
    if event_time is not None:
        try:
            bad_time = datetime.fromisoformat(event_time) > TEACHING_NOW
        except (TypeError, ValueError):
            bad_time = True
    invalid = (not event_id or line_id != "L1" or machine_id != "M01" or
               not isinstance(lot_id, str) or not lot_id.strip() or
               not _valid_nonnegative_number(vibration_mm_s) or
               not _valid_nonnegative_number(temperature_c) or
               not _valid_nonnegative_number(sensor_age_s) or
               sensor_age_s > TEACHING_SENSOR_AGE_LIMIT or
               quality_flag not in ("good", "bad") or bad_time)
    if invalid:
        result = {**base, "route": "data_quality_hold", "state": "data_quality_hold",
                  "next_actor": "数据与现场负责人",
                  "proposed_action": "核查传感器、时间戳、设备与批次记录。",
                  "reason": "数据缺失、过期或不在教学规则的有效范围内。"}
        return remember(result)

    # 每个达到阈值的信号计 1 分；等于阈值也计入异常。
    signals = []
    if vibration_mm_s >= TEACHING_VIBRATION_LIMIT:
        signals.append("vibration")
    if temperature_c >= TEACHING_TEMPERATURE_LIMIT:
        signals.append("temperature")
    if quality_flag == "bad":
        signals.append("quality")
    score = len(signals)
    base.update(risk_score=score, matched_signals=signals)
    if score == 0:
        result = {**base, "route": "monitor", "state": "closed",
                  "next_actor": "现场班组",
                  "proposed_action": "按既有频率继续监测。",
                  "reason": "本教学规则的三项异常条件均未触发。"}
        return remember(result)

    route = "warning_review" if score == 1 else "high_review"
    action = "提出维护调查草稿；由维护负责人复核。"
    if "quality" in signals:
        action += " 同时请质量负责人决定是否隔离批次。"
    result = {**base, "route": route, "state": "proposed",
              "next_actor": "维护负责人", "draft_id": f"D-{event_id}",
              "proposed_action": action,
              "reason": f"命中 {score} 项教学异常条件；只生成调查建议。"}
    remember(result)
    if approval_by == "maintenance_lead":
        # 无外部账本时用局部账本完成同一调用中的模拟审批。
        if ledger is None:
            local_ledger: dict[str, dict[str, Any]] = {}
            _remember(local_ledger, event_id, result, task="production", principal=observer_id,
                      request=request)
            return approve_production_event(event_id, approval_by=approval_by,
                                            observer_id=observer_id, ledger=local_ledger)
        return approve_production_event(event_id, approval_by=approval_by,
                                        observer_id=observer_id, ledger=ledger)
    return result


def approve_production_event(event_id: str, *, approval_by: str,
                             observer_id: str = "teaching-observer",
                             ledger: MutableMapping[str, dict[str, Any]],
                             ) -> dict[str, Any]:
    """维护负责人只批准本地工单；重复审批不增设工单。"""
    key = _ledger_key("production", observer_id, event_id)
    if key not in ledger:
        return {"route": "missing_proposal", "state": "clarify",
                "reason": "请先生成可复核的异常事件。", "new_ticket_count": 0,
                "control_commands": []}
    record = ledger[key]
    if not _record_valid(record, "production", observer_id, event_id):
        return _event_conflict("异常提案版本或请求指纹不一致，不能审批。")
    if record["request"].get("thresholds") != [TEACHING_VIBRATION_LIMIT,
                                                TEACHING_TEMPERATURE_LIMIT,
                                                TEACHING_SENSOR_AGE_LIMIT]:
        return _event_conflict("教学阈值版本已变化，请重新生成并审核异常提案。")
    saved = deepcopy(record["result"])
    if saved.get("state") not in ("proposed", "ticketed_local") or \
            approval_by != "maintenance_lead":
        return {"route": "approval_denied", "state": "restricted", "risk_score": None,
                "ticket_id": None, "new_ticket_count": 0, "control_commands": [],
                "approval_error": "只有维护负责人可审核异常草稿；设备状态不会改变。",
                "reason": "未通过审批角色或提案状态核验，不能回放已批准工单。"}
    if saved.get("state") == "ticketed_local":
        saved.update(replayed=True, new_ticket_count=0)
        return saved
    saved.update(state="ticketed_local", ticket_id=f"T-{event_id}",
                 new_ticket_count=1, approval_by=approval_by,
                 next_actor="维护与质量负责人",
                 reason="维护负责人已在本地演示中批准调查工单。")
    record["result"] = deepcopy(saved)
    record["result_fingerprint"] = _fingerprint(saved)
    return saved
