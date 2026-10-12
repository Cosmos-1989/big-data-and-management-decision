# 企业AI Agent教学方案包

包含专题讲义、四个可复算的企业案例、完整注释Python模块、标准测试、四份Skill任务配方、中立工作流契约和部署验收表。资料与程序均使用虚构教学数据，不调用真实LLM或外部企业服务。

在本包解压目录或课程仓库中运行：`PYTHONPATH=src python3 tests/test_enterprise_agent_teaching.py`。完整模块位于`src/bdm_decision/cases/week14_enterprise_agents.py`；将`src`加入Python模块搜索路径后，可用`from bdm_decision.cases.week14_enterprise_agents import answer_policy`等语句调用相应案例函数。网页实验可编辑和运行四种案例，网站另提供单文件程序下载。

工作流JSON描述任务契约，不能直接导入Dify或Coze；需要按目标平台的节点、变量、鉴权和业务服务进行适配。Skill文件本身不授予执行权限。真实试点评测应接入获准的模型和企业环境，独立记录任务质量、违规、人工时间与成本。
