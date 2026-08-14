---
schema: pdca.asset/v1
id: T0266-0815-skills-round3
phase: check
source_ids: [ac1-oos-manager, ac2-oos-antipollution, ac3-oos-triage-skill, ac4-merge-skill, ac5-merge-fixture, ac6-deepening-skill, ac7-deepening-table, ac8-no-regression, convergence-map]
---

## 上下文

T0266 是 mattpocock/skills 第二轮可证明增量。T0265 落地了文档结构契约级指标（AGENT-BRIEF 等），本轮三个增量全部为**行为级硬指标**：① out-of-scope 知识库完整化（概念聚合状态机）；② resolving-merge-conflicts 升级 intent-based（真实 git fixture）；③ design-it-twice 补 DEEPENING 深化测试策略（确定性决策表）。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：out-of-scope 可做概念级聚合状态机 | **supported**：`scripts/out-of-scope-manager.py` 实现 add/check/list；测试断言同概念追加（文件数不变）、不同概念新建、`--implemented` 反污染拒绝写入、check surfacing 历史理由。triage-work wontfix 分支升级为概念聚合 + Prior requests 追加 + dedup 前置检查。 |
| H2：merge-conflicts 可升级 intent-based 并有行为级验证 | **supported**：skill 重写为五步（状态/primary source/逐 hunk 保留意图/自动化检查/完成），含 never abort、preserve both intents 契约；真实 git fixture 构造 merge 冲突并解析，断言 `git diff --check` 无残留标记、双方意图均保留。 |
| H3：DEEPENING 深化策略可落为确定性决策表 | **supported**：design-it-twice 补深化测试策略章节（deletion test、one/two-adapter seam 纪律、replace-don't-layer）；测试断言 4 类依赖→策略映射确定性且互异。 |
| H4：每个增量有行为级硬指标 | **supported**：14 个新测试（8 行为状态机/决策表 + 6 结构契约）全绿，含真实 git fixture 与临时目录聚合状态机。 |
| H5：全量无回归 | **supported**：全量 214 passed / 4 既有失败 / 13 subtests。唯一真实回归是 SKILLS-INDEX.md 过期（改 3 skill 后未同步），已 `generate-skills-index.py` 重新生成修复；4 个既有失败（2 harness + 2 doctor）经 `git stash` 隔离验证仍失败，非本轮引入。 |

## 分析

### PRD 验收

| AC | 证据 | 状态 |
|---|---|---|
| AC-1 out-of-scope-manager 同概念追加/不同概念新建 | ac1-oos-manager（add/check/list + 聚合行为测试） | Passed |
| AC-2 已实现拒绝不写入（反污染） | ac2-oos-antipollution（`--implemented` 拒绝写入，状态 rejected-implemented） | Passed |
| AC-3 triage-work wontfix 描述概念聚合 + Prior requests + dedup 前置 + 仅 enhancement | ac3-oos-triage-skill（SKILL.md 5094 字节，含 4 条契约 marker + 脚本引用） | Passed |
| AC-4 merge-conflicts skill intent-based | ac4-merge-skill（SKILL.md 2804 字节，primary source/preserve both intents/never abort/automated checks） | Passed |
| AC-5 真实 git fixture：不 abort、无残留标记、意图保留 | ac5-merge-fixture（真实 merge 冲突→解析→diff --check=0→双方意图均保留） | Passed |
| AC-6 design-it-twice 补 DEEPENING 策略 | ac6-deepening-skill（SKILL.md 5831 字节，deletion test/seam 纪律/replace-don't-layer） | Passed |
| AC-7 依赖分类→测试策略决策表断言 | ac7-deepening-table（4 类依赖映射确定且互异） | Passed |
| AC-8 新增测试全绿 + 全量无回归 | ac8-no-regression（14 新测试绿 + 214 passed，4 既有失败非本轮） | Passed |

### 关键实现决策

- **失败驱动实现**：三个测试文件先写（12 红 2 绿），实现后全绿；merge fixture 曾因 setUpClass 共享 repo 导致测试间状态污染（单独跑过/一起跑挂），改为 setUp 每测试独立临时 git 仓库修复。
- **merge 冲突返回码**：git merge 产生冲突返回 1 是正常状态，`git()` helper 会误抛；新增 `git_allow_failure()` 显式接受非零返回码，冲突后断言 `UU` 状态。
- **反污染设计**：`--implemented` 标志使脚本直接拒绝写入（状态 rejected-implemented）——已实现的功能不是 out-of-scope，写入会污染 dedup 造成假拒绝。
- **契约 marker 双语**：DEEPENING 契约测试要求英文 marker（two adapters/the interface is the test surface），skill 文档保留中英文双语满足结构断言（术语契约延续 T0231 check-design-vocab 模式）。
- **SKILLS-INDEX 同步**：本轮改 3 个 skill，`test_generated_index_is_current` 捕获 SKILLS-INDEX.md 过期——真实回归，`generate-skills-index.py` 重生成后 valid: True。

### 已知边界（非本任务引入）

- 4 个全量测试失败均为既有状态：2 harness（AI-friendliness 契约 fixtures 涉及 round62-67 外部任务）+ 2 doctor（seam_contracts 检查外部 C++ 测试文件缺失返回 1）。`git stash` 隔离验证非本轮回归。
- LSP 静态告警（`arch_review`/`pdca_core` import 无法解析）不影响运行时。
- out-of-scope-manager 是轻量文件操作，无并发锁（与 check-ticket-claims 同级的 POSIX 约束）。
- merge fixture 覆盖单文件冲突；多文件/多 hunk 组合场景由 skill 流程指引，未逐一 fixture。

## 失败原因（仅 rejected/partial）

无。本任务全部 AC 通过，无 rejected/partial 项。

## 适用边界

- out-of-scope 知识库是 triage 的辅助记忆：真实拒绝才会填充 `knowledge/out-of-scope/`（当前仍为 .gitkeep 空目录，机制已就绪）。
- intent-based merge 解析适用于 AI agent 上下文（能查 PR/issue/commit）；纯人工小团队无外部上下文时退化为基础 git 命令指引。
- DEEPENING 决策表适用于接口设计阶段的浅模块深化评估；深度测量是定性判断（deletion test），非自动度量。

## 下一轮建议

1. 为 out-of-scope-manager 与 check-ticket-claims 增加进程级文件锁（消除并发竞态窗口）。
2. 将 merge fixture 扩展为多文件冲突 + rebase 场景（当前仅单文件 merge）。
3. 建立 out-of-scope 真实使用记录后，统计 dedup surfacing 命中率（机制效果的行为级二次证明）。
4. T0263（identity 观察）继续挂起等待观察窗，观察期满后出 effectiveness verdict。
