# T0255 PRD：durable segment wire 与 receipt

## 输入与边界

消费 T0253 定义的 immutable sealed segment。负责 wire capability、幂等 apply、durable receipt、cursor 和 partial 隔离；不实现源端枚举、对象存储、GC 或 restore。

## 实现范围

- 以 `(transfer_id, shard_id, segment_id, batch_id)` 为幂等键，版本化编码并协商新 capability。
- 严格模式在数据/目录依赖和 receipt 达到声明 durability 后 ACK；本地 cursor 只接受该模式 receipt。
- 目录 metadata、硬链接 group、空目录、特殊文件和 deletion mark 使用可恢复 segment record。
- partial 元数据绑定 protocol、transfer/run、目标 generation、canonical path、源 identity、长度和 verified offset。
- receipt 只确认下层 storage 已声明 durable 的 object/pack 与 manifest range；最终 ref 发布由 T0258 负责。

## 验收标准

- [ ] AC-1: ACK 前、data sync 后 receipt 前、receipt sync 后 cursor 前、final generation 前崩溃均有确定恢复结果且不漏文件。
- [ ] AC-2: 重放及乱序 batch 不重复应用副作用；receipt 损坏、错误 durability 或 identity 冲突均 fail-closed。
- [ ] AC-3: 目录元数据不随 checkpoint 重放全部历史，硬链接 first-path/group 可由 durable record 重建。
- [ ] AC-4: 旧 transfer、错误目标、损坏 metadata、路径或源 identity 冲突时 partial 不得复用。
- [ ] AC-5: 中断任务不产生 final publication receipt；普通 batch receipt 不得被解释为 generation 已发布。
- [ ] AC-6: receipt 绑定 target generation、segment digest、record range/count、payload bytes、protocol 和 durability；同 key 不同内容返回冲突。
- [ ] AC-7: 每 shard 串行提交，或用 contiguous high-watermark 加 gap set 防止乱序 ACK 越过未提交 batch。
- [ ] AC-8: 新 repository wire 与 legacy in-place mirror 使用独立 capability 和 frame/state domain，receipt 不得跨模式复用。
- [ ] AC-9: hardlink anchor 跨 shard 先提交，父目录 metadata 后提交；依赖失败有确定降级或 generation failure。
- [ ] AC-10: receipt/policy digest 绑定 effective `resume` 配置；本地 `metadata_index` 开关不进入 wire identity，也不能改变 receipt 的幂等结果。
- [ ] AC-11: `resume=off` 不协商 batch resume receipt、partial 或 cursor；immutable object dedup 响应使用独立类型和指标。

## 声明的测试接缝

- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp
