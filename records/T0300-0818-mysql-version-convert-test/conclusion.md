---
schema: pdca.asset/v1
id: T0300-0818-mysql-version-convert-test
phase: check
source_ids: ["t0300-convert-report", "t0300-extract-script", "t0300-verify-script", "convergence-map"]
---

## 上下文

对 MySQL 5.6/5.7/8.0/8.4 四版本各执行一次完整 .ibd→Parquet 转换测试（逐版本），
parquet 与 SQL 基准全量逐字段对照（1M×7 列），补齐 T0250 AC-1 缺失的 8.0 聚合列，
验证版本特性拆分（mysql_sdi_80.c / mysql_layout_schema_56_57.c 等）后无回归。场景：development。

## 假设与结果

| 假设 | 结果 |
|---|---|
| 四版本 .ibd 均可从既有容器 volume 干净提取（不重灌） | **成立**：extract_version_ibd.sh 提取 56/57/80/84 全部成功（56/57/84=201MB, 80=138MB） |
| 每版本 mysqlbin 转换 rows=1,000,000 | **成立**：四版本全部 rows=1,000,000 |
| 每版本 parquet 与 SQL 全量逐字段对照差异数=0 | **成立**：四版本全量差异=0（1M×7 列） |
| 聚合对照一致（含 8.0） | **成立**：count=1M / SUM(amount)=499,995,000.00 / distinct status=4 / active=true=500,000 / id 1~1M，全部与 SQL 一致 |
| 版本特性拆分无回归 | **成立**：四版本走拆分后的解析路径（SDI / schema / 统一页解析）全部 PASS |

## 分析

- **AC 判定**：
  - AC-1（四版本 .ibd 提取）**PASS**：extract_version_ibd.sh（innodb_fast_shutdown=0 干净关闭 + podman unshare）
  - AC-2（每版本转换 rows=1M）**PASS**：8.0/8.4 走 SDI 自动布局，5.6/5.7 走 --schema=bench/poc_orders.schema
  - AC-3（全量逐字段差异=0）**PASS**：verify_version_convert.py 三路验证（行数+逐字段+聚合）
  - AC-4（8.0 聚合补齐）**PASS**：聚合对照含 8.0 全一致；ac1_four_versions.md 聚合表已补 8.0 列
  - AC-5（记录+manifest 登记）**PASS**：T0300_version_convert.md + 源项目 evidence/manifest.jsonl 登记
  - AC-6（版本拆分无回归）**PASS**：AC-2/AC-3 通过即证（四版本均经拆分路径正确转换）
- **重要发现（页序陷阱）**：mysqlbin 按物理页序输出、不保证主键序（56/57/84 页序≠id 序，8.0 恰好一致）。
  对照脚本以 id 为键排序后逐行比对实现顺序无关全量校验；该点已补入 evidence/mysql/EVIDENCE.md。
- **权限坑修复**：podman unshare 内 chown $(id -u) 在 uid 映射下落到 100999 导致宿主侧不可读；
  改 unshare 内 chown 0:0（命名空间根 = 宿主调用者）后宿主属主正确。
- **吞吐说明**：四实例并行转换争用致 275~277K rows/s，低于 AC-1 单实例基准（302~937K），非回归（吞吐非 AC 验收项）。

## 适用边界

- 适用：同一 .ibd（干净关闭快照）下逐版本转换测试与全量对照、版本拆分回归验证。
- 不适用：在线数据一致性（需冻结场景）、性能基准（需单实例）、大表规模化（100M 级见 T0250 AC-6/AC-7）。

## 下一轮建议

1. 将 T0300 转换测试工具（extract_version_ibd.sh / verify_version_convert.py）纳入后续回归流程复用。
2. 顺序敏感消费 mysqlbin 输出前必须先按主键排序（EVIDENCE.md 已记录，作为约定）。
3. 如需版本级性能基准，单独单实例运行避免并行争用干扰。
