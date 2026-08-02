---
schema: pdca.asset/v1
id: T0189-0802-discard-open-bucket-boundary
phase: check
source_ids: [ac1-source-anchors, ev-ac2, ev-ac3, ev-ac4, ev-ac5, ev-ac6, convergence-map-v2]
---

## 上下文

T0191 建立了多桶 discard worker 的 FIFO 公平性与队列耗尽语义。T0189 补齐
discard 边界上两个缺失的回收守卫：open bucket（in-progress write claim）与
不可写设备。此前 allocate/reclaim/discard 三条路径均不感知这两类状态，属性
模型可构造出 open 桶被转 free 的非法状态。目标：need_discard + journal
boundary + 设备可写 + 无 open/live reference 四条件齐备才允许转 free。

## 假设与结果

| 假设 | 结果 |
|------|------|
| open bucket 拒绝回收（AC-2） | 成立：`open_bucket`/`close_open_bucket` 公共 API（open_buckets: BTreeSet，对应 open_buckets 哈希 foreground.h:274-296）；reclaim 拒绝 -16、discard 拒绝 -11，定向测试通过 |
| 不可写设备拒绝分配与回收（AC-2） | 成立：`set_device_rw`（rw_devs 位图 background.c:1650-1667）；allocate -1、reclaim -16、discard -11（dev_get_ioref(WRITE) discard.c:357-365），定向测试通过 |
| 故障注入无半状态（AC-3） | 成立：TransactionRestart 注入下 reclaim 重试成功；JournalWrite 注入下 flush 失败后索引一致，恢复后 discard 成功；重启持久化引擎 verify 一致 |
| worker 轮转不阻塞就绪桶（AC-4） | 成立：open/not_rw 桶保留队列（-17 重复入队拒绝）、就绪桶被 drain；not_rw 桶轮转、恢复 rw 后成功；open 关闭后 worker 成功 |
| 属性模型验证 open 不复用（AC-5） | 成立：16 cases × 1..=40 op（queue/run/reclaim/allocate/flush+重启重建/open/close），影子状态机逐 op 对齐；不变量：open 桶不得转 free、state==2 必须 NEED_DISCARD；首版失败输入 [(5,0)] 修正模型（free 桶不可 open），0.69s |
| 门禁全绿（AC-6） | 成立：6 定向 + 200 lib + 10 集成 + fmt 通过，单文件 +405 行 |

## 分析

1. **实现与上游对齐**（约束 3/10/12）：open 判定 ← `bch2_bucket_is_open_safe`
   跳过 open 桶（discard.c:344-347/433-436/743，foreground.h:274-296）；设备
   可写 ← `bch2_dev_get_ioref(WRITE)`（discard.c:357-365）与 rw_devs 位图
   （background.c:1650-1667）。未新增 bcachefs 不存在的结构体（BTreeSet 对应
   open_buckets 哈希/rw_devs 位图）。
2. **检查顺序对齐**：discard_bucket 的 open/可写检查置于 journal_seq 检查之后、
   reclaim 调用之前；reclaim_bucket 的检查置于位置校验之后、backpointer 副作用
   之前，与上游「先验证状态、再转 free」的执行顺序一致。
3. **错误码语义**：reclaim 拒绝 = -16（live reference 类）、discard 拒绝 = -11
   （未就绪轮转类）、allocate 拒绝 = -1（设备无效类），与既有错误码体系一致，
   可被调用方区分重试与硬失败。
4. **测试边界**（grill round 6）：设备可写为设备级状态，`set_device_rw(0,false)`
   影响 dev 0 全部桶，故「open+ready 同设备」与「not_rw 轮转」拆分为两个定向
   测试；属性测试中 open 仅允许作用于非 free 桶（模型与引擎共享的不变量）。
5. **审查修正**（A4 双轴）：初版属性模型允许对 free 桶 open，minimal 输入
   [(5,0)] 暴露模型缺陷而非引擎缺陷；修正模型限制后通过。代码侧无 blocking
   发现；两项 LOW 观察（rw_devs 初始 [0] 硬编码、open_bucket 不校验位置）作为
   技术债记录，不影响收敛。

## 适用边界

- engine-local 单 Mutex 模型：open/rw 守卫为内存态判定，不涉及真实设备热插拔
  或 I/O 队列中段撤销 open 的场景。
- open_buckets 为显式公共 API：调用方负责 open/close 配对；close 未配对不会
  由引擎自动清理（与 bcachefs open 桶随事务提交释放的机制不同，engine-local
  语义）。
- 单格式版本：不涉及旧格式迁移。
- 约束 14 豁免范围内：本任务未涉及 btree id 编号变更。

## 下一轮建议

- 若引入真实设备 I/O 或多设备拓扑，需将 rw_devs 初始化改为按 sb 成员推导，
  并为 open/close 配对增加泄漏检测（drop 时校验）。
- 可将「open/not_rw 桶不转 free」提升为公开断言工具，供后续 allocator
  变体复用（与 T0191 建议合并）。
