# PG 可见性判定矩阵与测试构造要点

> 来源：T0325 可见性 POC（records/T0325-0819-pg-poc-consistency-visibility/conclusion.md）

## 背景
物理直读（pgbin）必须复现 PG 可见性：`pg_tuple_visible` 按 xmin/xmax + hint bit
（infomask）+ clog（pg_xact 事务状态）判定行是否可见。本知识总结判定矩阵与
测试构造陷阱，供跨会话复用。

## 判定矩阵（关闭场景）
| 类别 | 记录状态 | 判定路径 | 结果 |
|------|----------|----------|------|
| G/A 已提交行 | xmin committed，hint 有(infomask XMIN_COMMITTED)/无(clog) | 有 hint 走 infomask，无 hint 走 clog | 可见 |
| B 已提交行（触碰过）| XMIN_COMMITTED=0x0100 | infomask 直接判定 | 可见 |
| C DELETE 旧版本 | xmax committed | xmax 链走 clog | 不可见 |
| D UPDATE 旧版本 | xmax committed，ctid 指向新版本 | xmax committed | 不可见 |
| F ROLLBACK 行 | xmin=aborted(clog) | clog=ABORTED | 不可见 |
| FROZEN 行 | infomask=0x0300（COMMITTED\|INVALID）| frozen 视为已提交 | 可见 |
| IN_PROGRESS（运行中）| clog=IN_PROGRESS | 返回不可见（关闭场景不出现）| 不可见 |

实测精确断言示例（PG18）：`rows=4, skipped_invisible=3, skipped_dead=0`。

## 测试构造要点（易踩陷阱）
1. **psql -c 多语句共享一个隐式事务**：串内含 `ROLLBACK`/`BEGIN`/`VACUUM` 会把
   整串回滚或报错。必须拆分为独立 psql 调用（T0308 的 CHECKPOINT 陷阱同源）。
2. **`SELECT count(*) WHERE id=..` 走 index-only scan，不触碰堆行 → 不设置 hint bit**。
   要强制设置 hint 须 `SELECT *`/`SELECT payload`（堆访问）后再触发。
3. **hint bit 是 per-tuple**：构造"无 hint 行"（走 clog 路径）时，复制前不要全表扫描
   （会触碰所有行并设置 hint）。先 SELECT 指定行设置 G 类 hint，其余行保持无 hint。
4. **VACUUM（正常关闭下）**：死行（已提交删除/更新旧版本）被清理为 unused
   （lp_flags=0），`skipped_dead`（ItemIdIsDead）仅在运行中场景（并发快照引用死行）触发；
   正常关闭后 `skipped_dead=0` 是必然正确结果。
5. **VACUUM (FREEZE)**：行 infomask 变为 XMIN_COMMITTED|XMIN_INVALID（0x0300），
   pg_tuple_visible 判为可见（不得误判 invisible）。

## 正常关闭语义（为什么 IN_PROGRESS / ItemIdIsDead 可忽略）
"正常关闭"（PG `-m smart` 等待事务结束 / `-m fast` 中止活动事务 + shutdown checkpoint）后：
- 所有事务在 clog 中要么 committed 要么 aborted，**不可能存在 IN_PROGRESS** → 该判定分支
  不触发（IN_PROGRESS 只在数据库运行期间复制时出现）。
- 无并发快照引用死行 → VACUUM 会把死行清理为 unused，**ItemIdIsDead / skipped_dead 不出现**。
因此正常关闭快照下，可见性判定只需覆盖 committed(hint/clog)/aborted/dead 已提交旧版本三路，
无需 IN_PROGRESS 与 ItemIdIsDead 分支。仅异常关闭（crash/`-m immediate`）后复制才需要这两者。

## 验证方法
- pageinspect：`heap_page_items(get_raw_page('t',0))` 核对 lp/xmin/xmax/infomask，
  与 pgbin 统计断言对照。
- parquet == SQL 可见行集：tsv 导出须 `to_char(created_at,'YYYY-MM-DD HH24:MI:SS.US')`
  （6 位微秒）、`active::int`（1/0）；pgbin parquet bool 列按 1/0 规范化后再比对。
