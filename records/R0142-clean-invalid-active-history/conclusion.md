---
schema: pdca.asset/v1
id: R0142-clean-invalid-active-history
phase: check
source_ids: [deletion-manifest, deletion-result-final, protected-comparison, validation-result, test-result, recovery-plan, review-report-final, convergence-map]
---

## 上下文

检查是否以可恢复、不可越界的方式删除 16 个旧格式活跃任务，并恢复
`validate-workflow --all` 作为可信全库健康信号。

## 假设与结果

- active dry-run 能精确选择旧格式无效任务：通过。目标集合与清理前 16 个无效活跃任务完全一致。
- 删除可以安全恢复：通过。16/16 目标、49/49 文件由 Git 跟踪；固定预删除 commit `4582c0c9e6e43f3184b322239a27f5010a066649` 仍包含全部 49 个文件。
- 破坏性门禁能失败关闭：通过。错误确认数量、digest 漂移、不可恢复目标、有效任务、越界路径、archive、保护目录和通配符均有拒绝测试。
- 删除没有越界：通过。实际 Git 删除 49 个文件，全部属于 manifest 目标；范围外删除为 0。
- 保护资产不变：通过。records、knowledge、journal、archive 和当前任务在删除动作前后的文件数与目录摘要完全一致。
- 全库信号恢复：通过。从 23 个任务、16 个无效变为 8 个任务、0 个无效；清理后 active dry-run 目标为 0。
- 无回归：通过。38/38 单元测试、12/12 确定性夹具、doctor、skill index、archive dry-run 和 convergence gate 均通过。

## 分析

本次改动符合 AI 价值门槛：清理前全库检查固定失败，AI 无法用它区分新错误；清理后同一命令返回 `valid: true`、`invalid_count=0`，以后任何失败都重新成为可行动信号。

代码审查在删除前发现并修复三个安全问题：apply 需再次拒绝有效任务、active dry-run 显式排除 archive 根、恢复命令必须固定预删除 commit 而不能使用会漂移的 HEAD。最终双轴 Blocking 为 0。

被删除目录不会保留旧格式兼容或迁移副本；其 records、knowledge 和 journal 等受保护资产未删除。需要恢复时，使用 recovery plan 中固定 commit 和 manifest 路径。

## 适用边界

- 本次证明的是确定性校验信号恢复，不是实际 LLM 成功率提升。
- active scope 只处理 `pdca/tasks/` 的无效直接子目录，不处理任意目录清理。
- dry-run 依赖已有 Git commit 来生成稳定 recovery source；未初始化或无 commit 的仓库会失败关闭。
- 恢复旧目录会重新引入严格 schema 错误，恢复仅用于取回历史内容，不表示可继续执行。

## 下一轮建议

保留 active audit scope，因为它已有真实消费者并具备严格路径、digest、数量和恢复门禁。下一项优化应单独评估 research 来源链 validator；不得与本次删除恢复逻辑耦合。
