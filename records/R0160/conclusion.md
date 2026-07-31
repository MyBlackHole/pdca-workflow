---
schema: pdca.asset/v1
id: R0160
phase: check
source_ids: [route-lifecycle-fixtures, content-budget, full-unittest, environment-health, implementation-review, convergence-map, convergence-validation]
---

## 上下文

T0159 后的复核发现原 AI 友好度评测存在标题自证、模拟断链、后半生命周期门禁未覆盖和内容 bytes 无预算四个缺口。T0160 的目标是把这些确定性评测缺口转化为可执行、可证伪的合约，而不是评估真实 LLM 能力。

## 假设与结果

假设：严格 route contract、真实断链和公共 phase transition fixture、逐资产 bytes baseline 能提高 AI 导航与评测 oracle 的可信度，且不引入模型或网络依赖。

结果：**confirmed**。公共 resolver 覆盖六个 scenario；16 个 route/reference/lifecycle fixture 全部通过；生命周期成功链由四次公开相邻转换及 receipts 证明；41 个 flow/skill 资产均受 baseline 约束，预算、引用和 fixture 非退化检查均通过。

## 分析

- AC-1 至 AC-5：schema、resolver、文档锚点校验、A/B 映射交换反例和真实文件删除共同排除“仅标题存在即通过”的旧 oracle。
- AC-6 至 AC-11：成功 fixture 只调用 `transition-phase.py`；Plan 的确认、Do 的 PRD/evidence/convergence、Check 的 conclusion/verdict/确认及 Act 的 disposition 各有真实拒绝反例。
- AC-12 至 AC-14：版本化 baseline 严格覆盖 41 项资产；遗漏、陈旧项、超预算、断链和 fixture 回归均 fail-closed，显式带理由更新后才可恢复预算通过。
- AC-15：fixture 输出把 UTF-8 bytes 明确标注为可重复内容代理，不报告或暗示真实 LLM 成功率、延迟或跨模型比较。
- AC-16：全量 `unittest` 60 项通过，fixture 16/16，内容预算无 issue，doctor 与技能索引校验通过；未增加网络、模型或外部 runtime 依赖。

## 失败原因（仅 rejected/partial）

不适用。本结论不对真实模型表现作推断，因此不存在以确定性测试替代模型失败分析的情况。

## 适用边界

本结论只适用于本仓库的确定性协议、导航、故障恢复、生命周期门禁和内容成本代理。真实模型表现仍需固定 runner、冻结工具接口、保留任务集以及成功、恢复和成本指标的独立任务评测。

## 下一轮建议

维持每次 flow/skill 变更后的 `audit-skill-content.py --check-budget` 与 fixture 执行。只有具备上述实验条件时，另建任务评估真实 Agent/LLM 成功率，避免把本任务的通过率外推为模型能力。
