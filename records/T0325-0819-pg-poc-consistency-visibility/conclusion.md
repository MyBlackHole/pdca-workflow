---
schema: pdca.asset/v1
id: T0325-0819-pg-poc-consistency-visibility
phase: check
source_ids: [research-report, pg-consistency-18, pg-consistency-11, pg-consistency-96, pg-vis-pageinspect, pg-vis-expected, pg-vis-pgbin, pg-vis-verify, mysql-consistency-56, mysql-consistency-57, mysql-consistency-80, mysql-consistency-84, verify-mysql-scen, mysql-vis-v2-verify, mysql-vis-v3-verify, mysql-vis-v4-verify, mysql-vis-v5-verify]
---

## 上下文
T0325（parent T0301）：双链路（PG+MySQL）一致性 + 可见性 POC，场景约束为**数据库正常关闭（graceful offline）**——PG `podman stop` 优雅关闭、MySQL `mysqladmin shutdown` 后复制数据文件再转换。PG 侧做三版本端到端一致性 + PG18 可见性矩阵（6 类判定路径）；MySQL 侧做四版本一致性 + delete-mark 可见性矩阵（V2-V5 场景）。research 场景，不改生产代码。

## 假设与结果
- 假设 A（正常关闭后 clog 已 flush，可见性可精确判定）：成立 — PG 三版本 skipped_invisible/dead/toast 全 0，五维 PASS。
- 假设 B（PG 可见性可由 6 类行矩阵区分 clog/infomask/dead/aborted 路径）：成立 — vis_matrix rows=4 / skipped_invisible=3 / skipped_dead=0 精确命中，parquet==可见行集。
- 假设 C（MySQL 关闭场景下 delete-mark 过滤即完整可见性）：成立 — V2(11→6)/V3(10→5)/V4(回滚行过滤)/V5(off-page 更新) 全部 parquet==SQL 可见行，逐字段差异 0。
- 假设 D（四版本一致性全量逐字段可复验）：成立 — 56/57/80/84 各 100 万行差异 0，聚合 PASS。

## 分析
- PG 一致性：三版本 10000 行 poc_toast（含 TOAST 全形态）正常关闭快照 → pgbin → verify 五维全 PASS。
- PG 可见性矩阵：pageinspect 核对（A 无 hint 走 clog、B/G 有 hint 走 infomask、C/D xmax committed、F xmin aborted），断言精确命中；副产物发现两个陷阱（psql 隐式事务 ROLLBACK 回滚整串、count(*) index-only scan 不设 hint bit）。
- MySQL 一致性：四版本 1M 行全量逐字段差异 0 + 聚合 PASS（56/57 --schema，80/84 SDI）。
- MySQL 可见性：新增 bench/verify_mysql_scen.py（通用 N 列对照，TEXT→binary 需 bytes 规范化）验证 V2-V5。
- 双链路对比：PG 用 xmin/xmax+hint bit+clog 精确判定；MySQL 关闭场景等价 delete-mark 过滤。差距：MySQL 未提交活跃事务 MVCC（undo/trx_sys）范围外。

## 缺口补齐（grill 二次审查，用户要求补齐后确认）
- (a) MySQL 5.6/5.7/8.4 V2/V3 删除场景复验：全 PASS（差异 0）；修复 --schema nullable 契约
  （InnoDB 列默认可空，schema 补 :null 后长度数组正确，TEXT 不再读空）。
- (b) PG dead line pointer：正常关闭下 VACUUM 清理死行为 unused，skipped_dead=0 正确；
  ItemIdIsDead 分支仅运行中场景（并发引用）触发，属范围外。
- (c) PG FROZEN：VACUUM FREEZE 后 infomask 0x0B02，pgbin rows=3/invisible=0 全值一致 PASS。
- (d) A 类 clog 间接证据：已注明推断性质。

## 逐条 AC 判定（补齐后）
- AC-1（PG 三版本五维 PASS）：PASS — pg-consistency-18/11/96
- AC-2（vis_matrix 6 类行 + FROZEN）：PASS — pg-vis-pageinspect/pg-vis-expected/pg-frozen-pgbin/pg-frozen-dead-verify
- AC-3（pgbin 断言 + VACUUM-dead）：PASS — pg-vis-pgbin/pg-dead-pgbin
- AC-4（parquet==PG 可见行集）：PASS — pg-vis-verify/pg-frozen-dead-verify
- AC-5（MySQL 四版本一致性）：PASS — mysql-consistency-56/57/80/84（差异 0）
- AC-6（MySQL 可见性 V2-V5 + 56/57/84 删除复验）：PASS — verify-mysql-scen + 10 份 verify
- AC-7（research-report+evidence）：PASS — research-report-v2 + 30 项登记

## 失败原因（仅 rejected/partial）
（无）

## 适用边界
- 场景仅覆盖**正常关闭**（PG smart/fast 优雅关闭 + shutdown checkpoint；MySQL mysqladmin
  shutdown 回滚所有未提交事务）：PG 无未提交活跃残留（clog 无 IN_PROGRESS）；MySQL 不可见行
  必 delete-marked。**因此 undo/trx_sys 与 PG IN_PROGRESS/ItemIdIsDead 均无需考虑**——
  未提交事务已回滚/未落盘，无并发快照（详见 research-report 与 knowledge/
  mysql/normal-shutdown-visibility-scope.md、knowledge/pg/visibility-clog-infomask.md）。
  运行中复制（未提交事务）在 PG 走 clog=IN_PROGRESS 不可见、MySQL 需 undo/trx_sys（范围外）。
- 可见性矩阵为 PG18 单版本；MySQL 矩阵为 8.0 单版本（其余版本一致性已验证，delete-mark 过滤逻辑统一，
  且 56/57/84 删除场景已复验）。
- verify 对照依赖 --pg-dsn（information_schema）/SQL 导出基准，仅验证关闭后快照。

## 下一轮建议
- MySQL 未提交活跃事务 MVCC 可见性（undo 链/trx_sys）立项（物理直读在线一致性前提）。
- 可见性矩阵可扩展至 PG11/96 与 MySQL 5.6/5.7 以覆盖跨版本可见性差异。
