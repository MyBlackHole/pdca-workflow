---
schema: pdca.asset/v1
id: T0158
phase: check
source_ids: [stale-archive, audit-implementation, audit-tests, runtime-audit, verification, code-review, convergence-map]
---

## 上下文

T0150 执行中暴露了遗留子任务、阶段步骤跳过、时间与 AC 格式不一致、证据条目丢失等流程偏差。T0158 的原 PRD 要求清理 T0151–T0157，并在四个阶段转换点自动检测和记录问题。

Check Grill 中，用户进一步明确本质目标不是止于记录，而是依据问题记录持续优化 PDCA，形成自我优化循环。

## 假设与结果

- **原 PRD 假设**：转换级非阻断审计可建立稳定的问题观测层。结果成立；AC-1 至 AC-6 均有非 map 证据覆盖，收敛验证通过。
- **本质目标假设**：问题记录能力本身即可构成 PDCA 自我优化。结果不成立；当前实现只有观测层，没有记录聚合、根因与频次分析、改进候选、确认后实施和下一周期效果验证。
- **判定**：`partial`。已完成部分可保留并作为下一循环输入，但任务尚未实现完整自我优化闭环。

## 分析

T0151–T0157 已移出 active，以 `task.invalid.json` 和归档说明保留真实遗留状态，没有伪造用户确认、证据、结论或 disposition。T0150 的正式 archive 任务通过严格校验。

`transition-phase.py` 已在 Plan→Do、Do→Check、Check→Act、Act→Archive 前调用非阻断审计。审计文件包含每次尝试的 `passed`、checks、issues 和历史记录；T0158 自身捕获了缺 record、缺 evidence manifest 等失败，登记证据后最新 Do→Check 审计转为 pass。40 项自动化测试全部通过，代码审查 Blocking 为 0。

这些能力能够回答“流程哪里出了问题”，但尚不能回答“哪些问题反复出现、优先改什么、改动是否有效”。因此它是自我优化循环的输入层，而不是完整循环。

## 失败原因（仅 rejected/partial）

原 PRD 将范围限定为问题检测和记录，没有把审计记录的聚合消费、改进决策及效果验证写入验收标准。Check 阶段用户澄清了更高层目标，暴露出规格与真实意图之间的缺口。

## 适用边界

- 同一任务并发执行多个转换时，审计尝试可能发生最后写入覆盖；现有转换器不支持该并发模式，本轮不增加锁。
- 审计器自身发生 I/O 或格式错误时输出 stderr 告警，但不新增转换阻断；原有 gate 仍是唯一转换判定。
- T0151–T0157 是无效历史快照，不是完成过独立 PDCA 的正式 archive 任务。
- 自我优化不得自动绕过 Grill、final confirmation、Check verdict 或 Act disposition；改进候选仍需用户确认。

## 下一轮建议

创建后续 PDCA 任务，验收完整反馈链：

1. 聚合多个 `flow-audit.json`，按问题代码、阶段、频次和影响形成问题队列。
2. 对高频或高影响问题形成根因分析与可追溯的改进候选。
3. 改进候选进入正常 Plan Grill 和用户确认，不自动修改权威流程。
4. 实施后在后续周期对比问题发生率，判断改善、无效或退化。
5. 将验证结果重新写入记录，成为下一轮优化输入。
