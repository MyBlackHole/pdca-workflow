---
schema: pdca.asset/v1
id: T0299-0816-transport-ownership
phase: check
source_ids: [ac-report-transport-ownership, ac-c2-review, convergence-map-v3]
---

## 上下文

T0299（research 场景）分析 backupstream v101 的传输所有权设计：plain 与 TLS 双径各自如何拥有 socket/传输，两类传输如何通过统一 transport adapter 与共享业务 FSM 协作，所有权在 Reactor/Work Pool/共享事件域之间的转移边界。研究对象包括 agent_plain_ingress（plain 路径核心）、tls_reactor（TLS 连接层）、agent_tls_runtime（TLS 业务桥接）、agent_tree_runtime/agent_file_runtime/agent_restore_reactor/agent_lane_group/agent_data_lane（业务 FSM）、agent_exec_runtime/agent_exec_io_pump（EXEC 共享域）、work_pool（回穿契约）、common.hpp（Connection 借用原语）。交付物为图示优先分析报告（7 张 Mermaid 图）+ 审查记录 + 风险清单，产出存 PDCA records。

## 假设与结果

| 假设 | 结果 | 结论 |
|------|------|------|
| plain 传输路径所有权可全链路剖析 | §2.1 状态机图 + §2.2 五阶段所有权明细表，每阶段 socket/协议状态/阻塞工作所有者给出 | 满足 AC-1 |
| TLS 所有权模型 + adapter 对照可完整给出 | §3 全节 + §4.2 两径实现对照表（9 维度） | 满足 AC-2 |
| 可枚举 ≥4 个所有权转移点含并发安全契约 | §5.2 枚举 8 个转移点，每点含转移前后所有权与契约 | 满足 AC-3 |
| 双径差异及设计理由可归纳 | §6 差异表 6 维度 + 设计理由列 + 图 | 满足 AC-4 |
| 存在所有权边界风险 | §7 输出 6 条风险（含位置与理由），风险 #2 被 LSP 诊断独立证实 | 满足 AC-5 |
| 报告三要素可 grep 核验 | 全文 34 处 `.cpp:` 引用；6 处关键锚点源码复核一致 | 满足 AC-6 |
| 图示优先且图可渲染 | 7 张 Mermaid 图，mmdc 全部渲染通过，每图含图例 | 满足 AC-7 |

## 分析

**核心结论**：backupstream 的所有权模型是「两容器 + 一抽象 + 一契约」。

- **两容器**：socket 所有权只落在两个地方——plain 的 `agent_plain_ingress_session_t`（直接持 `int fd` + source + tx 缓冲）或 TLS 的 `tls_reactor_conn_t`（持 `fd + SSL*` + 双 tx 队列）。plain 无独立传输对象，解析/发送内联于 session；TLS 连接永不离开 reactor（`tls_reactor_require_owner` 强制 owner 线程，业务层只通过回调访问，从不拥有 fd/SSL）。
- **一抽象**：业务 FSM（TREE/FILE/RESTORE/Lane/EXEC/Control）一律是**租借者**，通过 transport adapter（`agent_lane_transport_t` 12 接口 / `agent_tree_transport_t` 4 接口）借用 socket，双径实现同构（plain 的 `ingress_make_lane_transport` vs TLS 的 `agent_tls_make_lane_transport`）。
- **一契约**：阻塞工作通过 `work_item_t.completion_reactor`（work_pool.hpp:126）提交线程池，完成后 `reactor_post_wait_priority` 回穿 reactor 线程执行 done 回调（work_pool.cpp:388-394）。**worker 不碰业务状态，状态只在 reactor 线程改**——这是整个并发安全模型的底座。

**关键分化**：plain EXEC 是唯一一次 socket 所有权转移（`ingress_exec_handoff` :791-807：reactor_del → adopt_fd → handoff 到 `g_exec_domain` → erase → delete session）；TLS EXEC 留在 reactor（`agent_tls_ready_exec` :478-487：transport=&s->transport）。TLS 的「转移」仅是 reactor shard 间 handoff（安全点语义，OPEN+rx_paused+非 closing+非 renegotiating）。

**补充核验（grill 判定"需补充核验"）**：对 6 处关键源码锚点直接复核，全部与报告一致——① plain session 持 fd/source（agent_plain_ingress.cpp:151,153）；② TLS conn 持 fd+SSL + require_owner 返回 EPERM（tls_reactor.hpp:218-219、tls_reactor.cpp:59-70）；③ EXEC handoff 序列（reactor_del→adopt_fd→handoff→erase→delete，与 §2.3 完全一致）；④ work pool 回穿契约（work_pool.hpp:126 + work_pool.cpp:390-394）；⑤ TLS make_lane_transport（agent_tls_runtime.cpp:295-302）；⑥ TLS EXEC transport=&s->transport（agent_tls_runtime.cpp:478-487）。

## 失败原因（仅 rejected/partial）

无（verdict 为 confirmed）。

## 适用边界

- 结论限于 v101 与当前 HEAD 状态；未来版本需重新核验。
- 行号引用基于当前源码；重构后需重新定位。
- 风险清单为静态剖析产物，未做运行时验证；风险 #2 已被 LSP 诊断独立证实，其余为潜在风险供维护者核验。
- 不覆盖 dirty journal、catalog 存储、客户端目录结构等非传输模块。

## 下一轮建议

- 若未来统一两径，可评估将 `agent_lane_transport_t` 与 `agent_tree_transport_t` 合并为单一契约（当前两形状字段高度重叠）。
- 修改 EXEC 路径时优先复用 TLS 的「留在 reactor」模型，评估是否可消除 plain handoff 竞态（风险 #1）。
- 为风险 #4（lane group 跨线程完成通知链）补充 session-close 时的 group 槽位释放顺序测试。
- 风险 #6（INGRESS_TREE 下五 FSM 并发分发）值得在后续任务中做运行时验证。