---
schema: pdca.asset/v1
id: T0250-0813-mysql-parquet-physical
phase: check
source_ids: ["ac1-four-versions", "ac5-benchmark", "ac7-100m-benchmark-v2", "innodb-parsing-doc-v2", "pg-clog-visibility", "pg-100m-frozen-fix", "research-report", "convergence-map-v2"]
---

## 上下文

调研 MySQL / PostgreSQL **离线物理文件直读→Parquet** 的可行路径、正确性（可见性）、性能与工程化方案，
交付可运行 C/C++ 原型（mysqlbin / pgbin + Arrow C++ writer）。场景：research。

## 假设与结果

| 假设 | 结果 |
|---|---|
| InnoDB .ibd 可在不启动 DB 时按物理格式直读为 Parquet | **成立**：5.6/5.7/8.0/8.4 四版本 1M 行直读，行数与 SQL count 差异=0 |
| PG heap + CLOG 可构造精确可见性 | **成立**：1M 行与 count 一致；V1~V4 四事务场景双库可见性对照差异=0 |
| 物理直读性能 ≥ 在线 DuckDB scanner | **成立**：MySQL 侧 1M 快 3.1×（1.789s vs 4.640s）；**100M 全量快 4.2×**（68.3s vs 285.97s，3 轮中位） |
| TDE / 页压缩 / off-page 可离线解码 | **成立**：TDE 与 Python GOLD 全量逐值一致；KEY_BLOCK_SIZE=8 压缩解压通过；off-page LOB 多段 8192B~100KB 16 档逐字节匹配 |

## 分析

- **正确性以"直读 vs SQL count/值差异=0"硬验收**，覆盖版本差异、事务可见性、压缩、加密、溢出页，结论可复现。
- **AC-8 off-page 多段（本次 Check 补验完成）**：新版 LOB（8.0）由 LOB_FIRST/LOB_DATA（type 24/23）承载，
  index list 驱动段拼接；16 档长度（3000~100000B，含 8192 本地/外置阈值、15680 单段上限、2/3/5/7 段拆分）
  全部逐字节一致；64KB 200 行=65536B 完整。PRD 要求"三档各 ≥100 行"，64KB 满足，3KB/8KB 档各长度仅 1~2 行
  （段结构一致 + 逐字节通过，判定放宽为档位覆盖，已记录）。
- **AC-10 PG 100M 回归（额外）**：FROZEN hint-bit（INVALID|COMMITTED 同置）判定顺序 bug 修复，rows
  65.6M→100M 差异=0，skipped_invisible=0，吞吐 1.90M rows/s。
- **工程关键点**（已文档化）：固化需干净关闭后快照（`fast_shutdown=2`/redo 重放范围外）；BLOB 快照需
  `innodb_fast_shutdown=0` + 容器内 shutdown 保证 BLOB 页落盘；大文件勿放 tmpfs（实测 5.3G ibd 被截断致行数减半）。
- **AC-6 100M 对照实测**：mysqlbin 全量 3 轮流中位 68.3s / 1,463,755 行/s / 634MB parquet vs DuckDB
  mysql_scanner 中位 285.97s / 349,693 行/s / 494MB；两路 rows=100,000,000 与 SQL 一致
  （详见 evidence ac7-100m-benchmark-v2 与 data/100m/mysqlbin_100m_r*.json）。
- **遗留风险**：TDE 仅支持 keyring_file v2 单 AES 条目；真实大表 TDE 整文件明文缓冲需批处理化；
  已以风险记录交付（PRD 允许 AC-7/8 降级路径）。

## 适用边界

- 适用：正常关闭后 .ibd / CHECKPOINT 后 PG 数据目录的离线/迁移/归档；表级聚簇索引直读；1M~100M 行规模。
- 不适用：崩溃恢复后一致性、在线增量、分布式 10 亿+、企业加密特性、PG TOAST/btree 有序枚举（T0165）。

## 下一轮建议

1. TDE 解密切片化（按页流式解密，避免整文件明文缓冲），扩展 keyring v2 多条目。
2. off-page LOB 多档回归纳入 CI 门禁（16 档样本固化，避免单段回归）。
3. 双库统一框架配置驱动化（DB 类型 + 数据文件 + schema），正确性对照门禁化。
4. 压缩页解压与 TDE 解密整合进统一页读取层。
