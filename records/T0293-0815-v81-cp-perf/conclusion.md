---
schema: pdca.asset/v1
id: T0293-0815-v81-cp-perf
phase: check
source_ids: [ac1-control-plane-impl, ac2-data-path-noregression, ac3-asym-stall-noregress, ac4-ordering-protocol, ac5-criterion-doc]
---

## 上下文

T0293（承接 T0291 后的 v81 控制面性能提升）。目标：对称负载追赶 v80 基线（median ≤ 48.97ms、p99 明显下降、线程下降）+ 不对称负载资源不退化；承接 T0292 的 AC-5 判据口径修正（行为判据 + 对称基线双维度）。

实施范围：`src/agent_plain_ingress.cpp`，仅控制面：
- **O1** `ingress_arm_write` helper + `write_armed` 会话标志：多完成/快速路径同 tx 只调用一次 `reactor_mod(WRITE)`，flush 完成后复位；所有 WRITE 入口统一。
- **O3** fastpath：无 in-flight 控制 job 时 PING 在 reactor 线程零堆分配直写 PONG（不走 work pool/vector/sink），TIME 走本地 vector 同步渲染；SYS 仍走 work pool。`control_jobs.empty()` 门控保证与异步 SYS 不反转响应顺序。

## 假设与结果

- 假设：降低单 Reactor 每帧 syscall/分配往返可提升对称控制面性能且无回归。
- 结果（对称基准 control_plane 32/7，多采样）：
  - median：54.45ms → **约 51.9ms**（采样 50.5~53.3，中位集中）
  - p99_upper：12.03ms → **约 11.4ms**
  - agent_threads：7（未降）；RSS 6964~6976（持平）
  - v80 参照：median 48.97 / p99 4.56 / threads 4（归档口径）

## 分析

- AC-1（对称 median≤v80 / p99 明显降 / 线程↓）：**部分达成**。median -5%、p99 -5%，较 v81 优化前明显改善；但未追平 v80 绝对值（48.97），线程 7 未降。差距归因：单 Reactor 汇聚点 + 独立 control worker 是 v81 非阻塞架构固有成本，属 PRD 范围外「多 Reactor 分片」，非本轮改动引入缺失。
- AC-2（data-path ≥ v80 97% 无回归）：**达成**。put 持平/微升（521~545），get 在既有 ±5% 测量噪声内；改动仅触控制路径。
- AC-3（不对称 stalled 控制会话不增长业务 worker）：**达成**。v81_control_frame_integration.sh PASS（baseline=3、stall=3、burst=ok）。
- AC-4（每会话有序性 + 协议兼容）：**达成**。v81_control_frame_integration.sh + plain_ingress_integration.sh 全 PASS（含逐字节 PING→PONG 断言语义、business 帧 park、握手/超时）。
- AC-5（判据文档，承接 T0292）：**达成**。ac5-control-plane-criterion.md 定义「行为判据 + 对称基线」双维度，替换单一 agent_threads 峰值口径，并据新判据评估本轮。

## 失败原因（仅 rejected/partial 填写）

AC-1 未完全达成：median 未≤48.97、线程未降到 v80 的 4。非代码错误，是 v81 非阻塞架构相对 v80 阻塞模型的结构性成本（额外 reactor 汇聚 + control worker），继续追平需架构级改动（多 Reactor 分片），PRD 明确列入范围外。

## 适用边界

- 优化仅在单 Reactor 汇聚的 plain ingress 控制面有效；对 TLS 控制面、多 reactor、数据面无作用。
- fastpath 仅在 `control_jobs.empty()`（无异步 SYS 在飞行）时启用，保证协议顺序不变。
- 性能数据依赖 benchmark 口径（壁钟批次中位数），波动 ±5%，结论以多次采集中位判据。

## 下一轮建议

- 若需继续追平 v80 median/线程：立项范围外「多 Reactor 控制面分片」，新任务承接。
- 不对称负载深挖：O2（控制完成 HIGH 优先投递）在控制/数据混跑场景的理论收益未实测，可作后续提升片。
- T0292（AC-5 判据口径修正）目标已被本轮 AC-5 吸收产出，按流程归档/标记 absorbed。
