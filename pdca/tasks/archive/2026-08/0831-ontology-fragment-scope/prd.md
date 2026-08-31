# 扩展 ontology_fragment 强制范围至 research/design/review

## 背景
T0456 审查结论指出仅 `development/bugfix` 强制 `ontology_fragment`，其余 4 路径为顾问式，致本体在非开发工作中为可选。需将门禁扩至 `research/design/review`，使本体成为所有工作的默认基础，仅显式 `ontology_exempt` 可豁免。

## 问题
- `ontology_reason.py:32` `FALLBACK_ADMISSION` 仅含 `do: [ontology-ready]`
- `ontology_gate.ontology_ready_issues` 仅在 `admission_conditions` 含 `ontology-ready` 时校验，`research/design/review` 在 `do` 阶段不触发
- `task.json` 中 `ontology_fragment` 为空时无提示，导致知识沉淀易遗漏

## 方案
- 改 `ontology_reason.FALLBACK_ADMISSION` 或本体节点 `pdca-gate-do/research/design/review` 的 `relates_to`，使 `admission_conditions` 在四类路径的 `do` 均含 `ontology-ready`
- 改 `ontology_gate.ontology_ready_issues`：当 `scenario_type ∈ {research,design,review}` 且 `phase==do` 时，若 `ontology_fragment` 缺空且非 `ontology_exempt`，返回 `ONTOLOGY_FRAGMENT_MISSING`（阻塞）；若为 `ontology_exempt` 则要求 `meta` 含豁免原因（可选，顾问式）
- 保持 `documentation` 可选（纯文档不强制），或同样纳入（可选，二选一，Grill 定）
- 同步 `pdca_context.py` 的 fallback 提示

## 验收标准
- [ ] research/design/review 在 do 阶段缺 fragment 时被 `ontology_ready_issues` 阻塞
- [ ] ontology_exempt=true 时不阻塞（需显式声明）
- [ ] ontology-validate 通过
- [ ] ontology_graph islands 0
- [ ] 新增测试覆盖 4 路径门禁分支

## 关联本体节点
```
ontology:concept/pdca-gate-do
ontology:concept/pdca-ontology-ready
ontology:concept/pdca-task
```

## 风险
- 存量 research 任务若未声明 fragment 会被阻塞；需提供批量豁免迁移脚本或短期兼容开关

## 非目标
- 不改 Check/Act 门禁；仅 Do 准入
