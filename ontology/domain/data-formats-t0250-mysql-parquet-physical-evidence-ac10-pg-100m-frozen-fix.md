---
schema: pdca.asset/v1
id: ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac10-pg-100m-frozen-fix
type: domain
layer: Knowledge
status: active
summary: PG 100M 物理直读回归：FROZEN hint-bit 误判根因与修复（AC-10）
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
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# PG 100M 物理直读回归：FROZEN hint-bit 误判根因与修复（AC-10）

> T0250（0813-mysql-parquet-physical）| 场景：research | 阶段：do 收口
> 日期：2026-08-14 | 工具：build/pgbin

## 1. 背景

对 PG 18.4 表 `poc_orders_100m`（7 列，同 `poc_orders` 结构）灌入 100,000,000 行，
干净关闭固化 heap（7,249,559,552 B = 884,956 页 × 8 KiB）+ pg_xact/0000。

pgbin 直读回归首测结果异常：`rows=65,581,895`（应 100M），`skipped_invisible=34,418,105`。
直观排查（页首 item 抽样）呈现"约一半页 invisible 且 xmin 恒 29218"的假象，
一度误判为数据/合并问题，实际为**可见性判定逻辑 bug**。

## 2. 根因

### 2.1 PG12+ heap tuple 头布局（与 PG9 及以前不同）

`HeapTupleFields` 为 **3 字段**（xmin/xmax/field3 合并 cmin/cmax，共 12 B），
实测字段偏移（pageinspect 对拍确认）：

| 字段 | 偏移 | 实测值 |
|---|---|---|
| t_xmin | 0 | 29218 |
| t_xmax | 4 | 0 |
| t_field3 (t_cid) | 8 | 0 |
| t_ctid | 12 | (0,1) |
| t_infomask2 | 18 | 7 (natts) |
| t_infomask | 20 | 0x0B02 |
| t_hoff | 22 | 24 |
| t_data | t_hoff | id=1 |

（旧文档/经验值 t_infomask@24、t_hoff@26 是 PG9.0- 布局，PG12+ 已前移。）

### 2.2 FROZEN hint-bit 双置

100M 行中约 34.4% 被 autovacuum/vacuum freeze，hint bit：

```
HEAP_XMIN_FROZEN = HEAP_XMIN_COMMITTED(0x0100) | HEAP_XMIN_INVALID(0x0200) = 0x0300
```

实测 `t_infomask=0x0B02 = FROZEN(0x0300) + XMAX_INVALID(0x0800) + HASVARWIDTH(0x0002)`。

### 2.3 判定顺序缺陷（T0250 回归根因）

`src/pg/pg_heap_reader.c::pg_tuple_visible` 原逻辑先判 XMIN_INVALID：

```c
if (infomask & HEAP_XMIN_INVALID) return 0;   /* ← frozen 行(含 INVALID bit)在此被误判 */
if (infomask & HEAP_XMIN_FROZEN)   return 1;   /* ← 永远执行不到 */
```

frozen 元组两 bit 同置，第一条先命中 → 34.4M frozen 行全部判 invisible（aborted）。

## 3. 修复

调整判定顺序：INVALID 置位时先检查 COMMITTED 是否同置（frozen→可见），仅纯 INVALID 判 aborted；
无 hint bit 走 CLOG（原逻辑保留）。

```c
if (infomask & HEAP_XMIN_INVALID)
{
    if (!(infomask & HEAP_XMIN_COMMITTED))
        return 0;   /* 仅 INVALID → aborted */
}
else if ((infomask & HEAP_XMIN_COMMITTED) == 0)
{
    /* 查 CLOG */
}
```

## 4. 验证（物理直读 vs SQL 差异 = 0）

| 指标 | 修复前 | 修复后 |
|---|---|---|
| rows | 65,581,895 | **100,000,000** |
| skipped_invisible | 34,418,105 | **0** |
| seen_total | 100,000,095 | 100,000,095 |
| SQL `COUNT(*)` | 100,000,000 | 100,000,000 |
| 差异 | -34,418,105 | **0** |

- Parquet（正式产物）：`data/100m_pg/poc_orders_100m_pgbin.parquet`，100M 行 × 7 列
  （id int64 / customer_id int32 / amount decimal128(12,2) / created_at timestamp[us] /
  status string / payload string / active bool）。
- 全量校验：96 row group 分块，id 1..100,000,000 **连续无缺无重**；
  样例值（amount=0.01 起递增、created_at=2026-01-01 00:00:01 起、status 轮转、active 交替）符合灌数定义。
- 性能：parse 12.2s / 写出 36.5s / total 52.7s / **1.90M rows/s**（vs DuckDB postgres_scanner 768K rows/s）。

## 5. 经验沉淀

1. **FROZEN 判定的顺序**是 MVCC 物理解读最容易踩的坑：`FROZEN=COMMITTED|INVALID` 双置，
   `if (XMIN_INVALID)` 必须先排除 FROZEN。
2. **heap 头布局** PG12+ 与旧文档不同（t_field3 合并、infomask 偏移 20），
   判读以 pageinspect 对拍为准，勿套 PG9 布局。
3. 用 pageinspect（`heap_page_items` + `get_raw_page`）做字段偏移锚定是最快定位手段。

## 6. 产物

- 修复：`src/pg/pg_heap_reader.c`（pg_tuple_visible 判定顺序）
- 数据快照：`data/100m_pg/poc_orders_100m_heap`（7.25G）+ `data/100m_pg/pgxact/0000`
- Parquet：`data/100m_pg/poc_orders_100m_pgbin.parquet`（662,961,251 B）
- 错误产物备份：`data/100m_pg/poc_orders_100m_pgbin.bad65.6m.bak`（65,581,895 行，仅作回归对比）
