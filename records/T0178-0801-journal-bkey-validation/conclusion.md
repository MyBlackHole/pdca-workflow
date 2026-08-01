---
schema: pdca.asset/v1
id: T0178-0801-journal-bkey-validation
phase: check
source_ids: [source-alignment, test-results, review-report, convergence-map]
---

## 上下文

T0178 加固 journal 恢复入口：对 `BCH_JSET_ENTRY_btree_keys` 在构建 overlay
和 replay 前逐键处理布局损坏。初始“完整 fs 层语义校验”方案已在 Plan 阶段
收窄，因为 subvol 的独立 btree-id/key 语义不能安全复用 bcachefs extents
树的 type/size/snapshot 规则。

## 假设与结果

假设：按 bcachefs `journal_validate_key()` 的 btree-id 无关布局分支，在
恢复前截断或紧缩坏 key，能阻止其进入 overlay/replay，同时保留合法邻键。

结果：通过。

- 零 u64s、短于 bkey 头和超出 entry 尾部的 key 均截断 entry；
- 非当前 format 的 key 被删除并紧缩，同行当前 format 键仍正常进入 overlay；
- `cargo test --workspace --no-fail-fast`：178 个单测与 10 个属性/集成测试
  通过；fmt 与 diff 检查通过。

## 分析

实现复制本地 `fs/journal/validate.c:64-91` 的顺序：先处理零 u64s，再处理
越界，再处理非当前 format。`journal_entry_null_range()` 保持空 entry 填充，
因此恢复后续扫描沿用当前 jset 遍历规则。

Rust 在读取 bkey header 前增加最小 `BKEY_U64S` 剩余空间检查；这是固定大小的
C journal 缓冲区与精确长度 Rust Vec 的内存表示差异所要求的等价边界保护。

## 适用边界

本结论仅覆盖 key 布局校验。不覆盖 bcachefs fs 层的 key type、size、position
或 snapshot 语义；直接移植这些规则会错误拒绝 subvol 现有的默认 cookie key。
后续若引擎定义独立且可验证的 key-type 合约，应另立 PDCA 周期。

## 下一轮建议

保持 T0178 范围闭环。下一项优先评估 transaction/gc trigger 链，前提是先以
本地 bcachefs `commit.c` 证明其是否适用于当前独立 key 类型集合。
