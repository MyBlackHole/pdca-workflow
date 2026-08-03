# T0208 Check 证据：btree 随机操作序列一致性属性测试

任务：T0208-0803-btree-random-op-consistency

## AC-1：多 id 隔离与扫描一致性

- 测试：`multi_btree_random_operations_preserve_per_id_models`
  （engine.rs tests）。
- 设计：3 seeds × 256 步 × 4 btree id（0..4）确定性伪随机
  put/delete；每步后**全量**比对 4 个 id 的 `scan(id)` 与
  shadow BTreeMap（有序内容逐值相等）+ `get` 命中；操作只改
  目标 id 模型 → 其余 id 不变即隔离性；结束 `verify_all()`
  （engine.rs:807 遍历全部 live btree）。
- 结果：通过。验证扫描有序性（bch2_btree_iter 顺序遍历）与
  id 隔离（每 btree 独立 root，bch2_btree_id_root）。

## AC-2：拓扑变更一致性

- 测试：`multi_btree_topology_changes_preserve_all_models`。
- 设计：4 个 id 各写入 768 键（分批 16，避开路径池
  BTREE_ITER_INITIAL=64 约束与叶容量 64 谐振）触发多层
  split（T0174 模式）；随后交错删除 3/4（分批 16）触发
  前台 merge（T0204 模式）→ `verify_all` + 4 id 全量比对。
- 结果：通过。

## AC-3：崩溃重开一致性

- 测试：`multi_btree_random_sequence_survives_crash_reopen`。
- 设计：随机 sync 序列（put_sync/delete_sync，journal durable
  后返回）→ 随机步数（64..160）`drop(engine)`（StorageEngine
  无 Drop 隐式 flush = 模拟崩溃）→ `open_persistent` 重开
  （journal 重放已 durable 记录，T0201 语义：未 flush 事务
  丢弃）→ `verify_all` + 4 id 全量比对（已同步部分必须全部
  恢复）→ 重开后继续 64 步随机追加操作再比对。
- 结果：通过。

## AC-4：门禁

- `cargo test --lib`：247 passed; 0 failed（10.61s < 1min）。
- `cargo fmt --check`：干净。
- diff gate：仅 engine.rs tests 模块（+187 行，3 测试），
  commit 7889482；生产逻辑零改动。

## 结论

全部 4 项 AC 收敛。测试一次通过（无修复需求），属性测试
补齐多 btree id 隔离/拓扑变更/崩溃重开三缺口。
