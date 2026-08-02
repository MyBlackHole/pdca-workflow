---
schema: pdca.asset/v1
id: T0192-0802-open-bucket-lifecycle-device-rw
phase: check
source_ids: [ac1-source-anchors, E-T0192-CHECK-001, convergence-map]
---

## 上下文

T0189 引入了 open_buckets/rw_devs 守卫，但 rw_devs 硬编码 `[0]`、open/close
未配对静默容忍、设备下线无守卫。T0192 承接这两项技术债并补齐设备下线语义：
上游 bcachefs 在 fs 只读/销毁时关闭全部 open buckets（bch2_open_buckets_stop，
fs.c:324），设备上线/下线分别走 bch2_dev_allocator_add/set_rw 与 remove
（background.c:1663-1728），remove 等待 open write point 清空。

## 假设与结果

| 假设 | 结果 |
|------|------|
| drop 时未配对 open 桶视为泄漏（AC-2） | 成立：Drop for EngineState 在 worker join + rcu barrier 后、free_super 前检查 open_buckets 非空即 panic（对齐 umount 关闭语义）；close 配对后 drop 正常 + 重启 verify 一致 |
| rw_devs 初始按 sb 推导（AC-3） | 成立：attach 时按 devs_online 位图清除重建（对齐 bch2_dev_allocator_add 上线即 rw）；内存引擎空集、create_persistent 后 {0} 的定向断言；[0] 硬编码移除 |
| 设备下线有 open 桶拒绝（AC-4） | 成立：set_device_rw(dev,false) 时该设备仍有 open 桶返回 -16（对齐 remove 先置 ro 再等待清空）；关闭后下线成功、allocate -1 延续 |
| 属性模型适配新语义（AC-5） | 成立：T0189 属性测试 restart/结束 drop 前 close 全部 open 桶——新 drop 语义正确暴露了旧测试自身的泄漏 |
| 门禁全绿（AC-6） | 成立：3 新定向 + 205 lib + 10 集成 + fmt 通过，单文件 +169/-3 |

## 分析

1. **实现与上游对齐**（约束 3/10/12）：drop 泄漏检测 ← `bch2_open_buckets_stop`
   umount 关闭语义（fs.c:324，foreground.c:1171-1230）；rw_devs 推导 ←
   `bch2_dev_allocator_add` 上线即 set_rw(true)（background.c:1723-1728）与
   rw_devs 位图遍历（members.h:134-135 for_each_rw_member_rcu）；设备下线拒绝 ←
   `bch2_dev_allocator_remove` 先置 ro 再等待 open write point 清空
   （background.c:1690-1722，bch2_dev_has_open_write_point 1650-1662）。
2. **审查修正**（A4 双轴）：初版 set_device_rw 锁序为 rw_devs→open_buckets，
   与 reclaim/discard 的 open_buckets→rw_devs 相反，并发时构成死锁；修正为
   统一 open_buckets→rw_devs 后复测全绿。
3. **测试边界**（grill round 8）：泄漏检测 panic 路径 free_super 不执行——
   panic 即进程错误暴露，资源由 OS 回收；测试用 catch_unwind 断言消息并清理
   文件，避免 /tmp 残留。
4. **性能 trade-off**：attach 时一次 O(devs_online) 位图遍历（256 位上限），
   冷路径可忽略；set_device_rw 每次两次 Mutex lock（低频管理操作）。

## 适用边界

- engine-local 单 Mutex 模型：设备下线拒绝是等待语义的非阻塞等价，不模拟
  真实 I/O 中段撤销或热插拔。
- drop panic 不可恢复：面向测试与调用方配对契约，release 行为相同。
- 单格式版本：不涉及旧格式迁移。
- 约束 14 豁免范围内：本任务未涉及 btree id 编号变更。

## 下一轮建议

- 若引入多设备拓扑：rw_devs 推导已按 devs_online 就绪，需补多设备成员的
  定向测试（当前引擎固定单设备，推导路径仅 dev 0 覆盖）。
- 「open/not_rw 桶不转 free」「drop 无泄漏」不变量可提升为公开断言工具，
  与 T0189/T0191 建议合并为 worker 守卫断言套件。
