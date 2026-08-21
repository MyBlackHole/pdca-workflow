# 跟进：pgwrecover btree增量重放 + varlena崩溃修复

> parent: T0336（pgwrecover 增量重放扩展）
> 场景：development
> 调研结论：WAL 跨段已支持（WALRead 自动切换段文件）；PG16 xl_multi_insert_tuple 布局与 PG18 完全相同，仅标志位差异——两项无需实现。

## 问题陈述

T0336 完成后仍有两个阻塞性缺口：
1. **btree 增量跳过**：恢复产物中 btree 索引页可能不一致，若目标升级为"恢复产物可启动 PG"则必须实现
2. **pgbin varlena 崩溃**：`varlena_size_any()` 用 `*(uint32*)vp` 未对齐读取，所有含增量数据的 heap 用 cur_clog 读时崩溃（T0334 遗留），阻塞端到端流程

## S1: pgbin varlena 崩溃修复（必做，阻塞端到端）

### 根因

`src/pg/pg_heap_reader.c:219`，`varlena_size_any()` 函数：

```c
static uint32 varlena_size_any(const uint8_t *vp)
{
    uint8 h = vp[0];
    if (h & 0x01) return h >> 1;              // 1B 短头：安全
    return ((*(const uint32 *) vp) >> 2) & 0x3FFFFFFF;  // ← 崩溃：未对齐 4B 读取
}
```

当 `vp` 不是 4 字节对齐时：ARM 触发 SIGBUS，x86 是 UB（UBSan 报违规）。

同文件其他位置（第 99、120、443、619 行）已正确使用 `memcpy`，此处遗漏。

### 修复

将 `*(const uint32 *) vp` 替换为 `memcpy(&header, vp, sizeof(uint32))`。

### 验收

- AC-1: 构造含非对齐 varlena 的增量 tuple，pgbin 读取不崩溃
- AC-2: 现有 9 项单测仍全 PASS

## S2: btree 增量重放（S3a，可做）

### 范围（按优先级）

**P0（必须，影响查询正确性）：**
- `XLOG_BTREE_INSERT_LEAF`：叶页插入 IndexTuple → `PageAddItem()`
- `XLOG_BTREE_DELETE`：标记 LP_DEAD + posting list 部分更新
- `XLOG_BTREE_SPLIT_L/R`：页分裂（4 块重组：左页保留+右页重建+邻居链修复）
- `XLOG_BTREE_NEWROOT`：创建新根页 + 元页

**P1（影响 VACUUM）：**
- `XLOG_BTREE_VACUUM`：同 DELETE（无冲突处理）
- `XLOG_BTREE_MARK_PAGE_HALFDEAD`：父页删除下链接 + 叶页重建
- `XLOG_BTREE_UNLINK_PAGE`：页面从 btree 链摘除（5 块）

**P2（边界场景）：**
- `INSERT_UPPER` / `INSERT_META`：树增高
- `DEDUP`：叶页去重
- `META_CLEANUP`：元页维护

**跳过：**
- `REUSE_PAGE`：仅 Hot Standby 冲突点，pgwrecover 无需处理

### 关键技术挑战

1. **BTPageOpaque**：btree 页尾部 16 字节（btpo_prev/next/level/flags/cycleid），需新增 btree 页操作原语
2. **IndexTuple 格式**：`t_info` 编码长度，需实现 `IndexTupleSize()` / `BTreeTupleGetDownLink()` 等宏
3. **从 scratch 重建**：btree 重放大量使用 `_bt_pageinit()` + `_bt_restore_page()`（完全重建，非增量修改）
4. **多块协调**：SPLIT 涉及 4 块，UNLINK_PAGE 涉及 5 块

### 验收

- AC-3: INSERT_LEAF + DELETE 重放单元测试 PASS（构造 btree WAL 样本，重放后页内容一致）
- AC-4: SPLIT_L/R 重放单元测试 PASS（叶页分裂后左右页内容正确）
- AC-5: 回归不破坏：T0334+T0336 既有单测仍全 PASS
- AC-6: 端到端：备份+增量 btree 重放后，该索引可用于 PG 启动查询（需容器实证）

## 不做的项（调研结论）

| 项 | 结论 | 原因 |
|----|------|------|
| WAL 跨段 | 已支持 | `WALRead()` 自动检测段边界并切换段文件 |
| PG16 xl_multi_insert_tuple | 布局与 PG18 相同 | 仅标志位差异，无二进制兼容问题 |
