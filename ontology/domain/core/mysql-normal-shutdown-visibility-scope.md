---
schema: pdca.asset/v1
id: ontology:domain/mysql-normal-shutdown-visibility-scope
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/mysql-normal-shutdown-visibility-scope/1.0.0
summary: MySQL 正常关闭场景可见性范围（为什么不需要 undo/trx_sys）
domain:
- ontology:domain/mysql
relations:
  specializes:
  - ontology:domain/mysql
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# MySQL 正常关闭场景可见性范围（为什么不需要 undo/trx_sys）

> 来源：T0325 可见性 POC（records/T0325-0819-pg-poc-consistency-visibility/conclusion.md）

## 背景
物理直读（mysqlbin）判断可见性靠过滤 delete-mark（REC_INFO_DELETED_FLAG 0x20）。
为何不用 undo 链 / trx_sys（活跃事务表）？答：本工具适用场景限定**正常关闭**。

## 正常关闭（mysqladmin shutdown）后发生了什么
- 关闭流程**回滚所有未提交事务**：未提交行要么被回滚（带 delete-mark，物理过滤即生效），
  要么因 `innodb_fast_shutdown=1`（默认）脏页未刷盘而**根本不在 ibd 文件中**。
- 关闭后无活跃会话 → 无 MVCC 快照读旧版本的需求 → undo 链 / trx_sys 的"活跃事务"信息失去意义。
- 已提交删除/更新旧版本的行带 delete-mark（purge 未跑完也不影响，标记仍在）。

## 结论
正常关闭快照下，**可见行 = 无 delete-mark 的行**；不需要解析 undo/trx_sys。
V2-V5 场景矩阵（更新/删除/回滚/off-page 更新）与 56/57/80/84 四版本复验均以此成立。

## 边界（需要 undo/trx_sys 的情形）
- 数据库**运行期间**直接复制数据文件（活跃事务可能写入未提交行且无 delete-mark）。
- **异常关闭**（crash / kill -9）后未执行恢复流程：文件里残留未提交行，需 undo 链判定
  哪些行属于已中止事务。此类场景需另立项（解析 undo 段 + trx_sys 活跃事务列表）。

## 关联
- PG 侧对应结论见 ontology/domain/pg/visibility-clog-infomask.md（IN_PROGRESS / ItemIdIsDead
  在正常关闭下同样不出现）。