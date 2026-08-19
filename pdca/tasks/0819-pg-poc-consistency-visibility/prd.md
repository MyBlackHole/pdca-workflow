# T0325: 一致性+数据可见性 POC（双链路 PG+MySQL，端到端闭环 + 可见性矩阵）— 规格文档

## 问题陈述

- **现状**: PG 侧 T0308 已实现 TOAST 完整解码（pglz+lz4）并验证一致性（100万×3 五维+mutation 12/12），但可见性判定（`skipped_invisible/skipped_dead`）从未系统化矩阵验证——仅"全可见"场景间接覆盖；infomask（hint bit）vs clog 两条判定路径、DELETE/UPDATE 死版本、ROLLBACK 中止行均无专项证据。MySQL 侧 mysqlbin 已实现 delete-mark 过滤（`mysql_parse_pages.c:826`，REC_INFO_DELETED_FLAG 0x20）并有四版本/性能 evidence，但同样无系统化可见性矩阵，且双链路缺统一端到端 POC 闭环演示。
- **目标**: 双链路（PG+MySQL）× 双维度（一致性+可见性）POC 全 PASS：PG 可见性矩阵（7 类判定路径）与 MySQL 可见性矩阵（delete-mark/UPDATE 旧版本）系统化验证；三版本 PG + 四版本 MySQL 端到端一致性闭环。
- **差距**: 可见性判定两链路均无专项矩阵；一致性验证无统一闭环演示。

## 解决方案

**场景约束（用户指定）**：所有 POC 均在**数据库正常关闭（graceful offline）**状态执行——PG 走标准停库（无活跃连接后 `pg_ctl stop -m smart` 或等价的正常关闭，shutdown checkpoint 落盘），MySQL 走 `mysqladmin shutdown` 标准关闭，关闭后复制数据文件再转换。不使用 immediate/crash 关闭。不覆盖在线一致性（WAL/复制场景，超出物理直读）。关闭场景下：
- PG：正常关闭时所有事务已结束，已提交事务 clog 已 flush；abort 事务（ROLLBACK）行保留在数据页且 clog=aborted → pgbin 判 invisible；无"运行中复制 clog stale"陷阱；无"未提交活跃事务残留"（正常关闭不容许）。
- MySQL：正常关闭时未提交事务回滚（插入行 delete-marked 待 purge），已提交可见行无 delete-mark；`delete-mark 过滤`即完整可见性判定。

- **PG 可见性矩阵（PG18，正常关闭场景）**：构造 `vis_matrix` 表，每类行代表一种判定路径：
  - A 已提交·无 hint bit（提交后不读，关闭后走 clog 路径）
  - B 已提交·有 hint bit（提交后 SELECT 触发，关闭后走 infomask 路径）
  - C DELETE 后提交（旧版本 → dead）
  - D UPDATE 后提交（旧版本 → dead）
  - F ROLLBACK 事务的行（clog=aborted → invisible；正常关闭下唯一 invisible 来源）
  - G 常规提交行（可见基线）
  （E"未提交活跃残留"在正常关闭下不适用，已移除）正常关闭后复制 heap/toast/pg_xact，pgbin 转换，断言 `rows / skipped_invisible / skipped_dead` 与预期精确一致，且 parquet 内容 == PG 可见行集。
- **MySQL 可见性矩阵（关闭场景）**：复用 `gen_mysql_scenarios.py` V2（UPDATE 5+DELETE 5）/V3（批量 DELETE 5）场景并新增矩阵对照；正常 shutdown 后复制 ibd，验证 mysqlbin 过滤 delete-mark 后输出 == DB 可见行（逐字段），无 delete 基线四版本一致。未提交事务 MVCC 可见性（undo 链/活跃事务）**范围外**（另立项）。
- **PG 端到端一致性 POC**：三版本（18/11/96）poc_toast 关闭后走 `数据文件 → pgbin → parquet → verify_consistency --table` 五维全值对照。
- **MySQL 端到端一致性 POC**：四版本（56/57/80/84）关闭后 `ibd → mysqlbin → parquet → verify_version_convert` 全量逐字段+聚合对照复验。
- 验证均落盘 evidence 并写 research-report（含双链路对比与差距记录）。

## Seam 分析

### 测试接缝
research 场景，无被测代码修改；验证对象为既有 `build/pgbin` 与 `bench/verify_consistency.py`（T0308/T0301 产物）。新脚本为一次性 POC 构造工具（bench/gen_vis_matrix.py），不进生产链路。

### 验收可测性
- 每类可见性行有独立构造手段与 pageinspect 佐证，pass/fail 可判定。
- 统计断言：`rows/skipped_invisible/skipped_dead` 有确定预期值。
- parquet 内容与 PG 可见行对照可机器判定。

## 用户故事

1. 作为 pgbin 使用者，我想要系统化的可见性判定验证，以便确认物理直读不会漏读/误读已提交行或错留死行/中止行。
2. 作为交付方，我想要端到端一致性 POC 闭环报告，以便对外证明转换正确性。

## 实现决策

- 复用既有 `build/pgbin`（`--toast=/--rows=/--pg-version=`，严格参数）、`bench/verify_consistency.py`（`--pg-dsn`/`--table`）、`bench/gen_toast.py` 形态分桶模式。
- 新写一次性脚本 `bench/gen_vis_matrix.py`：构造 vis_matrix 并导出 `heap/toast/pg_xact` 副本 + 预期可见性清单（JSON）。
- 可见性判定依据：pgbin 源码 `pg_tuple_visible` 逻辑（infomask XMIN_COMMITTED/XMIN_INVALID + clog 查证）。
- 导出统一走"INSERT/SELECT→**单独** `CHECKPOINT`→复制文件"安全流程（T0308 已验）。
- 不修改 pgbin 生产代码；若发现判定缺陷，评估修复范围另行立项。

## 测试决策

- 验证方式为构造数据 + 断言统计 + 内容对照（非单测）。
- 对照基准：pageinspect（行状态）+ PG 查询（可见行集）+ tsv 导出。

## 验收标准

- [ ] AC-1: 端到端一致性 POC：三版本（18/11/96）poc_toast 走 文件→pgbin→parquet→verify 五维全 PASS，skipped_toast=0，产出统一 POC 报告
- [ ] AC-2: 可见性矩阵表 vis_matrix（PG18，正常关闭场景）构造完成，6 类行（A/B/C/D/F/G）xid/infomask 状态经 pageinspect 核对符合预期（E 未提交残留不适用），预期可见性清单 JSON 落盘
- [ ] AC-3: pgbin 转换 vis_matrix：rows/skipped_invisible/skipped_dead 与预期精确一致（含 A 走 clog、B 走 infomask、C/D dead、F invisible、G 基线）
- [ ] AC-4: vis_matrix 的 parquet 内容 == PG 可见行集（逐字段全值对照 PASS）
- [ ] AC-5: MySQL 一致性 POC：四版本（56/57/80/84）正常关闭后 ibd→mysqlbin→parquet→verify_version_convert 全量逐字段+聚合对照 PASS
- [ ] AC-6: MySQL 可见性矩阵：DELETE/UPDATE 场景（复用 gen_mysql_scenarios V2/V3）正常关闭后 mysqlbin 输出 == DB 可见行（逐字段全值对照），无 delete 基线四版本一致
- [ ] AC-7: 双链路 POC（PG+MySQL）结论写入 research-report 并登记 evidence

## 范围外

- 不改 pgbin 生产代码（除非发现缺陷，另行立项）。
- 不做三版本可见性矩阵（仅 PG18；三版本一致性已有 T0308 覆盖）。
- 不做性能压测。

## 备注

- 前置事实（T0308 已验）：`psql -c "INSERT; CHECKPOINT;"` 同串共享隐式事务导致 clog 未落盘，须单独 CHECKPOINT；pgbin 假定 poc_orders 同构 7 列（id int8）。
- 关联：parent T0301；知识 `knowledge/pg/toast-compressed-varlena-layout.md`。