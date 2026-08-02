---
schema: pdca.asset/v1
id: T0191-0802-discard-worker-fairness-property
phase: check
source_ids: [ac1-source-anchors, E-T0191-CHECK-001, convergence-map]
---

## 上下文

T0190 建立了单桶 discard worker 的 EAGAIN 重试 seam 与 `run_discard_worker_once`
公共 API。T0191 将其扩展到多桶场景：队列此前为 BTreeSet（提交无序），单个
未就绪桶会阻塞后续就绪桶的处理。目标是为 discard worker 引入确定性 FIFO
公平性，并用属性测试验证并发/重启收敛。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 多桶提交按 FIFO 顺序处理，公平不饿死（AC-2） | 成立：`discard_inflight` 改为 `Mutex<(VecDeque, BTreeSet)>`，提交 push_back 对应 darray；FIFO 定向测试通过 |
| EAGAIN 桶轮转队尾不阻塞就绪桶（AC-3） | 成立：就绪桶被处理、未就绪桶保留队列且返回 -11；轮转定向测试通过 |
| 并发 queue + 单 worker 收敛、重启后重新发现（AC-4） | 成立：4 线程 Barrier 并发 queue + 单 worker 一次 run 全部处理；restart 后 discover 重新入队（回归） |
| 属性测试模型与引擎公共 API 一致（AC-5） | 成立：16 cases × 1..=40 op 交错（queue/run/reclaim/allocate/restart），影子状态机逐 op 对齐，每 op 后索引验证通过，0.89s |
| 门禁全绿（AC-6） | 成立：6 定向 + 194 lib + 10 集成 + fmt 通过 |

## 分析

1. **实现与上游对齐**（约束 3/10/12）：while-直到耗尽 ← `bch2_do_discards_fast_work`
   while(1)（discard.c:605-633）；FIFO darray push ←
   `bch2_fast_discard_bucket_add`（discard.c:643-655）；EAGAIN 轮转不阻塞 ←
   主路径 advance 跳过继续遍历（discard.c:478-491）。未新增 bcachefs 不存在的
   结构体（VecDeque/BTreeSet 为 std 容器对应 darray/in_flight 集合）。
2. **审查修正**：A4 双轴审查发现初版 run_discard_worker 为「快照单轮」——
   与 PRD「while 直到耗尽」语义不符，run 期间并发新提交的桶会被漏到下一轮。
   修正为严格耗尽语义（全成功继续循环，deferred 立即返回 -11），修正后全部
   测试重跑通过。
3. **测试边界**（grill round 5）：并发定向测试是「queue 全部完成后 run」，
   未直接覆盖「run 执行期间新提交」的交错路径（无 hook 时难以确定性断言）。
   该路径由 while-耗尽循环承担，属性测试的「run 后队列空」不变量 +
   queue/run 交错 op 序列从模型层兜底。
4. **性能 trade-off**：每桶处理多次短暂 Mutex lock（pop/push/remove 分离）——
   引擎为单 Mutex 模型、discard 为低频后台路径，不构成热点；EAGAIN 轮转最坏
   一次 pass 后返回 -11，无无限循环风险。

## 适用边界

- engine-local 单 Mutex 模型：worker 与用户线程的公平性验证不涉及真实设备
  I/O 队列、多设备并行或 journal 提交延迟变化。
- 「run 期间新提交」交错路径无确定性定向测试（见分析 3）。
- 单格式版本：不涉及旧格式迁移。
- 约束 14 豁免范围内：本任务未涉及 btree id 编号变更。

## 下一轮建议

- 若后续引入真实设备 I/O（discard 提交延迟），需为 run 期间并发提交增加
  hook 型交错测试或并发属性测试（如 loom 风格）。
- 可将「run 后队列空」不变量提升为公开断言工具，供后续 worker 变体复用。
