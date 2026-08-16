# backupstream 传输所有权设计分析 — 规格文档

任务 ID: T0299
场景类型: research
创建: 2026-08-16

## 问题陈述

- **现状**: backupstream v101 的 Agent 网络侧存在两条传输路径：plain（单 Reactor + `agent_plain_ingress`）与 TLS（`reactor_group` 分片 + `tls_reactor_conn_t`）。v83-v87 演进后，两类传输通过统一的 transport adapter（`emit_frame`/`resume_rx`/`tx_bytes`/`request_close`）驱动共享的 TREE/FILE/RESTORE/Lane FSM；EXEC 在 plain 下二次转移到共享 EXEC 事件域，TLS 下留在 TLS Reactor。但文档（ARCHITECTURE/ROUND*_REVIEW/NETWORK_MODEL）零散描述了这些转移，缺少一份**系统化、以所有权归属为第一视角**的设计分析：每个阶段谁拥有 socket、谁拥有协议状态、谁拥有文件系统工作、转移的并发安全契约是什么。
- **目标**: 产出一份「传输所有权设计」系统分析文档，回答"backupstream 的传输所有权是如何组织的、为什么这样组织"。
- **差距**: 无现成文档以"所有权转移"为主线完整刻画 plain/TLS 双径；既有资产（T0287 架构总览、T0295 演进学习、T0294 优化方案）均非"所有权归属"单维度深挖。

## 解决方案

在 PDCA 记录目录产出 `transport-ownership-report.md` 分析报告，以源码（agent_plain_ingress/tls_reactor/agent_tls_runtime/agent_tree_reactor/agent_file_reactor/agent_restore_reactor/agent_lane_group/work_pool/agent_exec_runtime/client 侧）为唯一事实来源，docs 文档为设计意图补充。报告以**图示（Mermaid 图）为核心载体**（图示优先，文字仅作必要说明与图例），延续 T0296/T0297 的图形化报告规范。报告结构：

1. **所有权模型总览**: 三类所有权（socket 所有权 / 协议状态所有权 / 阻塞工作所有权）的定义与判定方法（含图示）。
2. **Plain 传输路径剖析**: ingress 状态机（HELLO→WAIT_OPEN→各业务 FSM）的所有权流转；业务帧（TREE/FILE/RESTORE/Lane/EXEC）各自的所有权归属与转移点（含图示）。
3. **TLS 传输路径剖析**: `tls_reactor_conn_t` 的所有权模型、与 plain 的 adapter 对照（含图示）。
4. **Transport adapter 抽象**: 五接口（emit_frame/resume_rx/tx_bytes/tx_can_accept/request_close）的语义、两径实现对照表。
5. **所有权转移点清单**: 逐个枚举转移（ingress→business FSM、FSM→work pool 提交/完成回穿、plain EXEC→共享事件域、Lane ATTACH→lane FSM、lane group 返回 WAIT_OPEN 等），每个给出转移前/后所有权与并发安全契约（完成回调必须回穿 Reactor 上下文等）（含图示）。
6. **双径差异与设计理由**: 为什么 plain 保留单 Reactor 而 TLS 用分片；为什么 EXEC 双径不同；遗留的阻塞桥（若有）。
7. **所有权边界风险清单**: 基于剖析识别的潜在所有权违规风险（不改码，仅指出）。

## Seam 分析

### 测试接缝

research 场景，无测试产物。分析正确性通过源码路径与函数级引用可核验。

### 声明的测试接缝

research 场景无测试产物，跳过。

### 验收可测性

- 每个 AC 可独立判定：报告存在、覆盖对应内容、含源码引用、git 可核验。

## 用户故事

1. 作为架构读者，我想要 plain 与 TLS 各帧类型的 socket 所有权归属表，以便知道任何时刻 socket 归谁管。
2. 作为并发维护者，我想要每个所有权转移点的并发安全契约，以便理解完成回调为何必须回穿 Reactor。
3. 作为学习迁移者，我想要 transport adapter 的两径对照，以便复用"同一 FSM 双传输驱动"的模式。
4. 作为风险审查者，我想要所有权边界风险清单，以便识别潜在的悬垂/重入问题。

## 实现决策

- 报告存放于 PDCA 记录目录 `records/T0299-0816-transport-ownership/evidence/`（沿用 T0296 惯例，不写入项目仓库）。
- **图示优先**：Mermaid 图为报告核心载体，每个主题节配至少一张图；文字承担图例与必要说明，不承担主要信息负载。图示风格延续 T0296/T0297：`flowchart LR/TD` 为主，图下加 `> 图例：` 说明。
- 以源码函数级分析为唯一事实来源；docs/ARCHITECTURE.md 与 ROUND*_REVIEW.md 仅补充设计意图。
- 报告使用结构化 Markdown：每节含「源码位置 + 函数级引用 + 机制说明」三要素；转移点用表格枚举。
- 每张 Mermaid 图经 mmdc 渲染验证通过（≤20 行优先，复杂图可适度放宽）。
- 不修改项目代码，不产出测试/脚本。

## 测试决策

research 场景无测试产物。

## 验收标准

- [ ] AC-1: 报告覆盖 plain 传输路径全链路所有权流转（ingress HELLO/WAIT_OPEN/业务 FSM 各阶段），每阶段给出 socket/协议状态/阻塞工作的所有者
- [ ] AC-2: 报告覆盖 TLS 传输路径所有权模型，并与 plain 侧给出 adapter 接口对照表（emit_frame/resume_rx/tx_bytes/tx_can_accept/request_close 两径实现）
- [ ] AC-3: 报告枚举至少 4 个所有权转移点（ingress→业务 FSM、FSM→work pool 完成回穿、plain EXEC→共享事件域、LANE_ATTACH→lane FSM），每个含转移前后所有权与并发安全契约
- [ ] AC-4: 报告给出双径差异（单 Reactor vs 分片、EXEC 归属差异）及设计理由
- [ ] AC-5: 报告给出所有权边界风险清单（含位置与理由，不改码）
- [ ] AC-6: 每个剖析对象含「源码位置 + 函数级引用 + 机制说明」三要素，可 grep 核验
- [ ] AC-7: 报告以 Mermaid 图为核心载体，每个主题节至少一张图，图经 mmdc 渲染验证通过，图下含图例说明

## 范围外

- 不改码、不产出优化方案（T0294 已覆盖）。
- 不重复 git 演进逐版本分析（T0295 已覆盖）。
- 不重复 Reactor 相位会计/可观测性时间分解（T0296/T0297 已覆盖）。
- 不覆盖 dirty journal、catalog 存储、客户端目录结构等非传输模块。

## 备注

- 基线资产：T0295（演进学习）、T0296/T0297（Reactor 相位会计）、T0294（优化方案）、T0287（架构总览）。
- 关键源码锚点：`agent_plain_ingress.cpp` 状态机与 `ingress_source_cb` 分发、`ingress_exec_handoff`、`ingress_make_lane_transport`、`agent_tls_runtime.cpp` 的 TLS transport adapter、`tls_reactor.hpp` 所有权接口。