---
schema: pdca.asset/v1
id: T0287-0815-backupstream-architecture
phase: check
source_ids: [ac-report, convergence-map-v2]
---

## 上下文

本任务（T0287）对 backupstream 80.0.0（约 2.9 万行 C++）做实现架构分析，聚焦网络、线程、事件三大维度。既有文档（`NETWORK_MODEL.md`、`REACTOR.md`、`ASYNC_CALLBACK_MODEL.md` 等）版本标注滞后（标 30.0/9.0，实际已演进到 80.0.0），缺少与当前源码一致、统一覆盖三者的实现视角报告。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：网络架构为 plain/TLS 双路径，plain 侧含 v80 非阻塞 ingress | **supported**：`agent_plain_ingress.cpp` 确认 WAIT_HELLO→SEND_HELLO_ACK→WAIT_OPEN 状态机 + 64 KiB 预算 + token 认证 + session-open 双阶段超时；TLS 侧 `tls_reactor.cpp` + `reactor_group.cpp` 分片确认 |
| H2：线程架构是"事件线程与阻塞工作线程分离" | **supported**：main reactor、Reactor Group、弹性会话池、EXEC 事件域 shard、control/lane/lane_cpu/tree 四类 work_pool 均有源码证据（`src/backup_agent.cpp`、`src/agent_session_pool.cpp`、`src/agent_exec_io_pump.cpp`） |
| H3：事件架构基于 reactor_t 且含安全 identity/优先级/合并 | **supported**：`src/reactor.hpp` 确认 generation:slot token、HIGH/NORMAL 双队列、eventfd 唤醒、timerfd 最小堆、interest 更新合并（50.0） |
| H4：既有文档存在可核验的滞后差异 | **supported**：清单列出 7 项差异，均对应源码已更新实现，如 v80 plain ingress 取代 NETWORK_MODEL 中"plain-TCP 仍同步"论断 |
| H5：报告可同时覆盖关键路径与存储概述 | **supported**：含接受→ingress→会话池→EXEC 移交、TLS 连接、备份目录批处理三条关键路径；存储/数据架构单列概述节 |

## 分析

### PRD 验收

| AC | 证据 | 状态 |
|---|---|---|
| AC-1 报告含六节 | `docs/ARCH_IMPLEMENTATION.md`（`## 1..8` 共 8 个顶层节） | Passed |
| AC-2 网络双路径各含 ≥2 源码引用 | plain: `agent_plain_ingress.cpp`×多、`agent_session_pool.cpp`；TLS: `tls_reactor.cpp`、`agent_tls_runtime.cpp`、`reactor_group.cpp` | Passed |
| AC-3 线程 ≥5 类且各含源码引用 | 7 类：main reactor/Reactor Group/弹性会话池/EXEC shard/control/lane/lane_cpu/tree 池，均列源码 | Passed |
| AC-4 事件机制各含源码引用 | `src/reactor.hpp` 覆盖 token/generation、双优先级、eventfd、interest 合并 | Passed |
| AC-5 滞后差异 ≥3 项且可 grep 核验 | 清单 7 项，差异对应源码均有 grep 证据 | Passed |
| AC-6 关键路径图 | ASCII 图覆盖接受→ingress→会话池→EXEC 移交（§5.1） | Passed |
| AC-7 副本入 evidence | `ac-report.md` 已登记（sha256:8c16…） | Passed |
| AC-8 中文+英文术语双注 | catalog/generation/plain/ingress/Data Lane/Work Pool/Reactor/resume 等均含英文原名 | Passed |

### 关键实现决策

- 以源码为唯一事实来源；滞后文档仅作背景参考，不复制其断言。
- 报告采用概念级分层 + 关键热路径源码级证据双轨（Q2=C）。
- 报告同时写入项目 `docs/` 与 PDCA 记录 evidence（Q3=A）。
- 滞后差异清单独立成节（Q4=A），存储架构仅概述其整体位置（Q5=B）。

### 验证

- `validate-convergence.py` 返回 `valid: true`，AC-1..8 均有非 map 证据覆盖。
- 收敛映射文本与 task.json `meta.convergence` 逐字一致。

## 适用边界

- 本报告描述 80.0.0 源码现状；未来版本演进后需重新核验。
- 存储架构仅为概述，不深入 LMDB/MDB_VL32 内部。
- 未做基准测试，无性能断言。
- 未逐文件穷举全部 ROUND*_REVIEW。

## 下一轮建议

- 可基于本报告对滞后文档（`NETWORK_MODEL.md`/`REACTOR.md`）做版本标注更新（独立任务）。
- 可对 v80 之后的"后续控制帧非阻塞化"方向做设计分析（ROUND80 提出的 next bottleneck）。
- 可考虑将本报告纳入项目文档目录索引。

## Verdict

```json
{
  "outcome": "confirmed",
  "reason": "八项 AC 全部通过，报告与 80.0.0 源码一致，网络/线程/事件三大维度均有源码证据支撑，滞后差异清单可核验。",
  "verdict_id": "T0287-confirmed-20260815",
  "at": "2026-08-15T15:22:00+08:00"
}
```
