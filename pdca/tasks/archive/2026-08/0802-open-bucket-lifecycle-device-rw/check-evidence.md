# T0192 Check Evidence

记录：`T0192-0802-open-bucket-lifecycle-device-rw`

## 对照上游源码（AC-1）

- `ac1-source-anchors.md`：bch2_open_buckets_stop（fs.c:324 umount 关闭语义、
  foreground.c:1171-1230）；bch2_dev_allocator_add/set_rw（background.c:1663-1728
  上线即 rw）；bch2_dev_allocator_remove + bch2_dev_has_open_write_point
  （background.c:1650-1722 先置 ro 再停 open 桶并等待清空）；for_each_rw_member_rcu
  （members.h:134-135，rw 设备集合与 online 成员一一对应）。

## 实现证据（AC-2/AC-3/AC-4）

- engine.rs:1660-1673：`Drop for EngineState` 泄漏检测（worker join + rcu barrier
  之后、free_super 之前，open_buckets 非空 panic）。
- engine.rs:1559-1580：attach_persistent_journal 中 configure 后按 devs_online
  位图推导 rw_devs（清除重建，对应 bch2_dev_allocator_add 上线即 rw）。
- engine.rs:494：rw_devs 初始空集（移除 [0] 硬编码）。
- engine.rs:802-826：set_device_rw 锁序 open_buckets→rw_devs（与 reclaim/discard
  一致，防死锁）；false 时该设备有 open 桶拒绝 -16。

## 测试证据（AC-4/AC-5）

- `set_device_rw_false_refuses_open_bucket_on_device`：open 桶存在时拒绝 -16、
  关闭后下线成功、allocate -1、恢复 rw 后 reclaim+discard 成功。
- `rw_devs_initialized_from_devs_online`：内存引擎（无在线设备）rw_devs 空集；
  create_persistent（devs_online.d[0]）后 rw_devs={0}。
- `persistent_engine_derives_rw_devs_from_devs_online`：attach 后 dev 0 rw 可分配，
  set_device_rw(0,false) 后 allocate -1，恢复后可用。
- `drop_detects_unclosed_open_bucket_leak`：catch_unwind 断言 drop panic 消息含
  "open bucket leak"。
- `close_open_bucket_then_drop_is_clean`：close 配对后 drop 正常 + 重启 verify。
- 既有 discard 属性测试适配：restart/结束 drop 前 close 全部 open 桶（新 drop
  语义暴露 T0189 测试自身泄漏，已修正）。

## 门禁证据（AC-6）

- `cargo test --workspace`：lib 205/205（10.18s）、集成 10/10（40.63s）。
- `cargo fmt --all --check` 通过。
- 单元测试单项 < 1s，满足 1 分钟约束。
- 变更范围：仅 crates/subvol/src/engine.rs（+169/-3）。

## 收敛

- convergence 目标 `T0192-0802-open-bucket-lifecycle-device-rw` 全部满足
  （见 convergence-map.json）。
- 审查：review-report.md，0 blocking（MEDIUM 锁序问题已修复并复测）。
