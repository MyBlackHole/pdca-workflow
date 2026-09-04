---
schema: pdca.asset/v1
id: ontology:domain/data-formats-pg-heap-physical-read-notes
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/data-formats-pg-heap-physical-read-notes/1.0.0
summary: PG heap 文件物理直读工程要点
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
  testable_signal: "运行 grep -q 'PG heap 文件物理直读工程要点' ontology/domain/core/data-formats-pg-heap-physical-read-notes.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# PG heap 文件物理直读工程要点

> 来源：T0163 C++ 官方源码物理路径（复用 PG 18.4 官方 `heap_deform_tuple` + stub backend 内存上下文，Arrow C++ 写 Parquet）。实现与调试中踩过的坑，直接复用可避免同类问题。

## 结构

- **内存上下文必须初始化**：heap_deform_tuple 依赖 palloc 分配 attcacheoff 缓存等 → 先 `MemoryContextInit()`，并 stub 所需后端符号（aset/generation/slab/bump/alignedalloc + snprintf 等）。
- **TupleDesc 用官方 CompactAttribute 布局手工构造**（7 列：BIGINT/INT/NUMERIC/TIMESTAMP/TEXT/TEXT/BOOL），与 PG 建表元数据一致，deform 依赖其 attlen/attalign。
- **HeapTupleData 必须填充 t_data + t_len**：`t_len = ItemIdGetLength(itemid)`，缺 t_len 会导致 deform 越界读、varlena 指针垃圾。

## 批量（batch）改造的三个 bug 教训

1. **C/C++ 跨语言结构体布局必须逐字段对齐**：C 端与 C++ 端各自定义 `HeapCols`，strbuf 字段位置不一致（C 端第 7 位、C++ 端第 11 位）→ C 端把文本写进 status_off 数组内存 → 静默数据污染，单次 1M 恰好"碰巧正确"、500k 才暴露。**修复：单侧定义为准，另一侧逐一核对字段顺序（含 offsetof 校验）**。
2. **批量边界游标漏行**：解析游标在"每行开始"推进 `next_offnum = offnum+1`，但 `row >= max_rows` 提前退出（goto done）时游标已指向下一行 → **每批漏 1 行**（1 亿行 96 批漏 95 行，id=1,048,577 处出现空洞，delta=批边界）。修复：退出前回退 `cur->next_offnum = offnum`，让未处理行留给下一批。
3. **行数上限误用 batch**：分批循环内把 `batch` 当 `max_rows` 传入 → 参数失效、总是读满全文件。修复：`want = min(batch, max_rows - total)`，达到上限后 break。

## 数据正确性校验（必做）

- 全量三查：count、distinct id、数值规则匹配（amount=(id%100000)/100）——**比行数相等更强**：批次边界漏行时 count 正确但 distinct 少、规则不匹配。
- NUMERIC 解码：零值行可只存 2 字节头（ndigits=0），先判 `ndigits<=0` 返回 0，否则 min_exp=INT_MAX 导致 20s+ 退化与垃圾值。
- 可见性：仅处理 `HEAP_XMAX_INVALID` 且非 `HEAP_UPDATED` 的行；死元组/重定向（ItemIdIsDead/Redirected）跳过。
- 页面大小 8192B；>1GB 分段文件各段整页，cat 拼接后 `page_count = size / BLCKSZ` 全局索引即正确。

## 性能基线（本机）

- 1M 行：mmap+deform 0.16-0.19s（600 万+ rows/s）、组装 0.08s、Arrow zstd 写 0.41-0.49s、端到端 0.67-0.76s、RSS 349-404 MiB（1M 批缓冲，与总行数解耦）。
- 100M 行：端到端 74.7s（133.9 万 rows/s）、RSS 403 MiB。
- 对比 DuckDB postgres_scan 直转：1M 持平、100M 快 13.5%（写盘差放大）+ 内存低 5 倍。
