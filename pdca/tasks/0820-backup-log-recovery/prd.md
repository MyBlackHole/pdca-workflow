# T0333 PG/MySQL 备份产物日志恢复一致性调研（PRD）

## 问题

备份出来的 PostgreSQL / MySQL 数据文件，在**非正常关闭（在线备份/运行中复制/异常退出）**场景下
存在**数据不一致**：数据页可能含未刷盘/部分写的已提交修改、以及未提交事务的行。T0325 已把该
场景划为现有物理直读（mysqlbin/pgbin）的**范围外**（记录于
`knowledge/mysql/normal-shutdown-visibility-scope.md` 与 `knowledge/pg/visibility-clog-infomask.md`）：
直接直读会得到错误/漏读结果。

现有工具链假设的是**正常关闭快照**（无未提交事务、可见行=无 delete-mark / clog aborted）。
因此备份产物必须先经**日志恢复**到"等价正常关闭快照"，才能复用既有工具链转换 Parquet。

核心待答问题：**有齐全的日志文件（MySQL redo log / PostgreSQL WAL）时，如何把不一致的备份数据
恢复到一致状态？**

## 目标

- **核心价值 = 路径 B（自研离线重放）**（用户 Q9 决策：A 借力工具显然可行无需调研，B 才有价值）。
  产出 B 的**完整技术方案设计**（research，不写实现代码）：
  - 恢复起点定位（MySQL：checkpoint LSN / 页 LSN 对比；PG：pg_control + checkpoint）
  - 前滚（MySQL：redo 物理前滚已提交修改；PG：WAL REDO 重放已提交修改）
  - 回滚/可见性（MySQL：undo 回滚未提交事务 + trx_sys 活跃事务；PG：WAL 重放后 clog 标记
    aborted，未提交行不可见）
  - 一致性校验（恢复后与 SQL 全量对照 / 现有 verify 工具复用）
- **路径 A（借力现有工具）仅作对照基线与最终衔接工具链的备选**，不展开调研。
- 明确与既有工具链（mysqlbin/pgbin + T0325 可见性）的衔接方式
- 用**容器构造**在线备份样本验证关键假设（PG 优先）

## 方案方向

1. **恢复一致性目标态 = 等价正常关闭快照**（用户 Q7 决策）：可见行 = 已提交行；未提交行
   aborted/回滚。复用 T0325 可见性逻辑即可衔接工具链。
2. **双平台覆盖，PG 优先**（用户 Q6 决策）：PG 无独立 undo（MVCC 元组 + clog 标记 aborted），
   复杂度低；MySQL 需 redo 前滚 + undo 回滚 + trx_sys，复杂度高。
3. **B 产出为 research 技术方案设计**（用户 Q10/Q11 决策）：解析器架构、前滚/回滚算法、
   pg_control 与 undo 依赖、风险清单、工程量评估；A 作对照基线。

## 验收标准

- [ ] AC-1: 恢复方法论文档完成：覆盖 MySQL 与 PG 的恢复起点定位、redo/WAL 前滚、undo 回滚 /
  clog aborted 判定、一致性校验，每环节含机制说明与适用版本
- [ ] AC-2: **路径 B 技术方案设计**完成：解析器架构、前滚/回滚算法、pg_control 与 undo/trx_sys
  依赖分析、风险清单、工程量评估（复杂度 S/M/L）；A 作对照基线备选
- [ ] AC-3: PG 容器验证：构造非正常关闭（运行中复制 / 异常退出）备份样本 + 齐全 WAL → 恢复
  到一致态 → pgbin 转换 parquet → 与 SQL 对照行数/字段一致（PASS）
- [ ] AC-4: MySQL 容器验证（若可复现）：构造在线备份产物 + 齐全 redo → 恢复到一致态 →
  mysqlbin 转换 parquet → 与 SQL 对照一致；若 undo/trx_sys 缺口阻塞则记录边界
- [ ] AC-5: 衔接说明：恢复后产物输入既有 mysqlbin/pgbin 的调用方式、可见性契约、已知限制文档化
- [ ] AC-6: research-report + evidence 登记 + 结论（B 自研离线重放是否值得立项实现的建议）

## Seam 分析

（research 场景，无测试产物，跳过 P3.5 测试接缝；验证实验以证据形式登记）

## 范围外

- 恢复引擎实现（自研 redo/WAL 重放代码）——仅技术方案设计
- Oracle（T0329 另立）
- 真实生产备份产物（环境无样本，用容器构造）
- 增量/CDC、PITR 时间点恢复
- TDE 加密备份产物的恢复

## 备注

- 复用资产：`knowledge/backup/xtrabackup-incremental-schemes.md`（XtraBackup 机制，A 路径参考）、
  `third_party/pg184`（PG 源码，clog/heap 已有）、本地 `/home/black/Documents/percona-xtrabackup`
  （redo 恢复参考实现源码，B 方案设计参考）。
- 既有容器：t0216-pg（PG18）、t0301-pg96/pg11、t0250-mysql56/57/80/84 可用于构造备份样本。
- 待确认事实：本机 xtrabackup 树是否含完整 redo 恢复（log0recv）；PG 恢复是否需要完整
  pg_control/checkpoint 文件集。