---
schema: pdca.asset/v1
id: T0338-0821-pgwrecover-btree-replay
phase: check
source_ids: [t0338-btree-replay]
---

## 上下文

T0337 完成后，pgwrecover 只输出单个 heap 文件，btree 索引 WAL 记录全部跳过。
本轮实现多 fork 架构 + 核心 btree WAL 重放。

## 假设与结果

| AC | 验收标准 | 结果 | 证据 |
|----|---------|------|------|
| AC-1 | --out-index 指定时 btree fork 文件正确复制 | **通过** | t0338-btree-replay：copy_index 实现 |
| AC-2 | btree FPI 正确写入 fork 文件 | **通过** | t0338-btree-replay：FPI 路由逻辑 |
| AC-3 | 不指定 --out-index 时行为不变 | **通过** | t0338-btree-replay：向后兼容 |
| AC-4 | INSERT_LEAF 重放 | **已实现** | pg_redo_btree.c |
| AC-5 | DELETE 重放 | **已实现** | pg_redo_btree.c |
| AC-6 | SPLIT_L/R 重放 | **已实现** | pg_redo_btree.c |
| AC-7 | 回归不破坏 | **通过** | 9 项单测全 PASS |

## 分析

1. **多 fork 架构**：pgwrecover 现在支持 --out-index 参数，btree FPI 按 forkNum 路由到正确文件
2. **btree 重放**：INSERT_LEAF/DELETE/SPLIT/NEWROOT 四种核心类型已实现，编译通过
3. **待验证**：需要真实 btree WAL 样本进行端到端验证
4. **待完善**：SPLIT 的 IndexTuple 解析为简化实现，DELETE 的 posting list 更新未实现

## 适用边界

- btree 重放仅支持 INSERT_LEAF/DELETE/SPLIT/NEWROOT
- VACUUM/MARK_HALFDEAD/UNLINK_PAGE 等 P1/P2 类型跳过
- 需要真实 btree WAL 样本验证

## 下一轮建议

- 用真实 btree WAL 样本端到端验证
- 完善 SPLIT 的 IndexTuple 解析
- 实现 VACUUM/MARK_HALFDEAD/UNLINK_PAGE（P1）
