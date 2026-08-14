# 独立效率损失参照集

本参照集先从非 `flow-events` 的真实任务产物提取问题，再检查 occurrence 是否捕获。它用于验证发现能力，不声称是全部真实任务问题的统计抽样。

| ID | 独立真实问题 | 非 flow-event 证据 | occurrence 匹配 | 判定 |
|---|---|---|---|---|
| IR-1 | 串行 Grill 增加用户交互轮次；frontier 批量后真实会话从逐题 11 轮降为 8 轮，后续 flow-act 案例从 3 轮降为 1 轮。 | `records/T0230-0809-ai-efficiency-proof/conclusion.md`；`records/T0231-0809-followup-frontier-batch-spread/conclusion.md` | T0230、T0231 均无 occurrence。 | false negative；满足两个真实任务的候选门槛。 |
| IR-2 | 设计词汇检查错误作用于 PRD，且手写 plan 时间戳与 transition 时间粒度冲突，造成真实流程摩擦。 | `pdca/tasks/archive/2026-08/0809-mechanism-fixes/triager-brief.md`；`records/T0238-0809-mechanism-fixes/conclusion.md`；`records/T0239-0809-transition-timestamps/conclusion.md` | T0234、T0238 无 occurrence；T0239 的 17 条事件只记录证据/收敛门禁中间失败，没有记录源问题。 | false negative；后续人工创建 T0238/T0239 才完成修复。 |
| IR-3 | seam 契约脚本没有自动消费者，需要接入 doctor；外部/归档 seam 的路径生命周期还会影响信号边界。 | `pdca/tasks/archive/2026-08/0809-seam-ci-gate/triager-brief.md`；`records/T0240-0809-seam-ci-gate/conclusion.md`；`records/T0241-0809-seam-doctor-gate/conclusion.md` | T0240、T0241 无 occurrence。 | false negative；问题由人工审查和后续任务发现。 |
| IR-4 | T0164 的 plan→do 早于 final confirmation，且 convergence 使用占位符，属于真实流程完整性和 AI 可用性问题。 | `pdca/tasks/archive/2026-07/T0166-0731-flow-integrity-hardening/triager-brief.md`；`records/T0166-0731-flow-integrity-hardening/conclusion.md` | `FE-32f57909a670228e0bffc027`、`FE-c059fe399df2979772ce9b83`；随后 T0166 实施并验证修复。 | true positive；证明记录机制至少一次产生了真实行动价值。 |
| IR-5 | 任务 ID 在多个不同 slug 间重复，且 5 个事件目录与内部 record_id 不一致，使全量 backlog 重建 fail-closed。 | 全仓库 `task.json` ID/slug 枚举得到 23 个冲突 ID；隔离重建返回 `EVENT_PATH_MISMATCH`。 | 没有 occurrence 报告 `TASK_ID_COLLISION` 或 `EVENT_PATH_MISMATCH`；问题在消费记录时才暴露。 | false negative / 记录完整性阻断；满足重复性和严重阻断门槛。 |

## 交叉匹配结论

- 在这 5 个有独立证据的参照项中，1 项被 occurrence 正确捕获并产生后续修复，4 项未被记录方式直接发现。
- `1/5` 仅描述本参照集，不外推为全仓库统计召回率。
- T0239 的 17 条 occurrence 不算 IR-2 命中：它们的 issue code 是 `ACCEPTANCE_CRITERION_UNCOVERED`、`CONVERGENCE_MAP_MISSING`、`CONVERGENCE_SUPPORT_MISSING`，与被修复的时间戳摩擦不是同一问题。
- 参照集证明记录方式具有局部发现价值，但覆盖面集中于 transition conformance，尚不能持续发现更广泛的 AI 使用效率损失。
