---
schema: pdca.asset/v1
id: ontology:domain/core-btree-random-op-consistency-proptest-pattern
type: domain
layer: Knowledge
status: active
summary: btree 随机操作序列一致性属性测试模式（多 btree id）
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
  testable_signal: "检查本文件 btree-random-op-consistency-proptest-pattern 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# btree 随机操作序列一致性属性测试模式（多 btree id）

来源：T0208 完成 PDCA（AC-1..AC-4 全收敛，测试一次通过）。

## 事实

engine 层 `BtreeId` 支持任意 id（0..BTREE_ID_NR=9，types.rs），
`verify_all` 遍历全部 live btree（engine.rs:807），但测试长期只
用 DEFAULT(0)。T0208 补齐三缺口：多 id 隔离、拓扑变更
（split/merge）、崩溃重开。

## 属性测试模式

- **多 id shadow 模型**：`Vec<BTreeMap<KeyPosition, BtreeKey>>`
  每 id 一个；随机序列 `(id, kind, pos)` 逐操作同步；逐步
  **全量**比对 `scan(id) == model[id]`（同时验证扫描有序性与
  id 隔离：操作只改目标 id 模型，其余 id 模型不变即 scan 不变）。
- **确定性伪随机**：固定 seed + xorshift（`state ^= state<<7 /
  >>11 / <<9`），保证可复现（T0204 merge_random 同模式）。
- **拓扑变更触发**：768 键分批 16/事务触发多层 split；交错
  删除 3/4 触发前台 merge。批大小约束：路径池
  BTREE_ITER_INITIAL=64（每 update 持路径引用）+ 避开叶容量
  64 谐振（批 32 + split 后半叶 32 = 恰好填满 → 无限 split
  重放）。merge 的 restart（-4）由 commit 循环透明处理，
  物理布局对逻辑模型不可见。
- **崩溃重开**：`drop(engine)` 不 flush = 模拟崩溃（StorageEngine
  无 Drop 隐式 flush）；`open_persistent` 重放已 durable 记录
  （未 flush 事务丢弃，T0201 语义）；已同步部分必须全部恢复，
  重开后继续追加操作仍一致。sync 操作用 put_sync/delete_sync
  （journal durable 后返回）。

## 适用条件

- 新增 btree 操作逻辑（split/merge/rewrite/新 btree id 类型）后
  回归一致性。
- 崩溃/恢复语义变更时验证重放完整性。

## 边界

- 本模式验证**最终状态一致性**（scan/verify），不验证中间
  物理布局（由 topology/深度断言补充，T0204 模式）。
- io 层读盘/重写（T0206/07）与并发交错（T0199）为独立覆盖。
