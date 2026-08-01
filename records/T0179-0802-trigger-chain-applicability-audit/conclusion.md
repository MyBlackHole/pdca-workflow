---
schema: pdca.asset/v1
id: T0179-0802-trigger-chain-applicability-audit
phase: check
source_ids: [trigger-applicability-report, trigger-scope-correction, verification-result]
---

## 上下文

T0168 D3 指出 subvol 未运行 bcachefs 式 transactional/GC trigger runner。T0179
验证该静态差异是否对当前独立键模型构成实际事务一致性缺口。

## 假设与结果

假设：只要 Rust 缺少 transactional/GC runner，就必须移植 bcachefs 完整 trigger
链；同时，当前可达的审计范围仅有 cookie/deleted/snapshot。

结果：**部分成立**。前半结论成立：当前公开 cookie/deleted API 不需要 trigger，
snapshot atomic trigger 已在 commit 路径执行，GC runner 不能脱离 `gc_visited()`
扫描状态移植。后半结论不成立：审计范围遗漏了 extent/range key、alloc、内部
btree pointer 与其派生的 backpointer/stripe-backpointer/accounting 更新。

## 分析

`trigger-applicability-report` 仅证明 cookie/deleted/snapshot 三条路径的判定，不能
推广到完整 btree core。`trigger-scope-correction` 证明：bcachefs 把
`BKEY_TYPE_btree` 纳入 transactional trigger；btree pointer 与 extent 绑定
`bch2_trigger_extent()`，该 trigger 同事务派生 alloc、backpointer 与 accounting
更新。subvol 已有 range iterator/update 分派和 btree pointer 格式，但没有这些
trigger runner/派生维护链。因此不能得出“无适用缺口”。

`verification-result` 记录 snapshot 原子 marker 单测、普通事务模型恢复单测、完整
workspace 测试和格式检查均通过。产品仓库无代码差异。

## 失败原因（仅 rejected/partial）

原假设将“当前公开 API 未使用”错误外推为“存储引擎 core 无适用路径”，遗漏了
已有的 extent/btree-pointer 内部结构和项目目标中的空间分配语义。

## 适用边界

可复用的部分仅限当前公开 put/delete 和 snapshot atomic 路径。完整 core 的
extent、alloc、btree pointer、backpointer、stripe-backpointer、accounting 与 GC
依赖图尚未审计；不得以本任务结论跳过它们。

## 下一轮建议

创建后续 Plan：完整审计 `extent / btree pointer -> alloc -> backpointer /
stripe-backpointer -> accounting / reconcile -> journal / recovery / GC`。在证明所有
派生路径和最小可实现边界前，不实现 trigger runner。
