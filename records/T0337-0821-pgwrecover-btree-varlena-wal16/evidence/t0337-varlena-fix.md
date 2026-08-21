# T0337 varlena 未对齐读取崩溃修复

> 来源：T0337-0821-pgwrecover-btree-varlena-wal16
> 范围：S1 varlena 崩溃修复（S2 btree 移至 T0338）

## 修复内容

`src/pg/pg_heap_reader.c:219`，`varlena_size_any()` 函数：

```c
// 修复前（崩溃点）：
return ((*(const uint32 *) vp) >> 2) & 0x3FFFFFFF;

// 修复后：
uint32 header;
memcpy(&header, vp, sizeof(uint32));
return (header >> 2) & 0x3FFFFFFF;
```

## 根因

packed varlena 编码允许 1B 头（bit0=1）在任意偏移地址，但 4B 头（bit0=0）需要
4 字节对齐。当数据区偏移导致 `vp` 未对齐时，`*(uint32*)vp` 触发：
- ARM: SIGBUS（硬件对齐检查）
- x86: C 未定义行为（UBSan 报违规）

同文件第 99/120/443/619 行已正确使用 `memcpy`，第 219 行遗漏。

## 验证

- 编译通过（bash scripts/build_pgwrecover.sh）
- 9 项既有单测全 PASS（样本缺失时跳过是预期行为）
- 无新回归

## WAL 跨段 & PG16 调研结论（无需实现）

- WAL 跨段：`WALRead()` 已自动检测段边界并切换段文件
- PG16 `xl_multi_insert_tuple`：布局与 PG18 完全相同，仅标志位差异

## btree 增量重放（移至 T0338）

调研完成（15 种 WAL 类型、BTPageOpaque/IndexTuple 结构、多块协调需求）。
因 pgwrecover 当前只输出单个 heap 文件，btree 需要支持多 fork 文件架构，
复杂度独立，已规划新任务 T0338。
