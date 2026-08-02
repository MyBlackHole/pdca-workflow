# T0194 Triage Brief

## 分类

- 类型：enhancement
- 场景：development
- 父任务：T0193

## 本地源码核验

- `fs/init/passes_format.h:55-98`：recovery passes 按依赖序逐个执行
  （check_topology → check_allocations → check_btree_backpointers → ...），
  每个 pass 带 PASS_FSCK_ALLOC/PASS_ONLINE 等标记。
- `fs/init/recovery.c:72/118/151`：`__bch2_run_explicit_recovery_pass` 是
  pass 驱动的批量执行入口——`bch2_run_recovery_passes`（passes_format.h
  BOOTSTRAP_JSET 序列）按序运行所有 required passes，任一失败即报错。
- engine-local 现状：`verify`（engine.rs:586，拓扑）、`verify_derived_state`
  （engine.rs:618，物理指针↔backpointer）、`verify_bucket_indexes`
  （engine.rs:624，alloc↔freespace/need_discard）、`verify_guard_invariants`
  （engine.rs:688，open/not_rw 守卫）四个校验分散，测试中 29 处逐点调用。

## 查重

T0193 disposition/结论建议「verify_guard_invariants 与 verify_bucket_indexes
合并为单一 verify_all 入口（对齐 check_allocations + check_btree 双 pass
聚合）」；无同范围活动任务。verify_all 语义对应 recovery pass 驱动批量
执行（recovery.c），非上游单一函数，属 engine-local 组合入口（AGENTS.md
允许 Rust API 按需设计，需语义依据——pass 驱动序列即依据）。

## 推荐

新增 `verify_all()`：内部按固定顺序依次调用四个校验（拓扑→派生状态→
桶索引→守卫），任一失败即返回首个错误（pass 序列的 fail-fast 语义）；
内部各校验保持独立可单独调用；既有 29 处测试断言切换为 verify_all。
范围外：不新增校验逻辑、不改变单个校验行为、不实现修复/repair 路径。
