---
schema: pdca.asset/v1
id: ontology:domain/control-plane-nonblocking-ingress-v81-control-plane-perf-fastpath
type: domain
layer: Knowledge
status: active
summary: v81 控制面性能：纯计算控制帧 fastpath + WRITE 归并
domain:
- ontology:domain/control-plane-nonblocking-ingress
relations:
  specializes:
  - ontology:domain/control-plane-nonblocking-ingress
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# v81 控制面性能：纯计算控制帧 fastpath + WRITE 归并

## 要解决

v81 非阻塞控制面（T0291）把所有控制帧（PING/TIME/SYS）都投进共享 control work
pool，再由完成回调回写 reactor。对称负载下每帧付出 work-pool submit + worker 唤醒 +
completion-post 两次线程往返，以及每 job 的堆分配。单 Reactor 成为控制帧回写汇聚点，
延迟与线程占用偏高。

## 关键折衷（可复用）

1. **纯计算控制帧（PING/TIME）走 reactor 线程同步 fastpath**，不经 work pool：
   - PING→PONG 字段固定，直接在 reactor 线程零堆分配直写 tx；
   - TIME 经本地 response vector 同步渲染；
   - SYS（可能有文件 I/O）仍走 work pool。
   - 前提：**仅当 `control_jobs.empty()`（无异步 SYS 在飞行）时启用**，否则与异步
     SYS 的响应顺序可能反转。这个门控是语义安全关键，缺它会有保序 bug。

2. **WRITE 装配归并（`ingress_arm_write` + `write_armed` 标志）**：多个完成/快速路径向
   同一未 flush 的 tx 追加时，只做一次 `reactor_mod(WRITE)`，flush 完成后复位。减少
   冗余 epoll_ctl（一帧一 mod → 会话每轮一次）。单 job 基准无感，pipeline 多 job 见效。

3. **性能判据口径修正（承接 T0292）**：不以 agent_threads 峰值单维度判定，改用
   「行为判据（reactor 非阻塞不变式 + 保序 + 集成测试全绿）+ 对称基线（同脚本同口径
   median/p99）」双维度。避免把"线程少"误判为"性能好"。

## 实证（对称基准 control_plane 32/7，中位多次采样）

- median 54.45ms → ~51.9ms（-5%），p99_upper 12.03 → ~11.4ms；线程 7 / RSS 持平。
- 无回归：v81_control_frame_integration.sh、plain_ingress_integration.sh 全 PASS；
  data-path put 持平、get 在 ±5% 测量噪声内。
- 未追平 v80 绝对值（median 48.97、线程 4）：v81 非阻塞架构相对 v80 阻塞模型的
  结构性成本（额外 reactor 汇聚 + control worker），需多 Reactor 分片（架构级）才能
  继续逼近，属范围外。

## 适用边界

- 仅单 Reactor 汇聚的 plain ingress 控制面生效；不影响 TLS 控制面 / 数据面 / 多 reactor。
- fastpath 依赖 `control_jobs.empty()` 门控，新增控制帧类型需复核保序约束。
- 性能数据是壁钟批次中位数，波动 ±5%，判据以多次采集中位为准。
