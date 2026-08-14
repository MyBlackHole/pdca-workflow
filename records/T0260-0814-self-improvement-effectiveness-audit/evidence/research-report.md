# T0260 真实 AI 使用与自我提升记录机制审计

## 调研目标

1. 用真实、非 fixture 的任务记录识别本项目可验证的 AI 使用效率损失。
2. 判断 Flow Issue 记录方式是否真的能发现并推动问题，而不是只积累记录。
3. 分别判定记录发现能力和完整自我提升闭环是否生效。

## 方法

- 观察窗口从 `pdca/improvements/flow-issue-cutover.json` 的 2026-07-30 20:27:22 +08:00 开始。
- 先从 clarifications、任务 triage/conclusion、journal、doctor 和可执行失败建立独立参照集，再读取 occurrence 交叉匹配，避免循环自证。
- 全量枚举 `records/*/flow-events/*.json`，并与正式 backlog、治理产物和任务 `improvement_source` 对比。
- 在 `/tmp` 隔离副本中重建 backlog；未修改正式 backlog。
- 运行现有 unittest 和 fixture，只验证代码可执行性，不外推真实 AI 效率。

## 发现

### 1. 真实 AI 效率记录的可测边界

- cutover 后存在 116 个唯一 task slug 和 296 条 grilling 记录，可用于分析交互轮次、返工线索与流程恢复。
- 未发现绑定 task identity 的结构化 token、elapsed time 或 tool-call telemetry；这些指标结论为 `unknown`。
- UTF-8 bytes、文件 mtime 和 fixture 轮数没有被替代为真实 token、耗时或模型成功率。

### 2. occurrence 在持续产生，但正式投影严重陈旧

- 现有 199 个 occurrence，覆盖 41 个 record_id、33 个 task_id；时间延伸到 2026-08-14。
- 197/199 来自 `transition-audit`，198/199 属于 `conformance-deviation`，只有 1 条 `ai-usability`。记录范围高度集中在阶段门禁，不覆盖大多数任务完成效率信号。
- 正式 backlog 只有 14 个 issue、34 个事件，事件覆盖率 17.09%，最新事件停在 2026-07-31。
- 全量隔离重建不是简单“尚未运行”：它因 `EVENT_PATH_MISMATCH` fail-closed。5 个事件位于 `records/T0252-0814-inih-hide-symbols/`，内部 record_id 却为 `T0252`。

### 3. ID/record identity 是当前首个技术阻断点

- 全仓库存在 23 个 task ID 被多个不同 slug 使用；cutover 后 120 个 task 文件只对应 93 个唯一 task ID。
- 任务 ID 冲突与事件路径不一致同时存在，但本审计不把二者直接宣称为唯一因果；需要后续候选用并发/分配测试验证根因。
- 已确认的直接后果是：当前完整事实集不能生成有效 backlog，因此下游查询和治理看不到 165 个未进入正式投影的事件。

### 4. 记录不是完全无用，但发现能力仅为局部

- 正例：T0164 的 `PLAN_TO_DO_BEFORE_FINAL_CONFIRMATION` 和 `CONVERGENCE_PLACEHOLDER` occurrence 被 T0166 引用，促成时间线门禁和 doctor 检测修复。这是真实行动价值，不是 fixture。
- 漏报：T0230/T0231 已用真实会话证明交互轮次改进，T0234/T0238/T0239 证明词汇误报与时间戳摩擦，T0240/T0241 证明 seam 消费者缺口；这些问题均不是由 occurrence 直接发现。
- 独立参照集 5 项中只有 1 项命中。该比例只描述参照集，但足以否定“现有记录已覆盖 AI 效率问题”的说法。

### 5. 信噪与可行动性不足

- 153/199 事件出现在“同一 record_id + 同一秒”多事件 burst 中；31 个 burst group 表明一次门禁尝试会展开为大量原子问题。
- 154/199 事件关联的任务最终 verdict 为 confirmed。失败可能帮助了现场恢复，不能直接视为 false positive；但记录没有 resolution/attempt 绑定，无法区分“已当场修复的瞬态失败”和“需要跨任务改进的系统问题”。
- 典型例子 T0239 在 54 秒内产生 17 条 evidence/convergence 事件，但最终任务 confirmed；这些记录没有进入治理，也没有标记已解决状态。

### 6. 治理和效果闭环没有真实运行

- `records/*/flow-improvements/*` 文件数为 0。
- 带 `meta.improvement_source` 的任务数为 0。
- 没有真实 Flow Issue Decision、Improvement Candidate 或 Effectiveness Verdict。
- T0166 是真实改进，但走的是人工任务路径，没有正式 candidate/decision/effectiveness 链。因此它证明“记录可被人利用”，不证明 T0159 的完整治理闭环已生效。

### 7. 代码可运行不等于真实数据可用

- `tests.test_flow_issues` 12/12 通过，flow issue fixtures 8/8 通过。
- 同一时刻，真实全量重建因事件路径不一致失败。这直接证明 fixture 正确性与运行数据有效性必须分开评价。

## 优化候选排序

### P0 — 建立唯一、并发安全的 task/record identity 合约

- **真实依据**：23 个冲突 task ID；5 个 event path/record_id mismatch；全量聚合直接失败。
- **效率影响**：记录无法投影，AI 无法可靠关联任务、记录和历史证据；所有下游分析被阻断。
- **根因假设**：任务 ID 分配缺少单一原子分配器/并发锁，目录或 record 命名在生命周期中发生漂移。
- **替代解释**：部分冲突来自旧迁移或复制，而非当前分配器；需按创建时间和 git 历史验证。
- **baseline**：冲突 ID=23，路径不一致事件=5，全量聚合 exit!=0。
- **验证计划**：固定并发创建夹具；新任务 ID 唯一；event path 与 payload record_id 恒等；全量聚合 exit=0。观察后续至少 20 个真实任务或 14 天。

### P1 — 为投影增加新鲜度与可消费性门禁

- **真实依据**：正式 backlog 仅覆盖 34/199 事件，最新投影停在 2026-07-31；治理产物为 0。
- **效率影响**：问题记录不能被查询和治理，记录成本没有转化为决策价值。
- **根因假设**：聚合没有稳定消费者/触发点，且单个坏事件阻断全量投影。
- **替代解释**：团队可能有仓库外消费者；当前仓库没有其 receipt 或结果，不能据此宣称存在。
- **baseline**：覆盖率 17.09%，投影 lag 约 14 天，治理文件=0。
- **验证计划**：投影成功且 input digest 对应全部有效事件；新事件在约定 SLA 内可查询；至少完成一次用户治理 decision，并保留 receipt。

### P2 — 记录真实 AI 任务效率，而不只记录 transition conformance

- **真实依据**：197/199 是 transition-audit；T0230/T0231 两个真实效率案例均无 occurrence；token/elapsed/tool calls 为 unknown。
- **效率影响**：系统能记录门禁失败，却不能系统发现交互轮次、返工和模型执行成本。
- **根因假设**：occurrence source/category 与触发点围绕 transition gate 设计，没有 runner/task outcome 消费者。
- **替代解释**：clarifications 和 journal 已提供部分代理事实；它们尚未进入统一的效率发现模型。
- **baseline**：独立参照集中的真实 AI 效率案例捕获 0/2；结构化运行遥测缺失。
- **验证计划**：先用 task ID 绑定交互轮次、返工/恢复与结果；只有真实 runner 可用时才增加 token/elapsed/tool-call。用保留任务集做前后配对，不建立无消费者的空 telemetry。

### P3 — 将事件 burst 归并为 attempt，并记录 resolution

- **真实依据**：153/199 事件位于 31 个同秒 burst；T0239 54 秒内 17 条但最终 confirmed。
- **效率影响**：AI/用户需要重复消化同一尝试的原子门禁问题，无法区分已修复瞬态问题和系统性问题。
- **根因假设**：事件缺少 attempt/session 与 resolution 关系，聚合只按 issue fingerprint 计数。
- **替代解释**：每条原子失败对现场修复可能都有价值；因此应保留不可变事实，只新增派生归并和解决状态，不删除事件。
- **baseline**：burst events=153，burst groups=31，resolution 绑定=0。
- **验证计划**：保持原始事件不可变；查询默认按 attempt 展示并可展开；confirmed 后能绑定 resolution；对保留样本测量上下文和人工判断轮次变化。

## 判定

### 记录发现能力：partial

通过理由：T0164→T0166 是至少一个经独立证实、足以支持后续验证的真实发现。

不能判 effective 的理由：独立参照集存在 4 个漏报；记录范围几乎全是 transition conformance；正式 backlog 陈旧且当前不可重建；大量 burst 没有 resolution，系统性可行动性不足。

### 完整自我提升闭环：partial

通过部分：真实 occurrence 持续产生，且至少一次被人工用于实施改进；确定性完整链 fixture 仍通过。

缺失部分：没有真实 decision、candidate、improvement_source task、post-change observation 或 effectiveness verdict。首个当前阻断点是 identity/path 完整性导致 backlog 无法重建；即使绕过该点，治理消费者仍为零。

## 结论与建议

现有机制不是完全“白记录”，但当前也不能称为真正生效。它成功证明过一次“记录 → 人工改进”的价值，却没有形成持续、可消费、可验证的 AI 效率提升循环。

建议按 P0→P1→P2→P3 顺序治理：先恢复身份与投影可信度，再建立消费/治理触发点，然后扩展到真实 AI 效率信号，最后优化事件展示噪声。每个候选仍需独立 Improvement Candidate/Task 和真实前后观察，本任务不越权创建。

## 参考资料

- `knowledge/pdca-flow/self-optimization-loop.md`
- `knowledge/ai-efficiency/ai-friendliness-review-methodology.md`
- `knowledge/ai-efficiency/ai-execution-and-invocation-contracts.md`
- `records/T0159/conclusion.md`
- `records/T0166-0731-flow-integrity-hardening/conclusion.md`
- `records/T0230-0809-ai-efficiency-proof/conclusion.md`
- `records/T0231-0809-followup-frontier-batch-spread/conclusion.md`
- `records/T0238-0809-mechanism-fixes/conclusion.md`
- `records/T0239-0809-transition-timestamps/conclusion.md`
- `records/T0240-0809-seam-ci-gate/conclusion.md`
- `records/T0241-0809-seam-doctor-gate/conclusion.md`
