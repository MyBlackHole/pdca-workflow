## 当前状态
T0083 已完成 — PDCA 工作流现在支持 6 种场景类型，每种有独立的 Do→Check 执行路径。

## 未完成事项
- 端到端验收：尚未用 research 或 documentation 场景类型跑一次真实任务

## 已知约束
- scenario_type 由 triage 根据输入形态推断，偶有误判需人工修正
- "review" 场景无代码变更，任务直接归档不用提交
- 旧 task.json 无 scenario_type 字段，默认按 development 处理

## 推荐的下一步
- 创建 research 或 documentation 类型的新任务，端到端验证整条链路

## 关键上下文文件列表
- flows/flow-do/SKILL.md — 场景感知执行路径
- flows/flow-check/SKILL.md — 场景感知验证条件
- skills/triage/SKILL.md — scenario_type 推断逻辑