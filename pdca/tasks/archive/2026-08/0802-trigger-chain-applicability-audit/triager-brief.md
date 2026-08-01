# T0179 分诊简报

## 分类

- 类别：review
- 场景：review
- 优先级：P2（事务一致性前置语义核验）

## 已核验事实

1. 本地 bcachefs `fs/btree/commit.c:507-656` 把 trigger 分为 atomic、
   transactional 与 GC 三个阶段；transactional 阶段可追加 update，并循环至同一
   sort order 的 insert/overwrite 均执行完毕。
2. 该 transactional 阶段只对 `btree_node_type_has_trans_triggers()` 为真的
   btree node type 执行；GC 阶段也以 `btree_node_type_has_triggers()` 和 GC
   visited 位置为前提，不能脱离键/树类型直接移植。
3. subvol `btree/update.rs:1995-2055,2294-2301` 仅将
   `KEY_TYPE_snapshot` 视为有 trigger 的键，并在 commit write-locked 路径运行
   atomic trigger；`insert_trigger_run` / `overwrite_trigger_run` 已存在但当前没有
   transactional runner 消费它们。
4. 外部 API 的普通 put/delete 在 `engine.rs:1152-1162` 只编码
   `KEY_TYPE_cookie` 或 `KEY_TYPE_deleted`；因此不能仅因 runner 缺失就断言普通
   数据路径遗漏语义。
5. T0178 已确认不可将依赖 bcachefs fs 层 btree-id/type 合约的校验直接施加到
   subvol；该边界同样适用于本项 trigger 链判断。

## 去重

- 已搜索 active/archive task 和 knowledge：没有 transaction/gc trigger
  applicability 的进行中或已归档任务。
- T0168 的完整性审计将 D3 列为待排期差距，但未完成当前独立键类型的逐项适用性
  证明；本任务补足该证据，不重复 journal 布局校验或 D1 空间检查修复。

## 推荐

先完成有界审计：为当前实际可写的 `cookie/deleted/snapshot` 键及相关内部 btree
路径，逐项判定 bcachefs transactional/GC trigger 是否适用、已实现还是确有缺口。
若确认存在适用且缺失的语义，只创建带最小范围和源码锚点的后续 bugfix 任务；不在
本审计中直接移植整条 fs 层 trigger 链。
