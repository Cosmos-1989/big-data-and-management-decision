/** Deterministic teaching simulations; no model or external business calls. */
export const agentExperiments=[
  {
    "id": "agent-rag",
    "title": "企业制度可信问答",
    "chapter": "14_ai_agent",
    "description": "按关键词、日期、角色和制度版本给出可追溯答复；缺证据时拒答或转人工。",
    "language": "python",
    "code": "# 固定关键词和制度版本过滤，模拟可信问答；此处没有语言模型。\nfrom bdm_decision.cases.week14_enterprise_agents import answer_policy, policy_threshold_rows\n\namount_yuan = 450\nemployee_access = True\n# 访客角色不得看到员工制度正文；金额滑块可触发不同审批分支。\nrole = 'employee' if employee_access else 'guest'\nresult = answer_policy('国内住宿报销额度', role=role, as_of='2026-10-10',\n                       region='domestic', amount_yuan=amount_yuan)\ndisplay([{'判定': result['decision'], '状态': result['state'],\n          '证据': '、'.join(result['evidence_ids']) or '无',\n          '理由': result['reason'], '下一处理人': result['next_actor']}], '制度问答与来源')\n# 仅在已授权时展示教学制度额度，不向访客泄露员工文件。\nif employee_access:\n    display(policy_threshold_rows(), '版本与额度（教学数据）', x='版本', y='自动额度')\n",
    "params": [
      {
        "name": "amount_yuan",
        "label": "每晚住宿金额 / 元",
        "min": 0,
        "max": 750,
        "step": 25,
        "value": 450
      },
      {
        "name": "employee_access",
        "label": "具有员工制度访问权限",
        "type": "bool",
        "value": true
      }
    ],
    "sourcePath": "src/bdm_decision/cases/week14_enterprise_agents.py"
  },
  {
    "id": "agent-office",
    "title": "办公数字员工与研发助手",
    "chapter": "14_ai_agent",
    "description": "计算共同会议空档，并仅引用角色可见的已批准最新版研发资料。",
    "language": "python",
    "code": "# 用固定日历求交集，用已批准资料的权限与版本筛选回答。\nfrom bdm_decision.cases.week14_enterprise_agents import (\n    office_assist, approve_meeting, research_answer\n)\n\napprove = False\nengineer_access = False\nledger = {}  # 内存账本只服务本次浏览器运行，不发送真实会议邀请。\nmeeting = office_assist('meeting', event_id='MEET-1', participants=['李', '王'], ledger=ledger)\n# 组织者审批是独立状态转移；未审批时始终只是提案。\nif approve:\n    meeting = approve_meeting('MEET-1', approval_id='ORG-1',\n                              organizer_authenticated=True, ledger=ledger)\nrole = 'engineer' if engineer_access else 'employee'\nresearch = research_answer('芯片接口', role=role)\npublic_note = research_answer('泵振动', role='employee')\ndisplay([{'任务': '会议排期', '判定': meeting['decision'],\n          '结果': meeting.get('proposal_time', '无共同空档'), '状态': meeting['state']},\n         {'任务': '受限研发资料', '判定': research['decision'],\n          '结果': research.get('answer_fact') or '不显示正文', '状态': research['state']},\n         {'任务': '公开研发资料', '判定': public_note['decision'],\n          '结果': public_note.get('answer_fact'), '状态': public_note['state']}],\n        '办公与研发助手')\n",
    "params": [
      {
        "name": "approve",
        "label": "组织者批准会议提案",
        "type": "bool",
        "value": false
      },
      {
        "name": "engineer_access",
        "label": "具有研发工程师权限",
        "type": "bool",
        "value": false
      }
    ],
    "sourcePath": "src/bdm_decision/cases/week14_enterprise_agents.py"
  },
  {
    "id": "agent-routing",
    "title": "客户咨询分流工作流",
    "chapter": "14_ai_agent",
    "description": "按安全、退货、订单、产品优先级分流；身份和订单归属检查先于展示状态。",
    "language": "python",
    "code": "# 固定词典和优先级实现客服分流；不会退款或查询真实订单。\nfrom bdm_decision.cases.week14_enterprise_agents import route_customer\n\nverified = False\nsafety_message = False\nmessage = '设备冒烟，O100 物流怎样？' if safety_message else 'O100 物流怎样？'\nledger = {}  # 完整账本保存请求指纹；首次调用和重试都使用它。\nresult = route_customer('CASE-1', customer_id='U1', verified=verified,\n                        message=message, order_id='O100', ledger=ledger)\ndisplay([{'消息': message, '路由': result['route'], '状态': result['state'],\n          '可显示事实': result.get('visible_fact') or '无',\n          '下一处理人': result['next_actor'],\n          '命中意图': '、'.join(result['matched_keywords']) or '无'}], '客户咨询分流')\n# 同一事件号再次提交只复用结果，不新增客服动作。\nreplay = route_customer('CASE-1', customer_id='U1', verified=verified,\n                        message=message, order_id='O100', ledger=ledger)\nprint('重复提交复用前次结果：', replay.get('replayed', False))\n",
    "params": [
      {
        "name": "verified",
        "label": "客户身份已核验",
        "type": "bool",
        "value": false
      },
      {
        "name": "safety_message",
        "label": "消息包含设备冒烟",
        "type": "bool",
        "value": false
      }
    ],
    "sourcePath": "src/bdm_decision/cases/week14_enterprise_agents.py"
  },
  {
    "id": "agent-production",
    "title": "生产线异常处理综合方案",
    "chapter": "14_ai_agent",
    "description": "以只读传感器和 PLC 联锁状态生成调查建议；审批后仅建立本地模拟工单。",
    "language": "python",
    "code": "# 只读教学事件：PLC 联锁状态只能输入，代码没有任何停启机调用。\nfrom bdm_decision.cases.week14_enterprise_agents import (\n    handle_production_event, approve_production_event\n)\n\nvibration_mm_s = 8.0\nstale_reading = False\ninterlock_trip = False\napprove_ticket = False\nledger = {}  # 本地账本用于工单审批和事件去重。\nresult = handle_production_event('E-DEMO', vibration_mm_s=vibration_mm_s,\n                                 temperature_c=79.0, quality_flag='good',\n                                 sensor_age_s=61 if stale_reading else 20,\n                                 interlock_trip=interlock_trip, ledger=ledger)\n# 只有有效异常草稿可被维护负责人批准；仍然不触及设备。\nif approve_ticket and result['state'] == 'proposed':\n    result = approve_production_event('E-DEMO', approval_by='maintenance_lead',\n                                      ledger=ledger)\ndisplay([{'事件': 'E-DEMO', '路由': result['route'], '状态': result['state'],\n          '风险分数': result['risk_score'],\n          '命中信号': '、'.join(result['matched_signals']) or '无',\n          '本地工单': result.get('ticket_id') or '未建立',\n          '设备控制调用数': len(result['control_commands'])}], '产线异常复核')\nprint(result['reason'])\n",
    "params": [
      {
        "name": "vibration_mm_s",
        "label": "振动值 / mm·s⁻¹",
        "min": 0,
        "max": 12,
        "step": 0.5,
        "value": 8
      },
      {
        "name": "stale_reading",
        "label": "传感器读数已过期",
        "type": "bool",
        "value": false
      },
      {
        "name": "interlock_trip",
        "label": "PLC 已上报安全联锁",
        "type": "bool",
        "value": false
      },
      {
        "name": "approve_ticket",
        "label": "维护负责人批准模拟工单",
        "type": "bool",
        "value": false
      }
    ],
    "sourcePath": "src/bdm_decision/cases/week14_enterprise_agents.py"
  }
];
