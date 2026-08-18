# 调研报告：PG 转换全面数据一致性校验方法完备性验证（POC）

- 任务: T0311（0818-pg-consistency-poc）
- 日期: 2026-08-18
- 场景: research（技术调研/方法验证）

## 调研目标

回答两个问题：
1. T0301（PG 9.6/11/18 多版本 heap+CLOG→Parquet）与 T0300（MySQL）沿用的
   "全量逐字段字符串规范化对照 + 行数 + 聚合"三路校验方法，对真实转换错误的
   覆盖度/灵敏度如何？盲区在哪里？
2. 校验方法是否可被"反向验证"（被注入的错误能否 100% 捕获）？能否作为 T0308
   （4B 头 varlena/TOAST）及后续回归的校验基线？

## 方法

1. 合成宽表 `poc_consistency`（PG18 容器 t0216-pg，库 poct25，10 万行），在 pgbin
   支持的 7 列结构（id int8 / customer_id int4 / amount numeric(12,2) / created_at
   timestamp / status text / payload text / active bool）上做**值形态**覆盖：
   NULL 三形态（列级全 NULL、部分 NULL、稀疏 NULL）、空串、全空白、中文+emoji、
   480B 4B 头 varlena、2564B TOAST（仅登记）、numeric 边界（0/0.00/负/99999999.99）、
   时间微秒边界（.000000/.999999）。灌数脚本 `bench/gen_consistency.py`。
2. 导出 SQL 基准 `evidence/pg/consistency/poc_consistency.sql.tsv`（10 万行，约定
   NULL→`NULL` 文本、`to_char(...,'YYYY-MM-DD HH24:MI:SS.US')`、bool→1/0）。
3. `pgbin` 自解码转换 heap+CLOG → `evidence/pg/consistency/poc_consistency.parquet`。
4. 五维校验 `bench/verify_consistency.py`：行数 / 逐字段全值 / 聚合（count、
   sum(amount)、distinct status、active=true、id 范围、各列 NULL 计数）/ schema 元数据
   （parquet 列名+类型 vs pg_catalog 信息模式）/ 类型语义（decimal 精度、时间微秒、
   NULL vs 空串、bool 值域）。
5. Mutation 注入测试 `bench/mutate_consistency.py`：12 种变异逐一注入基准 tsv，
   验证校验脚本必须 FAIL（被捕获）：改值、值→NULL、时间精度丢失、删行、重复行、
   换列序、decimal 精度、bool 翻转、NULL↔空串、payload 截断、id 错位、尾随空格。

## 发现

### F-1. T0301 校验盲区实锤：pgbin 对含 NULL 数据的转换是坏的（3 个缺陷）

T0301 数据全部 NOT NULL（poc_orders 无 NULL 列），导致三个缺陷在"全量 PASS"下
从未暴露。本次 POC 引入 NULL 行后全部现形：

| 缺陷 | 根因 | 后果 |
|------|------|------|
| #1a nullbit 判定反转 | `if (nullbit) continue`：PG null bitmap **bit=1=非空**，代码把非空当 NULL 跳过 | 含 NULL 行时所有列错位读取 |
| #1b t_bits 偏移错误 | `PG_HEAP_HEADER_SIZE=24` 但 `offsetof(HeapTupleHeaderData, t_bits)=23`（xmin4+xmax4+t_field3 4+ctid6+infomask2 2+infomask2+t_hoff1） | bitmap 从数据区首字节读起，列级错乱 |
| #2 NULL 语义丢失 | pgbin 写 parquet 时所有 Arrow 数组 validity buffer 传 `nullptr,0` | parquet 中 NULL 变空串/0/0.00/epoch/false |
| #3 未初始化 UB | NULL 列直接 `continue`，cols 数组（`new[]`）读垃圾 | 潜在越界读（`__divti3` SIGFPE 即由此触发） |

修复（已获用户批准，偏离 PRD"不改 src/pg"一条，记录于 clarifications 选项 A）：
- #1a/#1b：`pg_heap_reader.c` 判定改为 `!nullbit` 判 NULL、`PG_HEAP_HEADER_SIZE` 24→23；
- #3：NULL 列显式写哨兵并登记 `PgCols.nulls` 位图；
- #2：`pgbin.cpp` 由 `nulls` 位图构建各列 validity buffer，Decimal128 Builder 用
  `AppendNull`。

修复后含 NULL 转换成功（10 万行，TOAST 50 行跳过），各列 NULL 计数与灌数分布
精确一致（cid=5263/amt=4347/ts=3448/st=14285/pl=7692/act=5882）。T0301 三版本
（9.6/11/18）回归仍 PASS（无 NULL 数据不受影响）。

### F-2. TOAST 是登记不判值的长尾盲区

`g%500==0` 的 2564B payload 行（200 行）pgbin 按设计跳过（`skipped_toast`），
parquet payload 为空串。五维校验将此类行标记为"仅登记"（id%500==0 白名单），
**不校验内容**。真实转换链路对 2KB+ 字段的值正确性仍无验证——属 T0308。

### F-3. 五维校验全部 PASS（修复后）

- 维度 1 行数：100000 = 100000
- 维度 2 逐字段：10 万行 × 7 列全一致（TOAST 200 行仅登记）
- 维度 3 聚合：13 项全一致（含 amount 求和 9847668592.51、各列 NULL 计数）
- 维度 4 schema：parquet（BIGINT/INTEGER/DECIMAL/TIMESTAMP/VARCHAR/VARCHAR/BOOLEAN）
  与 pg_catalog 列名/序/类型映射全 PASS
- 维度 5 类型语义：decimal 固定 2 位文本、timestamp 微秒 `%f`、NULL vs 空串可区分

### F-4. Mutation 注入捕获率 12/12 = 100%

基线（未变异）PASS，12 种变异逐一被捕获（见 `mutate_consistency.py` 与
`/tmp/opencode/mut/` 各变异 tsv + verify 输出）。覆盖维度：值/语义/NULL/行级
（删/重）/列序/精度/bool/时间/文本/空白。这证明校验方法对上述变异类确定性 FAIL。

## 结论与建议

1. **校验方法可信**：五维（行数+逐字段+聚合+schema+类型语义）对好数据 PASS、
   对 12 类注入错误 100% 捕获，可作为校验基线。三路"规范化对照"是逐字段维度的
   核心，聚合/schema/类型语义三个新增维度补齐了隐式盲区。
2. **T0301 结论需修订**：其"三版本全量对照 PASS"仅覆盖全 NOT NULL、短文本形态；
   pgbin 的 NULL 支持在 T0301 范围内是隐式缺失。建议在 T0301 记录中追加本 POC
   的盲区声明与修复引用。
3. **固化建议（供 T0308 及后续）**：
   - 校验基线 = verify_consistency.py（五维）+ mutate_consistency.py（mutation ≥12
     类，捕获率须 100%）；
   - T0308 必须在含 NULL/4B 头 varlena/TOAST 数据上跑校验基线，并**实现 TOAST 值
     对照**（当前仅登记）；建议 pgbin 对 TOAST 行输出占位 + toast 计数校验；
   - 后续新增类型（float/uuid/json/bytea 等）应把"类型全集→parquet 类型映射"纳入
     schema 维度对照。
4. **过程建议**：校验脚本与转换器不应共享错误的"正确性假设"——本 POC 通过
   "合成表注入形态"而非"复用旧数据"暴露缺陷，该思路应固化为转换类任务的默认做法。

## 参考资料

- 源码：`src/pg/pg_heap_reader.c`、`src/pg/pgbin.cpp`、`src/pg/pg_versions.h`
- PG18 权威逻辑：`third_party/pg184/src/access/common/heaptuple.c`
  （`heap_form_tuple`/`heap_fill_tuple`/`fill_val` null bitmap 写入约定：
  bit=1 非空、bit 序 LSB-first、`offsetof(HeapTupleHeaderData, t_bits)=23`）；
  `third_party/pg184/include/access/tupmacs.h`（`att_isnull`）
- 数据与脚本：`evidence/pg/consistency/`（heap/pg_xact/sql.tsv/parquet）、
  `bench/gen_consistency.py`、`bench/verify_consistency.py`、
  `bench/mutate_consistency.py`
- 容器验证：t0216-pg（PG18，user test/test，db poct25）SQL 基准；pageinspect
  `heap_page_items` t_bits 复核