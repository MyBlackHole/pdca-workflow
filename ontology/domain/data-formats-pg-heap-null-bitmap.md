---
schema: pdca.asset/v1
id: ontology:domain/data-formats-pg-heap-null-bitmap
type: domain
layer: Knowledge
status: active
summary: PG heap null bitmap 物理布局（含读写约定）
domain:
- ontology:domain/data-formats
relations:
  specializes:
  - ontology:domain/data-formats
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# PG heap null bitmap 物理布局（含读写约定）

> 来源：T0311 POC（0818-pg-consistency-poc）。由 POC 合成宽表（含 NULL）实测 + PG18
> 源码（third_party/pg184）确认。T0301 的 poc_orders 全 NOT NULL 曾掩盖此事实。

## 布局

- `HeapTupleHeaderData` 定长头 = 24 B（含 t_hoff@22 1B）；null bitmap（`t_bits`）起点 =
  `offsetof(HeapTupleHeaderData, t_bits)` = **23**（xmin4 + xmax4 + t_field3 4 + ctid6
  + infomask2 2 + infomask 2 + t_hoff 1）。
  - 坑：PG_HEAP_HEADER_SIZE 常被误写为 24（那是 t_hoff 对齐后的数据区起点）。t_bits
    在 23，数据区在 t_hoff（本表 24）。偏移 1 字节会把数据区首字节当 bitmap。
- null bitmap 仅在 infomask 置 `HEAP_HASNULL=0x0001` 时存在（否则 0 字节）。
- 数据区从 `t_hoff` 起，**已含 bitmap 空间**，无需额外对齐。

## 位约定（关键）

- **bit=1 非空 / bit=0 NULL**（与直觉相反）。`att_isnull` = `!(BITS[ATT>>3] &
  (1 << (ATT & 7)))`，1 表示非空。
- **位序 LSB-first**：第 1 列（attnum 1）→ bit0。来源 `heap_fill_tuple`：
  `bitP = &bit[-1]; bitmask = HIGHBIT;` 且 `fill_val` 在 `bitmask != HIGHBIT` 时
  `*bitmask <<= 1`，即首列用 bitmask=1。
- 每行解码：`nullbit = hasnull ? ((bits[a>>3] >> (a&7)) & 1) : 1`——**hasnull=0 时
  全列非空**（nullbit 恒 1）。
- NULL 列不占数据区空间、不推进 offset；非 NULL 列按 attalign 对齐后读取。

## 与 pageinspect 的显示差异（坑）

pageinspect `heap_page_items` 的 `t_bits` 输出是 **bit 反转**（如 heap 字节 0x6F 显示
0xF6）。以 heap 文件字节为准，勿用 pageinspect 输出直接解位。

## 校验/复用

- 含 NULL 数据的转换校验必须覆盖：NULL 三形态（整列/稀疏/部分）、bit 位与列对应、
  validity buffer（parquet 侧）非空。
- 修复参考：`src/pg/pg_heap_reader.c` decode_tuple（判定反转 + 偏移 23 + 哨兵/null
  位图）、`src/pg/pgbin.cpp` validity_buf（由 nulls 位图建 arrow validity）。
