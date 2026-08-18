---
schema: pdca.asset/v1
id: T0301-0818-pg-version-convert-test
phase: check
source_ids: ["t0301-convert-report", "t0301-extract-script", "t0301-gen-script", "t0301-verify-script", "convergence-map"]
---

## 上下文

对 PostgreSQL 9.6 / 11 / 18 三版本各执行一次完整 heap+CLOG 物理直读→Parquet 转换测试
（逐版本），parquet 与 SQL 基准全量逐字段对照（1M×7 列，差异=0 含聚合），实现
PG9.x pg_clog 读取（pg_clog_legacy_pg9.c）与 pgbin 运行时版本适配（--pg-version 分派
+ 字段自解码），验证多版本环境离线转换正确性。场景：development。

## 假设与结果

| 假设 | 结果 |
|---|---|
| 三版本容器就绪，各版本 poc_orders 独立灌数 1M（SQL count=1,000,000） | **成立**：t0301-pg96/11 与 t0216-pg 各 1M 行，heap 文件 154,566,656 B |
| 各版本干净关闭固化并提取 heap+CLOG 至 evidence/pg/versions/{96,11,18}/ | **成立**：96=pg_clog/、11/18=pg_xact/（CLOG 目录随版本迁移） |
| pg_clog_legacy_pg9.c 实现，PG9.6 直读与 SQL 一致 | **成立**：复用 pg_clog_xid_status（目录参数化），PG9.6 全量 PASS |
| pgbin 运行时版本适配 + 字段自解码，三版本 rows=1,000,000 | **成立**：三版本均 rows=1M，seen_total=1M |
| 三版本 parquet 与 SQL 全量逐字段对照差异数=0 | **成立**：三版本 1M×7 差异=0，聚合 PASS（count=1M / SUM=5000005000.00 / status=4 / active_true=50 万 / id=[1,1M]） |
| PG18 默认参数（无 --pg-version）基线无回归 | **成立**：默认参数全量 1M 转换 PASS |

## 分析

- **AC 判定**：
  - AC-1（三版本容器+独立灌数 1M）**PASS**：gen_pg_versions.py 灌数，SQL count=1,000,000
  - AC-2（固化提取 heap+CLOG 至 evidence/pg/versions/）**PASS**：extract_version_pg.sh 提取，目录按版本
  - AC-3（pg_clog_legacy_pg9.c 实现，PG9.6 直读与 SQL 一致）**PASS**：legacy 转发目录参数化读取器；PG9.6 全量对照差异=0
  - AC-4（--pg-version 运行时适配 + 自解码，三版本 rows=1M）**PASS**：三版本均 rows=1,000,000；自解码替代编译期 heap_deform_tuple
  - AC-5（三版本全量逐字段差异=0 含聚合）**PASS**：verify_version_convert.py 三路验证全 PASS
  - AC-6（每版本记录入 evidence + manifest 登记；PG18 基线无回归）**PASS**：EVIDENCE.md + manifest.jsonl 登记；PG18 默认参数无 --pg-version 转换 PASS
- **关键事实修正（实测推翻 PRD 版本差异假设）**：
  1. **heap 头布局三版本一致**（xmin/xmax/cid@0/4/8、ctid@12、infomask2@18、infomask@20、
     t_hoff@22、头 24B）。三容器 pageinspect 均 t_hoff=24、t_infomask=2306。旧假设
     "PG12 移除 t_xvac 使头 28B→24B"有误：t_xvac 与 t_cid 同处 t_field3 union（4B），
     不改变头布局。PG11 转换崩溃（t_hoff 读 b[26]=0→dp=b 全错位）即由此根因，修正后通过。
  2. **varlena 编码三版本一致（packed）**：1B 头最低位=1 长度=头>>1（PG9.6/11 payload
     头 0xA3→81B）；4B 头低 2 位=00/10 长度=(va_header>>2)&0x3FFFFFFF（PG11 临时表
     200B 文本实测 0x00000330>>2=204B）。旧假设"PG13- 老格式（最高位标志）"无实例支撑。
  3. **CLOG 唯一版本差异为目录名**：pg9.x- pg_clog/，PG10+ pg_xact/；SLRU 段与 2-bit
     xid 状态编码一致，读取器同一（目录参数化）。
  4. **--pg-version=96 的 atoi 陷阱**：atoi("96")=96>11 早前被误判为 PGVER_12PLUS，
     PG9.6"成功"是假象（恰好 24B 布局+packed 才是正确解释）。修正后 --pg-version 仅
     作源版本标注，不参与解码分派（解码无版本差异）。
- **性能**：三版本全量转换 0.7-0.9s（~1.2-1.4M rows/s，ZSTD 写出）；吞吐非 AC 验收项。

## 失败原因

（无 rejected/partial；全部 AC PASS）

## 适用边界

- 适用：PG 9.6/11/18 干净关闭快照下的 heap+CLOG 离线转换与全量对照；CLOG 目录名版本迁移处理。
- 边界：
  - 4B 头 varlena 未进入正式对照数据（poc_orders 全为 1B 头短值≤127B），仅 PG11 临时表单点实测确认（>>2 编码）；TOAST 外置/压缩属 PRD 范围外（跳过逻辑用 PG18 宏，packed 判定通用）。
  - "布局/编码一致"实测范围为 9.6~18，PG10/12/14/16 中间版本未单独实测（推论依据结构一致，但按范围外对待）。
  - 在线数据一致性、WAL 崩溃恢复、大表规模化不在本任务范围。

## 下一轮建议

1. 若需覆盖 4B 头 varlena 与 TOAST 外置路径，扩展 poc_orders 灌数含长文本列（>127B 与 >2KB）并纳入全量对照。
2. pgbin 参数统一为 `<heap> <clog_dir> <out> [--rows=] [--pg-version=]`（对齐 mysqlbin 风格，PRD 备注）。
3. 将 extract_version_pg.sh / verify_version_convert.py 纳入后续多版本回归流程复用（与 T0300 的 mysql 版本工具并列）。