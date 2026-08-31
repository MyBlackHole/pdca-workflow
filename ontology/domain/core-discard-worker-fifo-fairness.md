---
schema: pdca.asset/v1
id: ontology:domain/core-discard-worker-fifo-fairness
type: domain
layer: Knowledge
status: active
summary: discard worker FIFO 公平队列语义
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 discard-worker-fifo-fairness 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# discard worker FIFO 公平队列语义

来源：T0191-0802-discard-worker-fairness-property（bcachefs 风格 Rust 存储引擎
discard worker 多桶队列）。

## 上下文与约束

T0190 建立了单桶 discard worker 的 EAGAIN 重试 seam（`run_discard_worker_once`、
`queue_discard_bucket` 返回 -11 EAGAIN / -17 EEXIST）。多桶扩展时，队列若用
无序集合（BTreeSet）提交，单个未就绪桶会阻塞后续就绪桶的处理，违反公平性。
engine-local 约束：不接真实设备 I/O、worker 为同步公共 API、测试 ≤1 分钟。

## 假设与行动

- 队列结构用 `Mutex<(VecDeque<(u64,u64)>, BTreeSet<(u64,u64)>)>`：
  VecDeque 保 FIFO 提交序（对应 bcachefs fastpath darray，
  `bch2_fast_discard_bucket_add` 的 darray_push，discard.c:643-655），
  BTreeSet 保去重（对应 in_flight 集合语义），EEXIST 不入队。
- worker 主体 `run_discard_worker()` 采用 while-直到耗尽循环（对应
  `bch2_do_discards_fast_work` while(1)，discard.c:605-633）：每轮快照当前
  队列长度，全部处理成功后继续循环以承接并发新提交；有 EAGAIN 则立即返回
  -11（无无限循环风险）。
- EAGAIN 桶 pop 后 push_back 移队尾轮转（对应主路径 advance 跳过继续遍历，
  discard.c:478-491），保证就绪桶不被阻塞。
- 并发/重启验证：多线程 Barrier 并发 queue + 单 worker run 全处理；
  属性测试用影子状态机（4 桶 free/btree/need-discard + FIFO 队列镜像）
  逐 op 对齐引擎公共 API，restart 时从磁盘重建模型并与 discover 数量一致。

## 结果与证据

- AC-1..AC-6 全部通过：6 定向测试（FIFO 耗尽 / EAGAIN 轮转 / 并发收敛 /
  重启再发现 / 去重回归）+ 属性测试 16 cases × 1..=40 op（0.89s）+
  workspace 194 lib + 10 集成全绿。
- 审查发现初版「快照单轮」实现与 while-耗尽语义不符（run 期间并发新提交
  被漏到下一轮），修正后全部测试重跑通过。

## 成功原因

- 队列结构与上游结构一一对应（darray → VecDeque、in_flight → BTreeSet），
  不引入 bcachefs 不存在的结构体（约束 13）。
- EAGAIN 用「移队尾 + 立即返回」而非「原地阻塞」：公平性（就绪桶不被阻塞）
  与可终止性（deferred 即返回，无无限循环）同时满足。
- 属性测试影子模型镜像的是公开 API 语义而非内部实现，restart 重建覆盖
  持久化路径。

## 适用与不适用条件

- 适用：同步公共 API 的 worker 队列、有上游 darray/集合可对照的公平性设计。
- 不适用：无确定性交错 hook 时，「run 执行期间并发提交」无可靠定向测试
  （断言时序敏感、易 flaky）——该路径只能由 while-耗尽语义 + 属性测试
  「run 后队列空」不变量从模型层兜底，结论需如实记录该边界。

## 下一轮建议

- 若后续引入真实设备 discard 提交延迟，为 run 期间并发提交增加 hook 型
  交错测试或 loom 风格并发属性测试。
- 「run 后队列空」不变量可提升为公开断言工具供后续 worker 变体复用。
