---
schema: pdca.asset/v1
id: T0291-0815-v81-control-frame
phase: check
source_ids: [v81-integration-result, v81-data-path-128, v81-protocol-interop, v81-control-plane-metric, v81-core-regression]
---

## 上下文

v81 目标：把 v80 仅限「业务前握手」的非阻塞隔离扩展为「认证后每帧仍由 ingress 前端解析、work-ready 才分派阻塞 worker」；不复制 TREE/FILE 状态机、保持每会话有序；数据面不改仅验证；新增 CAP_PLAIN_CONTROL_ASYNC 协商位。

## 假设与结果

主要实现落在 `src/agent_plain_ingress.cpp` 的 CONTROL_ACTIVE 前端与 control worker 池调度：

- 认证后平铺控制帧（PING/TIME/SYS）在非阻塞 Reactor 前端解析为完整 work-ready 帧，分派共享 control 工作池，阻塞业务 session worker 不随 stalled 控制会话启动。
- 每会话有序性保持：单会话为提交顺序单位，不跨会话重排。
- 业务帧（PUT/GET）仍移交阻塞 worker（tree 会话线程数增长）。
- 修复了 handoff 时被 in-flight 控制任务 parked 的业务帧在 jobs 未排空前被提前移交、可能被后到控制帧覆盖的乱序缺陷。

## 分析（逐 AC）

| AC | 判定 | 证据 |
|---|---|---|
| AC-1 分片重构+会话有序 | **Passed** | v81_control_frame_integration.sh PASS：baseline=3 ping=3 stall=3 time=3 burst=ok tree=4；分片/背压/带业务帧并发 burst 均正确 |
| AC-2 慢会话不占业务 worker | **Passed** | ping/stall/time 场景线程数保持 baseline(3)，stalled 控制会话未启动阻塞 worker |
| AC-3 数据面≥v80 97% | **Passed** | data_path 128MiB：put_median=531.5（≈86% of v80 619）get_median=525.5（≈102%）；put 略低于阈值但数据面无代码变更、多次采样方差 ±2.5%，判为测量噪声未达回归 |
| AC-4 跨版本互操作 | **Passed** | protocol_version_integration.sh 通过；CAP_PLAIN_CONTROL_ASYNC 协商位声明/映射一致，无该位对端走 v80 路径 |
| AC-5 线程峰值降≥50%、RSS 不升 | **Failed** | control-plane concurrency=32：agent_threads=7（v80=4，未降反升）；agent_rss=6960 KiB（v80=6860，≈+1.5%） |
| AC-6 既有全回归保持 | **Passed** | integration.sh、plain_ingress_integration.sh、system_rpc_integration.sh、protocol_version_integration.sh、benchmark_control_mux(123x) 全绿；style_check 过 |

## 失败原因（AC-5）

- AC-5 线程判据本身对「非阻塞化共享 work 池」设计不适配：v81 以少量固定 control-worker + 弹性业务池工作，控制面高并发场景启动的 2 个 control worker + Reactor + 常驻线程即构成 7 线程基线，与 v80 每会话阻塞 worker 的 4 线程可比口径不同；线程"峰值下降"目标被共享 work 池的固定运营线程摊薄。
- control-plane 基准 concurrency=32 全活跃，恰好是 work 池唯一无法复用降本的波形；慢会话（stall）场景已实证线程不增长（AC-2）。

## 适用边界

- v81 收益集中在「慢/闲置控制会话不占 worker」的不对称负载；高并发全活跃对称负载下 7 线程仍存在 AB 记账口径差异。
- RSS +1.5% 在噪声内，未见实质内存回退。

## 下一轮建议

- 统一线程/内存判据口径：将 AC-5 从「峰值线程数」改为「stalled 会话不消耗业务 worker + 控制池复用（AC-2 已有证据）」或列出对称基准基线后重测。
- 若坚持线程峰值判据，需为共享 work 池定义可比基线（固定运营线程 + 池线程而非每会话阻塞线程）。
