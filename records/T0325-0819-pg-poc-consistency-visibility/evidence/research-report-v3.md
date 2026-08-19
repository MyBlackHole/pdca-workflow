# T0325 双链路一致性 + 可见性 POC — 调研报告

## 场景约束（用户指定）
所有验证均在**数据库正常关闭（graceful offline）**后复制数据文件再转换：
- PG：`podman stop` 优雅关闭（shutdown checkpoint 落盘 clog/hint bit）后复制 heap/toast/pg_xact；
  已提交事务 clog 已 flush，abort 事务行保留且 clog=aborted。
- MySQL：容器内 `mysqladmin shutdown`（innodb_fast_shutdown=0 全量刷盘）后复制 .ibd；
  正常关闭回滚未提交事务（插入行 delete-marked），可见行无 delete-mark。

## PG 端到端一致性 POC（AC-1）
三版本（18/11/96）poc_toast（10000 行，含行内/external 压缩与未压缩/NULL 分桶），
正常关闭后 `pgbin → parquet → verify_consistency --table` 五维全值对照：

| 版本 | rows | skipped_invisible | skipped_dead | skipped_toast | 五维 |
|---|---|---|---|---|---|
| 18 | 10000 | 0 | 0 | 0 | PASS |
| 11 | 10000 | 0 | 0 | 0 | PASS |
| 96 | 10000 | 0 | 0 | 0 | PASS |

数据文件：/tmp/opencode/t0325/pg/{18,11,96}/（关闭场景快照）。
证据：poc-consistency-pg{18,11,96}.txt（每份 23 个 PASS）。

## PG 可见性矩阵（AC-2/3/4）
表 `vis_matrix`（PG18，6 类行），pageinspect 核对状态后正常关闭复制：

| lp | id | 类别 | 判定路径 | 预期 | 实测 |
|----|----|------|----------|------|------|
| 1 | 1 | G 基线（SELECT 触发 hint） | infomask(XMIN_COMMITTED=256) | 可见 | 可见 |
| 2 | 2 | A 已提交·无 hint（不触碰） | clog(29251=COMMITTED) | 可见 | 可见 |
| 3 | 3 | B 已提交·有 hint | infomask | 可见 | 可见 |
| 4 | 4 | C DELETE 旧版本 | xmax=29251 committed | 不可见 | invisible |
| 5 | 5 | D UPDATE 旧版本 | xmax=29251 committed, ctid→(0,6) | 不可见 | invisible |
| 6 | 5 | D UPDATE 新版本 | xmin committed | 可见 | 可见 |
| 7 | 6 | F ROLLBACK 中止行 | clog(29252=ABORTED) | 不可见 | invisible |

**pgbin 断言精确命中**：rows=4（预期 4）、skipped_invisible=3（预期 3）、skipped_dead=0（预期 0）。
parquet 内容 == PG 可见行集（id 1,2,3,5 新版本），五维 verify PASS。
证据：pg-visibility-pageinspect.txt / pg-visibility-pgbin.txt / pg-visibility-verify.txt /
pg-visibility-expected.json。

### 构造要点与陷阱（可复用知识）
- `psql -c "A;B;ROLLBACK;"` 多语句共享**一个隐式事务**：串尾 ROLLBACK 会把 A/B 一并回滚
  （T0308 CHECKPOINT 陷阱的又一表现）——ROLLBACK 必须独立 psql 调用。
- `SELECT count(*) WHERE id=3` 走 **index-only scan**，不触碰堆行 → **不设置 hint bit**；
  需 `SELECT *`（或 `SELECT payload`）强制堆访问才触发 XMIN_COMMITTED hint。
- hint bit 是 per-tuple 的：全表扫描会触碰所有行设置 hint；构造"无 hint 行"须避免复制前扫描。

## MySQL 端到端一致性 POC（AC-5）
四版本（56/57/80/84）poc_orders（1,000,000 行），`mysqladmin shutdown` 正常关闭后
复制 ibd → `mysqlbin → parquet → verify_version_convert` 全量逐字段 + 聚合：

| 版本 | 行格式 | rows | 全量逐字段差异 | 聚合 | 吞吐 |
|---|---|---|---|---|---|
| 5.6.51 | COMPACT | 1,000,000 | 0 | PASS | 710K/s |
| 5.7.44 | DYNAMIC | 1,000,000 | 0 | PASS | 742K/s |
| 8.0 | DYNAMIC | 1,000,000 | 0 | PASS | 748K/s |
| 8.4.11 | DYNAMIC | 1,000,000 | 0 | PASS | 584K/s |

证据：mysql-consistency-{56,57,80,84}.txt。schema：56/57 用 `--schema=bench/poc_orders.schema`，
80/84 走 SDI 自动。

## MySQL 可见性矩阵（AC-6）
8.0 场景表（id BIGINT PK, val INT, note TEXT），`mysqladmin shutdown` 正常关闭后复制 ibd，
mysqlbin 过滤 delete-mark（`(page[org-5]>>5)&1`）后与 SQL 可见行逐字段对照
（bench/verify_mysql_scen.py，通用 N 列）：

| 场景 | 内容 | SQL 可见 | parquet | 逐字段差异 |
|---|---|---|---|---|
| V2 | UPDATE 5 + DELETE 5（11 行） | 6 | 6 | 0（更新读最新值，删除行被过滤）|
| V3 | 批量 DELETE 5（10 行） | 5 | 5 | 0 |
| V4 | COMMIT 2 + ROLLBACK 2 + INSERT 2 | 4 | 4 | 0（回滚行 delete-marked 被过滤）|
| V5 | off-page UPDATE（9000B note）| 1 | 1 | 0（物理读最新值）|

证据：mysql-visibility-v{2,3,4,5}-{pgbin,verify}.txt + -visible.tsv。
说明：note TEXT 在 parquet 为 binary（TEXT 属 BLOB 家族），对照脚本需 bytes→utf8 规范化。

## 双链路对比与差距
- **可见性机制**：PG 用 xmin/xmax + hint bit(infomask) + clog（transaction status）判定；
  MySQL 关闭场景下等价于 delete-mark（REC_INFO_DELETED_FLAG）过滤。PG 判定更细（区分
  committed/aborted/in_progress/dead），MySQL 关闭后无"未提交活跃"矛盾。
- **差距（范围外）**：MySQL **未提交活跃事务的 MVCC 可见性**（undo 链/trx_sys 活跃事务表）
  未覆盖——物理直读在数据库运行期间复制时不可见行不一定 delete-marked；此场景需 undo/trx_sys
  解析，另立项。
- PG 的 IN_PROGRESS 判定：pg_tuple_visible 对 clog=IN_PROGRESS 返回不可见（关闭场景下不出现）。

## 为什么"正常关闭"下 undo/trx_sys 与 IN_PROGRESS/ItemIdIsDead 都不需要考虑
**适用前提**：本 POC 的"正常关闭" = 优雅停机——PG `-m smart`（等待事务结束）/`-m fast`
（中止活动事务）后 shutdown checkpoint；MySQL `mysqladmin shutdown`（回滚所有未提交事务）。

- **MySQL（undo/trx_sys）**：关闭流程回滚所有未提交事务，未提交行要么被回滚（带
  delete-mark，物理过滤生效），要么因 `innodb_fast_shutdown=1`（默认）脏页未刷盘而根本
  不在 ibd 文件中。关闭后无活跃会话 → 无 MVCC 快照读旧版本的需求 → undo 链/trx_sys 的
  "活跃事务"信息失去意义。V4 回滚场景实测 PASS 即直接证据。
- **PG（IN_PROGRESS / ItemIdIsDead）**：正常关闭后所有事务在 clog 中要么 committed 要么
  aborted，**不可能出现 IN_PROGRESS** → 该判定分支不会触发。无并发快照引用死行 →
  VACUUM 把死行清理为 unused（lp_flags=0）→ ItemIdIsDead/skipped_dead 不出现（t_dead 实测证实）。
- **边界**：仅**异常关闭**（crash/`kill -9`/`-m immediate`）后直接复制文件才需要这两者——
  此时恢复流程未跑，未提交行残留在文件且无 delete-mark/aborted 标记，MySQL 需 undo+trx_sys
  判定、PG 需 clog IN_PROGRESS 判定。这与"范围外"声明一致。

## 缺口补齐（用户要求二次审查后）
Check 阶段 grill 发现 4 个覆盖缺口，用户选择补齐后再确认，均已完成：

- **(a) MySQL 5.6/5.7/8.4 删除场景复验**：V2/V3 场景在 56/57/84 复跑
  （mysqladmin shutdown → ibd → mysqlbin → SQL 可见行对照），delete-mark 过滤全部正确：
  v2=6/v3=5，逐字段差异 0。**发现并修复 schema 契约缺陷**：InnoDB 列默认可空
  （无 NOT NULL），记录含 null 位图；5.6/5.7 经 `--schema` 时未标 `:null` 会把长度数组
  起点算高 1 字节 → TEXT 长度误读为 0（空串）。8.0/8.4 走 SDI 自带真实 nullable 不受影响。
  修复：bench/poc_scen.schema 补 `:null`。经验沉淀：**--schema 必须如实标注 nullable**。
- **(b) PG dead line pointer（ItemIdIsDead）**：t_dead 8 行删 4 → VACUUM 后 pageinspect 证实
  死行被清理为 unused（lp_flags=0），pgbin rows=4/skipped_dead=0 正确。**正常关闭场景下
  VACUUM 必然清理死行**（无活动快照引用），skipped_dead 分支仅在运行中场景（并发事务引用
  死行）触发——属范围外，代码分支已存在（T0301 引入）。
- **(c) PG FROZEN（VACUUM FREEZE）行**：t_frozen 3 行 VACUUM FREEZE 后
  infomask=XMIN_COMMITTED|XMIN_INVALID(0x0B02)，pgbin rows=3/invisible=0，全值一致 PASS
  （FROZEN 正确判可见，不误判 invisible）。
- **(d) A 类"走 clog"弱证明**：无直接路径探针，由 hint bit=0 推断——已注明为间接证据。

证据：mysql-visibility-{56,57,84}-v{2,3}-verify.txt / pg-frozen-pgbin.txt / pg-dead-pgbin.txt /
pg-frozen-dead-verify.txt。

## 结论
双链路 × 双维度 POC 全 PASS：PG 一致性（三版本）+ 可见性矩阵（6 类行精确断言 + FROZEN +
VACUUM-dead 复验）+ MySQL 一致性（四版本 100 万）+ 可见性矩阵（V2-V5 delete-mark/回滚/
更新 + 5.6/5.7/8.4 删除场景复验）。无生产代码改动；新增 bench/verify_mysql_scen.py +
bench/poc_scen.schema；沉淀 --schema nullable 契约经验。