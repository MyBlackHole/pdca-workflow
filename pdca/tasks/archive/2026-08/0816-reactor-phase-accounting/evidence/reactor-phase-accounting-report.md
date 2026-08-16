# Reactor 相位会计专题调研报告：callback/phase/residual 守恒分解方法论

任务: T0296 (0816-reactor-phase-accounting)
来源: T0295 识别出的深潜专题（v101 相位会计）
日期: 2026-08-16

## 调研目标

对 backupstream v101 的 Reactor 相位会计机制做源码级剖析，覆盖：
reactor.cpp/reactor.hpp 的相位记录与窗口 API、agent_observability.cpp 的 server 端
采集、backup_observe.cpp 的离线 diagnose 消费、ROUND100/101 文档的设计意图，
提炼可跨项目复用的「事件循环时间守恒分解」方法论，并输出实现缺口改进建议。

## 方法

1. **primary source 优先**：以当前 HEAD 源码与 v101 commit（867da08）diff 为事实来源；
   ROUND101_REVIEW.md 为设计意图佐证；tests/unit.cpp 与
   tests/backup_observe_diagnose_integration.sh 为行为断言交叉验证。
2. **链路追踪**：producer（work_pool 快照）→ 记录（reactor_record_phase/callback）
   → 窗口查询（reactor_callback_window）→ server 归因（agent_observability）
   → 离线诊断（backup_observe diagnose）四段逐一核验。
3. **交叉核验**：ROUND101 文档声称的守恒不变量、相位域不相交、truncated 语义、
   容量 512、互不挤占，逐一与实现代码对照。

## 发现

### 0. 链路架构总览（ASCII）

```text
┌───────────────────────── 事件循环时间守恒分解（v101）─────────────────────────┐
│                                                                              │
│  [producer] worker 线程完成 work，post completion 回 Reactor                 │
│    work_pool.cpp:389-398                                                     │
│    └─ reactor_post_wait_priority_observed_kind → observation 快照             │
│       { enqueued_ns, callback_sequence, phase_sequence }  (acquire 游标)      │
│                                                                              │
│  [记录] Reactor 主循环四处埋点（reactor.cpp）                                 │
│    EPOLL_WAIT(1244)  EVENT_DISPATCH(1253-1311)  POST_DRAIN(635-724)          │
│    TIMER_DISPATCH(1128-1215)                                                 │
│    └─ reactor_record_phase → phase_history[512]   （相位区间在 leaf callback │
│       reactor_record_callback → callback_history[256]   体外，会计域不相交）  │
│                                                                              │
│  [窗口] completion 回调运行（work_pool.cpp:130-133）                          │
│    reactor_callback_window(after_cb_seq, after_phase_seq, [enqueued,run])    │
│    └─ 双历史重叠裁剪会计 → 覆盖率(coverage_complete) + 分桶 wall 累加         │
│                                                                              │
│  [归因] server 端（agent_observability.cpp:525-542）                         │
│    reactor_unattributed_ns = wait - callback_wall            (v100 回退)     │
│    reactor_residual_ns     = wait - callback_wall - phase_wall(v101)          │
│                                                                              │
│  [诊断] 离线 backup-observe diagnose（backup_observe.cpp:484-509）           │
│    phase-history-truncated → 拒绝归因（环回绕）                               │
│    internal-phase-busy     → 归因到四相位（top_phase + 明细）                 │
│    residual-delay          → 归因到域外（线程去调度/未插桩 gap）              │
│                                                                              │
│  守恒：callback_wall + phase_wall + residual == reactor_wait（三者均可得时）  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1. 数据结构与固定容量（reactor.hpp）

- `reactor_phase_record_t{sequence, begin_ns, end_ns, phase}`（reactor.hpp:126-131）：
  相位记录仅含时间区间与四值枚举，**不含 FD/路径/负载/标签**——固定基数、无 payload 设计。
- `reactor_callback_window_t` 扩展相位域（reactor.hpp:152-161）：
  `phase_history_enabled/phase_coverage_complete/phase_history_capacity/phase_records/
   phase_wall_ns/top_phase/top_phase_records/top_phase_wall_ns/phase_counts[4]/
   phase_wall_by_kind_ns[4]`。
- 四相位枚举 `reactor_internal_phase_t`（reactor.hpp:109-115）：
  `EPOLL_WAIT=0 / EVENT_DISPATCH=1 / POST_DRAIN=2 / TIMER_DISPATCH=3`。
- 独立固定容量：callback 历史 **256**（`kReactorCallbackHistory`，reactor.cpp:18），
  相位历史 **512**（`kReactorPhaseHistory`，reactor.cpp:19）——两个独立环形，
  内部 bookkeeping 不会挤占 callback 证据。

### 2. 记录机制（reactor.cpp）

- `reactor_record_phase()`（reactor.cpp:106-118）：单调序列 `phase_sequence`（release 递增），
  环形写入 `phase_history`，满时覆盖最旧；无效区间（end<=begin）直接丢弃。
  与 `reactor_record_callback()`（reactor.cpp:88-104，`callback_sequence` 独立递增）**双序列并存**。
- 初始化/销毁/使能（reactor.cpp:316-319, 423-428, 917-925）：`phase_sequence` 归零、
  环形清空、`reactor_set_callback_history_enabled(true)` 时 `callback_history.resize(256)`
  且 `phase_history.resize(512)`，两者一起开关。

### 3. 会计域不相交（关键设计）

相位区间**刻意记录在 leaf callback 体之外**，使会计域两两不相交：

| 相位 | 埋点位置（reactor.cpp） | 覆盖区间 |
|------|------------------------|---------|
| EPOLL_WAIT | 1244-1245 | epoll_wait 前后 |
| EVENT_DISPATCH | 1253-1265, 1311 | 每个 fd 事件 dispatch 前 [dispatch_begin, dispatch_pre_end] + 回调返回后 [callback_return, now] |
| POST_DRAIN | 635-636, 642-650, 678-682, 692-705, 709-724 | post 队列 dequeue/dispatch 前后/requeue/finish |
| TIMER_DISPATCH | 1128-1135, 1153-1215 | timer source 读 fd 前后 + 每个 timer 回调 dispatch 前后 + rearm |

核心证据（EVENT_DISPATCH，reactor.cpp:1253-1311）：
- 相位区间 `[dispatch_begin, dispatch_pre_end]`（1265）与 `[callback_return, now]`（1311）
  **不包含** callback 执行区间 `[begin, end]`（1272-1289）；
- callback 执行区间单独记入 callback 历史（1301-1303，`REACTOR_CALLBACK_FD`）。
- wake_source 与 timer_source 的 FD 事件不记入 callback 历史（1261-1262 `record_fd`），
  但记入相位（POST_DRAIN 733-734 / TIMER_DISPATCH），避免计数双算。

### 4. 窗口重叠会计与守恒（reactor.cpp:120-217）

`reactor_callback_window(r, after_sequence, after_phase_sequence, begin_ns, end_ns, out)`：

- **双序列快照输入**：`after_sequence`（callback 序列）与 `after_phase_sequence`（相位序列）
  均为 producer 在 completion 被接受 posting 时快照的游标（reactor.hpp:167 中
  `reactor_post_observation_t.phase_sequence`；reactor.cpp:843-845 捕获）。
- **覆盖完整性**：callback `coverage_complete = oldest.sequence <= after_sequence+1`（136）；
  相位 `phase_coverage_complete = oldest_phase.sequence <= after_phase_sequence+1`（184）。
  环形回绕 → `truncated`，不做假装完整的分解。
- **重叠裁剪**：每条记录与 [begin_ns, end_ns] 求 overlap（141-143），
  callback 累加 `wall_ns += overlap`、按 class/source_kind 分桶；相位累加
  `phase_wall_ns += overlap`、按四相位分桶（194-198）。**同一时刻不重计**
  ——callback 区间与相位区间不相交，故求和即窗口内总忙。
- **top 计算**：top_source（166-172）与 top_phase（201-206）均为窗口内累计最大。

守恒不变量（当 coverage_complete && phase_coverage_complete 且减数为非负）：
```
callback_wall_ns + phase_wall_ns + residual == reactor_wait_ns
```
其中 `reactor_wait_ns` 由 work_pool.cpp:124-126 计算（`run_ns - completion_enqueued_ns`，
即 enqueue-to-run 区间）。

### 5. 链路起点：work_pool 双序列快照（work_pool.cpp / .hpp）

- `work_item_t` 持有 `completion_enqueued_ns / completion_callback_sequence /
  completion_phase_sequence`（work_pool.hpp:138-140）。
- producer（worker 线程 posting 完成时）经 `reactor_post_wait_priority_impl` 的
  observation 捕获两个序列号 + 时间戳（reactor.cpp:843-845）。
- consumer（completion 回调在 reactor 线程运行时）用双序列快照 + [enqueued, run]
  区间查询窗口（work_pool.cpp:130-133）。

**producer 端深入**（work_pool.cpp:376-402）：
- 捕获条件：仅当 `item->lifecycle` 存在时，走观察版
  `reactor_post_wait_priority_observed_kind(completion_reactor, REACTOR_POST_NORMAL,
  REACTOR_SOURCE_WORK_COMPLETION, work_completion_post, item, &observation)`
  （389-392），否则用无观察的 `reactor_post_wait_priority`（393-394），此时不做会计。
- observation 语义（reactor.cpp:843-845）：`enqueued_ns = reactor_now_ns()`、
  `callback_sequence = callback_sequence.load(acquire)`、
  `phase_sequence = phase_sequence.load(acquire)`——即 **post 入队瞬间的游标值**。
- 捕获失败处理：`post_rc != 0` 时 `completion_pending` 复位并走异常路径（403-404），
  observation 不被采纳。
- 三字段归零时机：work item 初始（205-207）与复用前（382-384）均清零，
  防陈旧快照被误用。

### 6. server 端归因（agent_observability.cpp:490-545）

`agent_observability_completion_detail()` 输出 completion-run 事件字段：
- callback 域：`callback_wall_ns / callback_max_ns / class/source 分桶`（505-524）；
- v100 遗留：`reactor_unattributed_ns = reactor_wait_ns - callback_wall_ns`
  （525-526，仅 coverage_complete）；
- **v101 相位域**（527-538）：`reactor_phase_history=complete|truncated`、
  `reactor_phase_history_capacity=512`、`reactor_phase_count`、`reactor_phase_wall_ns`、
  `reactor_phase_top(+count/ns)`、四相位各自 `_ns`；
- **残差**（539-542）：`reactor_residual_ns = reactor_wait_ns - callback_wall_ns -
  phase_wall_ns`，仅当两个 coverage_complete 且减数非负。

### 7. 离线诊断（backup_observe.cpp:90-111, 411-435, 484-509）

`diag_stage_t` 新增相位字段（90-111）；`diagnose_event` 解析 JSONL attrs（411-435）；
`diagnose_timing` 按阈值产生三类 finding（484-509），全部 confidence=confirmed：

| finding | 触发条件 | 语义 |
|--------|---------|------|
| `reactor-phase-history-truncated` | phase_history 存在且 `!phase_history_complete` | 相位环回绕，显式拒绝残差根因归因 |
| `reactor-internal-phase-busy` | phase complete 且 `phase_wall_ns >= stage_ms` | 固定相位累积占用窗口，报告 top_phase + 四相位明细 |
| `reactor-residual-delay` | 两个 history complete 且 `residual_ns >= stage_ms` | callback+相位都解释不了 → 线程去调度或未插桩 gap |

v100 的 `reactor-unattributed-delay` 回退保留（当 phase_history 缺失时），
兼容旧记录（backup_observe.cpp:506-508）。

### 8. 测试断言（tests/unit.cpp:349-366, tests/backup_observe_diagnose_integration.sh）

- unit.cpp:362-366：`phase_history_complete && phase_count >= 1 &&
  phase_wall_ns <= reactor_wait_ns - callback_wall_ns && phase_top < PHASE_COUNT`。
- 集成测试三案例（152/161/170 行事件）：
  - b-20-1 → `reactor-internal-phase-busy`（相位 1200ms，top=post-drain）；
  - b-21-1 → `reactor-residual-delay`（callback 100M + phase 200M + residual 1200M == wait 1500M，守恒成立）；
  - b-22-1 → `reactor-phase-history-truncated`（phase 环 512 满 → 不产生 residual）。

### 9. 文档-实现一致性核验（AC-6）

| ROUND101 声称 | 实现证据 | 一致 |
|--------------|---------|------|
| 第二套独立固定 512 相位历史，不挤占 256 callback | reactor.cpp:19, 917-925 | ✓ |
| 仅四固定枚举值，无 FD/路径/负载/标签 | reactor.hpp:109-115；record 结构无 payload | ✓ |
| 相位区间记录在 leaf callback 体外，会计域不相交 | reactor.cpp:1253-1311, 1265/1311 vs 1272-1289 | ✓ |
| 守恒 callback+phase+residual == wait | agent_observability.cpp:539-542；集成测试 b-21-1 | ✓ |
| 环回绕报 truncated，不做假完整 | reactor.cpp:184 `phase_coverage_complete` | ✓ |
| residual 仅在两 history complete 且减法非负时输出 | agent_observability.cpp:539-542 | ✓ |
| 三类 finding confidence=confirmed | backup_observe.cpp:484-509 | ✓ |
| v100 unattributed 回退保留 | backup_observe.cpp:506-508 | ✓ |
| 测试显式强制会计边界 | tests/unit.cpp:362-366 | ✓ |

### 10. 演进衔接：v100 与 v101

v100 引入 callback 历史与 `reactor-unattributed-delay`（callback 唯一归因域），
v101 在其上叠加独立相位历史，把 unattributed 进一步拆成
`phase_wall_ns`（四相位）与 `residual_ns`（仍不可归因）。v100 记录无相位字段仍有效，
诊断优先用更强的 phase/residual 证据。

## 结论与建议

### 方法论提炼：事件循环时间守恒分解

1. **固定基数、无 payload 的分域会计**：事件循环按「相位（内部 bookkeeping）/
   callback（leaf 执行）」两域记账，每域独立固定容量环形历史，字段仅含时间与枚举，
   不携带任何 FD/路径/负载——保证可观测性不随业务规模膨胀。
2. **会计域不相交**：相位区间刻意排除 callback 执行区间（callback 前/后分别埋点），
   使两域求和不重计、不遗漏；这是守恒等式成立的前提。
3. **双序列快照窗口**：producer 在事件入队时快照两个序列游标，consumer 在窗口查询
   时以「序列 > 快照值 且 ≤ 当前」过滤，天然处理并发与覆盖；环形回绕时显式报
   `truncated` 而非假装完整。
4. **守恒残差归因**：完整窗口内 `callback + phase + residual == wait`；残差是
   "两者都解释不了"的保守信号（线程去调度、未插桩 gap），**不是根因断言**——
   证据边界与根因猜测严格分离。
5. **诊断分级**：truncated（拒绝归因）/ phase-busy（归因到相位）/ residual
   （归因到域外）三级，均为 confirmed 置信度但语义逐级保守。

### 改进建议（不改码）

| # | 建议 | 位置 | 理由 |
|---|------|------|------|
| 1 | `reactor_internal_phase_name` 对 `REACTOR_PHASE_COUNT` 返回 "unknown"（reactor.cpp:83），而 top_phase 未命中合法相位时 server 端也会输出 unknown——建议在窗口 zero 态与 truncate 态明确区分 "none" vs "unknown" 语义 | reactor.cpp:42, 79-84 | 避免 unknown 被误读为第四相位冲突 |
| 2 | `reactor_residual_ns` 的减数非负检查在 server 端仅兜底跳过输出（agent_observability.cpp:539-542），但 backup_observe 端 `reactor_residual_present` 依赖字段存在性——建议 server 端在减法为负时输出显式哨兵字段而非静默省略，便于 offline 区分「无残差」与「会计异常」 | agent_observability.cpp:539-542 | 负残差意味着会计域重叠（bug），静默丢失会掩盖实现缺陷 |
| 3 | phase 记录与 callback 记录都只存 `begin/end_ns`，无 `cpu_ns`——相位域 CPU 时间不可分离（如 post-drain 内自旋 vs 阻塞）；建议未来若 `reactor-internal-phase-busy` 反复指向单相位，为该相位加 cpu_ns | reactor.cpp:126-131 | ROUND101 第 101-103 行已预告按主导相位拆分，CPU 分离是自然延伸 |
| 4 | `reactor_record_phase` 与 `reactor_record_callback` 均通过 `callback_history_enabled` 开关（reactor.cpp:91, 108）——两历史共享单开关，无法只开相位；若想长期采集相位而不采 callback，需独立开关 | reactor.cpp:91, 108 | 当前耦合简化了控制面，但降低了诊断弹性 |
| 5 | 文档建议"若 residual 反复显著，加保守的 scheduler/run-state 证据"（ROUND101:102）——建议作为下一轮方向，不在此轮实现 | 设计层 | 遵循文档的分阶段演进纪律 |

### 适用范围与限制

- 结论限于 v101（867da08）及当前 HEAD 状态；未来版本需重新核验。
- `reactor_wait_ns` 仅覆盖 completion enqueue→run 区间，不覆盖 work 执行本身。
- 相位历史 512 固定容量，在超高事件率下可能频繁 truncated（届时只产生
  `phase-history-truncated`，不产生相位/残差归因）。
- `epoll-wait` 相位含线程去调度时间，不能直接解读为 epoll 问题（ROUND101:105）。

## 参考资料

- backupstream 当前 HEAD 源码：src/reactor.cpp, src/reactor.hpp, src/work_pool.cpp,
  src/work_pool.hpp, src/agent_observability.cpp, src/backup_observe.cpp
- v101 commit: 867da08（git show 867da08 --stat 及逐文件 diff）
- docs/ROUND101_REVIEW.md（v101 设计意图与资格声明）
- tests/unit.cpp:349-366（守恒边界断言）
- tests/backup_observe_diagnose_integration.sh:152-224（三类 finding 行为验证）
- 关联：T0295 报告（v65-v101 演进学习，已归档）