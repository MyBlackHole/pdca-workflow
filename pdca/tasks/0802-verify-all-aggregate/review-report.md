# T0194 Do 阶段双轴代码审查报告

## 审查范围

- `crates/subvol/src/engine.rs`：新增 `verify_all()`（engine.rs:742-775），
  35 处测试断言切换（22 处 verify_bucket_indexes + guard + 属性测试 2 处），
  3 个新定向测试。
- diff：+136/-32，单文件。

## 轴一：上游语义对齐（对照本地 bcachefs-tools）

| 检查点 | 结论 |
|--------|------|
| 全部执行 + 首个错误优先 ↔ `__bch2_run_explicit_recovery_pass(...) ?: ret`（recovery.c:68-98） | ✅ 一致：每个校验都运行，`first_err.get_or_insert` 保留首个错误（C `?:` 语义的 Rust 等价） |
| 执行顺序 ↔ pass 依赖序（passes_format.h:55-98） | ✅ 一致：拓扑→派生状态→桶索引→守卫；check_allocations 依赖 check_topology 位，拓扑最基础 |
| 拓扑校验覆盖范围 ↔ check_topology 遍历全部 btree | ✅ 一致：遍历 0..BTREE_ID_NR 中 root 非空（live）的 btree |
| 单校验 API 行为 | ✅ 未改动，仅新增聚合入口；verify_bucket_indexes/guard 保持独立可调用 |
| 错误类型 | ✅ 复用 EngineError，无新变体新码 |

## 轴二：安全与并发

| 检查点 | 结论 |
|--------|------|
| 锁 | ✅ verify_all 不跨调用持锁：live_btrees 快照在局部作用域锁内获取并释放，四个校验各自 lock_fs；无死锁、无重入问题 |
| root 判断 TOCTOU | ✅ 快照式判断 + 校验自身只读，与 verify_bucket_indexes 既有风格一致；单线程测试下无并发写 |
| 越界安全 | ✅ `BtreeId::new(id as u8).expect`：id ∈ 0..BTREE_ID_NR 保证 new 不失败（new 仅 id >= NR 报错） |
| 测试构造 | ✅ 多失败验证：need_discard 索引坏（桶索引失败）+ open∧free（守卫失败）→ 返回首个（NeedDiscardSet），验证顺序正确性与全部执行 |

## 发现（非问题）

- `discard_worker_requires_rw_device` 在 not_rw 非法态（free 桶在 not_rw
  设备）断言 verify_all 会失败——该状态是测试故意构造的非法态，守卫
  断言必然触发，故该点保留为 verify_bucket_indexes 单校验（正确）。

## 结论

0 blocking，0 MEDIUM，0 LOW。实现与上游 pass 驱动语义、既有锁序完全一致，
可进入 Check。
