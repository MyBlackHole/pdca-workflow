# T0197 双轴代码审查报告（review-report）

审查范围：subvol 提交 `2873d52`（engine.rs tests 模块改造：
ModelEngine 注入式模型 + op 7 set_device_rw + not_rw 维度建模 +
确定性测试；proptest-regressions +3 反例）。

## A 轴：上游语义对齐

| 检查点 | 上游锚点 | 本实现 | 结论 |
|---|---|---|---|
| open 桶守卫（裁决入口） | discard.c:344-347, 433-436, 743 `bch2_bucket_is_open_safe()` skip open 桶 | open_bucket 无预校验 insert（engine.rs:901）；裁决交给 verify_all / verify_guard_invariants（engine.rs:688-726，树序 open 先于 not_rw） | 对齐 |
| set_device_rw rw_devs | background.c:1650-1667 `bch2_dev_allocator_set_rw()`；remove 时等 open write points 排空（1690-1722） | engine.rs:924-949：open 桶存在→-16（以拒绝表达等待），锁序 open_buckets→rw_devs | 对齐 |
| not_rw 失败语义 | discard.c:349-357, 654, 871 `bch2_dev_get_ioref()` WRITE 失败 | allocate -1（engine.rs:807-810）、reclaim -16（980-982）、worker EAGAIN 旋转（1142-1146） | 对齐 |
| rw_devs 重建 | devs_online 派生（open_persistent engine.rs:1687-1700） | 模型 op 4 reopen 后 device_rw 重置 true，确定性测试验证再分配成功 | 对齐 |
| 无新增行为分支 | — | 生产代码零改动（diff hunk 全在 `mod tests`）；仅测试断言 | 符合约束 8/12 |

## B 轴：安全/健壮性

- panic 掩盖防护：ModelEngine 用 `Option<StorageEngine>` + Drop 关桶，
  反例失败时先 `expect_verdict` 关桶再 panic——open-bucket-leak 断言
  （engine.rs:1788）不再遮蔽 prop_assert 消息（实测反例输出真实错误名）。
- 模型/实现状态脱节防护：影子 `open`/`queued`/`device_rw` 与引擎状态
  每步经 expect_verdict 双裁决（verify_all + verify_guard_invariants）
  强制一致；op 4 重开后从 alloc 树重新投影（含 need_discard 恢复入队）。
- 反例闭环：3 个模型 bug（影子数组漏更新、allocate 清 open、worker 缺
  device_rw 条件）均由 proptest 最小反例定位修复，回归文件自动保存
  4 个反例重放。
- 测试资源：prepared_bucket_engine 唯一命名 + 每测试 drop + remove_file；
  确定性测试无时序依赖。
- 无 panic 新增路径；锁序/错误处理未触碰生产代码。

## 结论

两轴通过；0 blocking / 0 MEDIUM / 0 LOW。残留：lib 既有 never-used
警告（bkey.rs MAX_VERSION、interior.rs unused imports，非本次引入）。
