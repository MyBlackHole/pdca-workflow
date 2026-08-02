# T0197 检查证据（check-evidence）

## AC-1：修改前逐段记录上游锚点

证据：`ac1-source-anchors.md`（实现前撰写）。
- open bucket 守卫语义：`fs/alloc/discard.c:344-347, 433-436, 743`
  `bch2_bucket_is_open_safe()` 跳过 open 桶；engine-local
  `verify_guard_invariants`（engine.rs:688-726，树序扫描 free 桶，
  open 先报 OpenBucketFree、not_rw 次报 NotRwBucketFree）。
- not_rw rw_devs：`fs/alloc/background.c:1650-1667`
  `bch2_dev_allocator_set_rw()` 的 rw_devs bitmap；`background.c:1690-1722`
  `bch2_dev_allocator_remove()` 先标 ro 再等 open write points 排空
  （engine-local `set_device_rw` engine.rs:924-949 以"open 桶存在即 -16"
  表达该等待）；`discard.c:349-357, 654, 871` `bch2_dev_get_ioref()` WRITE
  失败跳过桶。
- open_bucket 为无预校验 insert：engine-local `open_bucket`
  （engine.rs:901）直接插入 open_buckets 集——这是注入式模型的裁决入口。

## AC-2：模型 op 5/6 删除手写守卫预判；open 后模型期望由实现裁决

- op 5 删除 `if state[index] != 0` 预判，改为无条件 `engine.open_bucket(index)`
  + `open[index] = true`；op 6 对称 close。open 结果不再被模型预判，
  由循环尾部 `expect_verdict` 以实现 `verify_all` 的裁决匹配期望
  （合法态 None→Ok；open∧free 报 OpenBucketFree）。
- proptest 反例验证裁决真实生效：`(3,0),(3,0),(5,2),(3,0),(2,2)` 曾暴露
  模型错误（op 3 清除 `open[allocated]`），引擎报 OpenBucketFree 而模型
  期望 None——修复后随机序列（含非法 open free 桶）全程一致。
- `expect_verdict` 失败时先关 open 桶再 panic，防止引擎 drop 时
  open-bucket-leak 断言（engine.rs:1788）掩盖真实消息。

## AC-3：新增 set_device_rw op；not_rw 维度期望与实现裁决一致

- op 7：`index & 1 == 0` 决定 rw/!rw；set false 时 open 桶存在→-16
  （bch2_dev_allocator_remove 等排空语义），否则 Ok 且 `device_rw=false`。
- 期望推导扩展：free 桶树序裁决 open 优先、not_rw 次之
  （NotRwBucketFree），与 verify_guard_invariants（engine.rs:713-722）
  及 verify_all（guard 检查最后执行，无树错误时 guard 错误优先）一致。
- not_rw 语义保留：allocate→-1（engine.rs:807-810 rw 检查先于 data_type
  扫描）；reclaim→-16（engine.rs:980-982）；discard worker EAGAIN 旋转
  （engine.rs:1142-1146 discard_bucket -11 → run_discard_worker 旋转，
  模型 `state==2 && !open && device_rw` 才处理）；queue_discard 无 rw
  检查（engine.rs:1157-1169）保持 Ok。
- 确定性测试 `not_rw_dimension_guard_verdicts_are_implementation_
  adjudicated`：NotRwBucketFree / open 优先 / open 拒绝 set false -16 /
  not_rw allocate is_err / reclaim -16 / worker -11 EAGAIN / reopen 后
  rw_devs 从 devs_online 重建（engine.rs:1687-1700）再分配成功。

## AC-4：随机序列（含非法操作路径）全程模型状态与引擎实际状态一致

- proptest `open_bucket_discard_model_protects_open_from_reuse`（16 cases
  × 1..=40 ops，op 域 0..8）：每步后 alloc 树投影断言（state==2 时
  data_type 必须 NEED_DISCARD）+ verify_all 裁决 + verify_guard_invariants
  裁决 + expect_verdict 全操作路径匹配。
- 3 个模型 bug 由反例定位修复：① op 5 漏更新影子 `open` 数组（期望推导
  脱节）；② op 3 错误清除 `open[allocated]`（open 与 data_type 独立维度，
  allocate_bucket 不查 open_buckets）；③ worker 模型未含 device_rw 条件
  （not_rw 时引擎 EAGAIN 旋转，模型若置 free 将偏离）。
- proptest-regressions/engine.txt 自动记录 4 个历史反例，每次运行重放
  作为回归保障。

## AC-5：库 API 不变

- 生产代码零改动：提交 `2873d52` 全部 hunk 位于 `mod tests` 内
  （engine.rs:3503 起）；复用既有公开 API verify_all /
  verify_guard_invariants / set_device_rw / allocate_bucket /
  reclaim_bucket / queue_discard_bucket / run_discard_worker /
  discover_discard_buckets。

## AC-6：workspace 全量测试、fmt、diff gate

- `cargo fmt` 通过；`cargo test --workspace` 全绿：216 lib + 10
  btree_proptest + 3 fsck_cli = 229；单项 ≤40s（btree_proptest 38.84s，
  AC 上限 1min）。
- 提交：subvol `2873d52`（2 files：engine.rs +242/-35 全在 tests、
  proptest-regressions +3）。

## 结论

六项 AC 全部达成；模型从"预判合法"转为"探索含非法在内的操作并由实现
裁决"，守卫错误名（OpenBucketFree / NotRwBucketFree）与失败语义
（-1/-16/-11）首次被随机序列与确定性 not_rw 场景联合验证。
