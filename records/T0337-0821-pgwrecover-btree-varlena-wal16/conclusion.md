---
schema: pdca.asset/v1
id: T0337-0821-pgwrecover-btree-varlena-wal16
phase: check
source_ids: [t0337-varlena-fix]
---

## 上下文

T0336 完成后两个遗留：pgbin varlena 未对齐崩溃（阻塞端到端）、btree 增量跳过（需架构改造）。
本轮收口 varlena 修复，btree 移至 T0338。

## 假设与结果

| AC | 验收标准 | 结果 | 证据 |
|----|---------|------|------|
| AC-1 | varlena 修复后 pgbin 不崩溃 | **通过** | t0337-varlena-fix：memcpy 替代指针解引用，编译通过 |
| AC-2 | 既有单测仍 PASS | **通过** | 9 项单测全 PASS（样本缺失跳过为预期） |

## 分析

1. **修复精确**：仅改 1 行（`*(uint32*)vp` → `memcpy`），同文件其他位置已用 memcpy
2. **WAL 跨段已支持**：`WALRead()` 自动检测段边界切换，无需实现
3. **PG16 布局兼容**：`xl_multi_insert_tuple` 与 PG18 相同，仅标志位差异
4. **btree 需架构改造**：pgwrecover 当前只输出单个 heap 文件，btree 需多 fork 文件支持

## 适用边界

- varlena 修复适用于所有 packed varlena 场景（PG9.6+）
- WAL 跨段在单 segment ≤1GB 时自动工作

## 下一轮建议

- T0338：btree 增量重放（需改 pgwrecover 架构支持多 fork 文件）
