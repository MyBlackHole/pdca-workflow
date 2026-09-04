---
schema: pdca.asset/v1
id: ontology:domain/core-snapshot-table-lifecycle-filter-semantics
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-snapshot-table-lifecycle-filter-semantics/1.0.0
summary: 快照表生命周期与过滤语义验证模式
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 snapshot-table-lifecycle-filter-semantics 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 快照表生命周期与过滤语义验证模式

来源：T0209 完成 PDCA（AC-1..AC-4 全收敛，测试一次通过，提交
3302e78）。由 btree 核心完整性盘点（缺口 3：snapshot 遍历语义）
驱动。

## 事实

- iter 侧 filter_snapshots 六步流程完整（iter.rs:2062-2152 对齐
  iter.c:2808-2900：out_of_range → `p.snapshot < iter.snapshot`
  数值快路径 → update_path 释放 → intent 缓存 update_path →
  `bch2_snapshot_is_ancestor` 过滤 → whiteout），但快照表
  （`bch_fs.snapshots.table`）只由事务 trigger
  （`bch2_mark_snapshot`，snapshot.rs:475）填充，**无启动重建路径**。
- 后果：崩溃重开后表空 → ancestor 查询全 false → filter_snapshots
  把所有带 snapshot 的 key 过滤掉。此前 engine 层靠全部
  `BTREE_ITER_all_snapshots` 规避（engine.rs:2419 注释明言
  "must enumerate all snapshots"）——规避而非实现。

## 修复模式（双路径）

- **mark 路径**（实时）：事务提交时 trigger 按 `KEY_TYPE_snapshot`
  分发 `bch2_mark_snapshot(trans, op)` 维护内存表（含 is_ancestor
  bitmap 沿 parent 链构建、WILL_DELETE → `need_delete_dead_snapshots`
  flag）。
- **加载路径**（启动）：`bch2_snapshots_read`（snapshot.rs，对齐
  `snapshots/snapshot.c:783-806`）：`bch2_btree_iter_peek_prev` +
  `bch2_btree_iter_rewind` **反向遍历**（is_ancestor bitmap 需祖先先
  初始化，故从 POS_MAX 起反向），过滤 `KEY_TYPE_snapshot` 后以
  `btree_trigger_op{old: null, new: k, flags: 0}` 复用 mark —— 等价
  上游 801 行 `__bch2_mark_snapshot(trans, id, 0, bkey_s_c_null, k, 0)`
  直接调用（**绕过 trigger dispatch**：域内 `bch2_key_trigger` 会读
  `(*op.old.k).type_`，old 为 null 时是 UB）。
- 挂载点：`attach_persistent_journal` 中 `bch2_journal_replay` 之后、
  派生树重建之前（对齐上游 snapshots_read 于 go_rw 前执行）。

## 过滤语义验证手法

- **快照视图方向**（关键）：`bch2_snapshot_is_ancestor(id, ancestor)`
  = id 是 ancestor 的子孙；id 越大越靠根。iter filter 保留
  `is_ancestor(iter.snapshot, k.p.snapshot)` 为 true 的键 → **视图
  可见祖先链**（view=LEFT 可见 {root, left} 的键，left 子孙的键被
  数值快路径 `p.snapshot < iter.snapshot` 滤除）。
- **快照键自身的 p.snapshot = 0**：filter 模式下被快路径跳过，
  不会误返回；但 `bch2_snapshot_is_ancestor` 有 `assert_ne!(id, 0)`，
  故 **iter 必须 `bch2_btree_iter_set_snapshot` 显式设视图**，且普通
  遍历必须 all_snapshots（engine scan 的既有约束）。
- **端到端验证**：raw 事务写快照键（`encode_key` 只支持
  cookie/deleted，须直接构造 `bkey_i_snapshot` + `trans_update`；
  trans_update 前必须 traverse 使路径 intent 锁定）→ `engine.sync()`
  → drop（崩溃）→ open_persistent → 表逐字段断言 + raw iter
  （`BTREE_ITER_not_extents | BTREE_ITER_snapshot_field` +
  set_snapshot）收集过滤视图，断言崩溃前后一致。
- 域内快照树 id 归属：无 `BTREE_ID_snapshots`（约束 14 豁免），
  快照键混存 id 0，加载按 key type 过滤。

## 边界

- 死快照删除回收（`bch2_delete_dead_snapshots_work`）仍范围外：
  仅保留 `BCH_SNAPSHOT_WILL_DELETE` flag 设置语义。
- 缺口 1（node_scan 全盘扫描重建）与缺口 2（节点级内容检查器）
  仍未排期。
