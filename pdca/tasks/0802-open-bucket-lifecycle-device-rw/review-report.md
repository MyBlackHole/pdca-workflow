# T0192 Review Report

## 审查范围

- 变更：`crates/subvol/src/engine.rs`（+169/-3，仅 1 文件）。
- 意图：drop 泄漏检测、rw_devs 按 devs_online 推导、设备下线拒绝 open 桶（PRD AC-1..AC-6）。

## 标准轴发现

| 严重度 | 位置 | 发现 | 处置 |
|---|---|---|---|
| MEDIUM→已修 | `set_device_rw` | 初版锁序 rw_devs→open_buckets，与 reclaim/discard 的 open_buckets→rw_devs 相反，并发时构成死锁 | 修正为 open_buckets→rw_devs，与 reclaim/discard 一致；修复后相关测试全绿 |
| LOW | `Drop for EngineState` 泄漏检测 | 泄漏检测在 worker join + rcu barrier 之后、free_super 之前，panic 时 free_super 不执行（仅 panic 路径） | 可接受：panic 即进程错误暴露，资源由 OS 回收；测试用 catch_unwind 验证消息并清理文件 |
| 无 | 位图遍历 | devs_online 遍历与上游 for_each_online_member 位图语义一致（dev_mask_nr / bch2_dev_idx_is_online） | — |
| 无 | 错误码 | set_device_rw(false) 拒绝 -16 与 reclaim 守卫同码（live reference 类） | — |
| 无 | 约束 8/13 | 未新增函数名与结构体；位运算内联，无 bcachefs 不存在的 API | — |

Rust 清单：unsafe 无新增（仅测试内既有模式复用）；Poisoned 全处理；测试为行为验证 + catch_unwind 断言。

## 规范轴发现（对照 PRD AC）

- AC-1：ac1-source-anchors.md（bch2_open_buckets_stop fs.c:324/foreground.c:1171-1230、bch2_dev_allocator_set_rw/add/remove background.c:1663-1728、bch2_dev_has_open_write_point background.c:1650-1662、for_each_rw_member_rcu members.h:134-135）。
- AC-2：drop 时 open_buckets 非空 panic（对齐 umount 关闭语义）；close 配对后 drop 正常 + 重启 verify。
- AC-3：rw_devs 初始由 devs_online 推导（attach 时），移除 [0] 硬编码；内存引擎空集、create_persistent 后 {0} 的定向断言。
- AC-4：set_device_rw(dev,false) 有 open 桶拒绝 -16（等待语义非阻塞等价）；清空后可下线，allocate -1 守卫延续。
- AC-5：3 新定向测试 + 既有 discard 属性测试适配（restart/结束 drop 前 close 全部 open 桶——新语义暴露了 T0189 测试自身的泄漏，已修正）。
- AC-6：workspace lib 205/205 + 集成 10/10 + fmt 通过。

## 风险评级

- Blocking = 0。全部通过门禁。
