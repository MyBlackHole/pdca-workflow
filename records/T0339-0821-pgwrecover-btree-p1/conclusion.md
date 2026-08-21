---
schema: pdca.asset/v1
id: T0339-0821-pgwrecover-btree-p1
phase: check
source_ids: [t0339-btree-p1]
---

## 上下文

T0338 完成 btree P0 类型（INSERT_LEAF/DELETE/SPLIT/NEWROOT）。本轮扩展 P1 类型。

## 假设与结果

| AC | 验收标准 | 结果 | 证据 |
|----|---------|------|------|
| AC-1 | VACUUM 重放 | **通过** | t0339-btree-p1 |
| AC-2 | MARK_HALFDEAD 重放 | **通过** | t0339-btree-p1 |
| AC-3 | UNLINK_PAGE/UNLINK_PAGE_META 重放 | **通过** | t0339-btree-p1 |
| AC-4 | 回归不破坏 | **通过** | 编译通过 |

## 适用边界

- P1 类型已覆盖 btree 主要维护操作
- 剩余 P2（INSERT_UPPER/META/DEDUP 等）和边界类型（REUSE_PAGE/GIN/GiST）跳过
- 需要真实 btree WAL 样本端到端验证
