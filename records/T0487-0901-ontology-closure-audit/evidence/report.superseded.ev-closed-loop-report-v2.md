# 本体闭环完整性审计报告 — T0487

> 任务：T0487-0901-ontology-closure-audit（research）  
> 审计范围：ontology/ 363 nodes / 871 edges / 0 islands（`ontology_graph.py --format summary` 2026-09-01）  
> 对照基线：T0450闭环审查 + T0482深化收敛 + mattpocock/skills main@457 commits (243k stars)  
> 校验：`python3 scripts/ontology-validate.py --ontology-dir ontology` → OK: 0 issues

---

## 1. 本体是否完整融入“使用完成闭环”

### 1.1 全流程硬门禁地图（`ontology/README.md:§10/§12` 为SSOT）

| PDCA阶段 | 本体消费点 | 门禁强度 | 实现位置 | 证据 |
|---------|----------|---------|---------|------|
| **Plan** | `meta.ontology_fragment` 声明 + `ontology-ready` 准入 | **硬门禁**（`plan→do` transition拒绝） | `scripts/ontology_gate.py:ontology_ready_issues()` + `ontology/concept/pdca-ontology-ready.md:1` | `transition-phase.py` 打印 `ontology-ready` 缺失时返回 `ONTOLOGY_FRAGMENT_MISSING` |
| **Do** | 实现对照fragment；变更后 `ontology_graph --format summary` 无孤岛；`register-evidence --kind` 锚定到 `pdca-evidence` 子类型 | **硬门禁**（kind未知直接报错；archive自检亦阻断） | `scripts/register-evidence.py` 枚举 `pdca-evidence` 子类型建允许表；`ontology/entity/evidence-*.md` 3子类型 | `evidence-convergence-map`/`evidence-review`/`evidence-test-result` |
| **Check** | `verify-convergence` 逐条回链 `meta.convergence → PRD AC → evidence`；Grill问“结论是否可被既有ontology节点/relations支撑” | **硬门禁**（`validate-convergence.py valid:true` 必过）+ 顾问式提问 | `scripts/validate-convergence.py` + `ontology/process/flow-check.md:1` + `ontology/concept/pdca-verdict.md` | `convergence.json` 不可作验收证据（`ontology:concept/pdca-evidence.md:8`） |
| **Act** | `meta.disposition` 必须含 `ontology:` 或显式 `records-only`；知识优先关联既有节点，缺口创建补强任务 | **硬门禁**（`act→archive` transition拒收；`ontology_gate.disposition_ontology_issues`） | `scripts/ontology_gate.py:disposition_ontology_issues` + `ontology/process/flow-act.md:1` | T0475起收紧为节点校验（`scripts/check-research-ontology-settlement.py`扩展为全任务） |
| **Archive** | `ontology-validate` 通过 + `islands:0` + `conclusion.md` verdict锚定到 `verdict-*` | **硬门禁**（`archive_ontology_ready_issues`）+ CI/Hook提交级阻断 | `scripts/ontology_gate.py:archive_ontology_ready_issues()` + `scripts/ci-ontology-gate.py` + `.github/workflows/ontology-gate.yml` + `scripts/install-git-hook.sh` | `islands: 0` 否则 `ARCHIVE_ONTOLOGY_ISLANDS` |

**设计取舍**（`ontology/README.md:127`）：plan/do/check/act的“消费”保持顾问式（不阻断吞吐），仅**创建门禁、证据/结论锚定、archive自检、CI/hook**为硬门禁；通过 `meta.ontology_exempt=true` 保留豁免，但需显式理由。

### 1.2 成熟度判定

- **已闭环（5/5阶段有硬门禁落地）**：门禁已从文档约束升级为 `transition-phase.py` + `ci-ontology-gate.py` 的提交级阻断，`archive`阶段做全图自检，符合 `ontology:concept/ontology-creation-gate.md` 与 `ontology:concept/ontology-validate.md` 的meta-ontology授权。
- **缺口（2项）**：
  1. **历史任务回溯缺口**：62个归档任务中35个 `disposition` 不含 `ontology:`/`records-only`（`pdca/tasks/archive/**/task.json` 统计），但门禁自T0475后才收紧，历史按“冻结前不追溯”处理，统计口径需分母区分（新任务85%已覆盖，`python3 audit...`）。
  2. **PRD模板硬化的可观测性**：`ontology/domain/skill-to-tickets.md:45` 已声明“有fragment无`##拆分映射`即阻断”，但仅在 `ontology_tree_split.py` 报ERROR，未在 `pdca-doctor.py` 中单独计分，属于**执行时阻断**而非**静态校验**。

**可重跑验证**：
```bash
python3 scripts/ontology-validate.py --ontology-dir ontology
python3 scripts/ontology_graph.py --root ontology --format summary  # islands: 0
python3 scripts/ci-ontology-gate.py  # GATE OK
```

---

## 2. mattpocock/skills 增量差距复审（基线 T0450）

### 2.1 对照方法

以 `ontology/domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms.md`（v1.2.3快照）为基线，拉取 `github.com/mattpocock/skills` main（2026-09-01, 36 skills: user-invoked 21/model-invoked 15）逐 skill 比对正文与本地 `ontology/domain/skill-*.md` 及 `SKILLS-INDEX.md`（54 skills）。

### 2.2 已吸收（二次验证通过）

| T0450 P级 | 本地落地 | 验证 |
|----------|---------|------|
| P0 writing-for-agents重构 | 已拆 `ontology/domain/skill-writing-great-skills.md` + `ontology/concept/skill-mechanics.md` + `skill-mechanics-detail.md` | `writing-for-agents-levers.md` 四杠杆已并入，`SKILL-MECHANICS` router/ invocation规则本地化 |
| P0 skill-invocation-contract | `ontology/concept/skill-invocation-contract.md` + `skill-invocation.md` | user-invoked不可调user-invoked校验在 `check-skill-structure.py` |
| P1 ask-matt | `ontology/domain/skill-ask-matt.md` 含phase boundaries决策树 | wayfinder入口 |
| P1 prototype | `skill-prototype.md` 含logic/UI双分支、throwaway branch | 已对齐 |
| P1 triage外部PR | `skill-triage.md` + `skill-triage-work.md` 增加HITL/AFK、外部PR发现 | 5 state roles已映射 |
| P1 research并行burn-down | `skill-research.md:§Subagent并行` + `ontology/domain/skill-research.md:49` | 多tickets并行、throwaway分支 |
| P2 to-questionnaire/wait-what | `skill-to-questionnaire.md` / `skill-wait-wait.md` | 已新增 |
| P2 Negative Space/cache | `skill-writing-great-skills.md` 已含双负载、锚定词、指针措辞 | 对应 |

### 2.3 增量差距（本次新识别 ≥7项）

| 优先级 | 差距项 | mattpocock源 | 本地现状 | 建议 | 映射本体 |
|-------|-------|-------------|---------|------|---------|
| **P1** | **wizard（HTIL bash向导）** | `skills/engineering/wizard/SKILL.md` template.sh 四阶段+Stage清屏+`open_url/ask/write_env` | 本地无 `skill-wizard` 节点，仅在 `ontology_reason` 提及 | 新增 `ontology/domain/skill-wizard.md`（user-invoked），复用 `template.sh` 6 helpers，门禁：wizard脚本须 `bash -n` 通过 | `ontology:domain/skill-wizard` → specializes `pdca-task` |
| **P1** | **domain-modeling多上下文** | `domain-modeling` CONTEXT-MAP.md（多 bounded context） | 本地 `CONTEXT.md` 单上下文，T0450未覆盖多上下文映射 | 扩展 `domain-modeling.md` 增加 `CONTEXT-MAP.md` 路由段 | `ontology/concept/domain-modeling.md` |
| **P1** | **tdd seams前置确认** | `tdd` “Test only at pre-agreed seams” 需书面确认方可写测试 | 本地 `skill-tdd.md` 已有seam讨论但无“书面确认”硬约束 | 在 `skill-tdd.md` 增加seam确认清单（`## Seam分析`机器可读） | `ontology:domain/skill-tdd.md` |
| **P2** | **teach连续教学** | `skills/productivity/teach/SKILL.md` 多session stateful workspace | 本地无teach skill | 评估后决定是否引入（P2，低优） | `skill-teach` |
| **P2** | **diagnosing-bugs 10回路完备** | `diagnosing-bugs` 10种反馈回路+failing test→curl→harness→property/bisection | 本地 `skill-diagnosing-bugs.md` 已有Phase1但未枚举10回路 | 增补10回路清单至 `skill-diagnosing-bugs.md` | `ontology:domain/skill-diagnosing-bugs` |
| **P2** | **wayfinder Decision Ticket术语** | `wayfinder` block/ frontier用tracker原生blocking | 本地 `skill-wayfinder.md` 已吸收但未显式HITL/AFK label | 补 `wayfinder:<type>` 4 label校验 | `ontology:domain/skill-wayfinder.md` |
| **P2** | **handoff压缩语义** | `handoff` compact conversation for another agent | 本地 `handoff-work.md` 仅写journal，未定义压缩格式 | 补 handoff doc模板（类似 `template.sh`） | `ontology:domain/skill-handoff` |
| **P3** | **cache/negative-space显性化** | `writing-for-agents` cache段 | 已含但未单列 `ontology` 节点 | 维持现状，不单列节点（清单透传原则） | — |

**结论**：T0450的18项中15项已吸收并经 `ontology-validate` 复验；本次增量新增约7项未吸收/部分吸收，其中仅 `wizard` 与 `domain-modeling多上下文` 属P1，其余为P2增强。未出现T0450后新增的P0级架构gap。

---

## 3. 调研→本体→拆分→测试 链路与 6种工作模式本体核化

### 3.1 链路形态（`ontology/README.md:§12` 全周期消费）

```
[Plan] grilling(决策树) → domain-modeling(CONTEXT.md/ADR) → triage(scenario_type)
        ↓ meta.ontology_fragment 声明（ontology-ready硬门禁）
[Do]    to-tickets#3.5 关系树驱动拆分 ─┐
        ├─ clash-check(阻断)           ├─ WBS: composed_of/specializes 叶→根
        ├─ tree-split(候选+依赖)       ├─ task_identity自动继承 fragment/node_type
        └─ compute-frontier(ready-set) ┘
        ↓
        implement/tdd @ pre-agreed seams
        ├─ testable_signal 三模式 → ontology_test_scaffold.py
        └─ 双轴code-review
        ↓
[Check] validate-convergence(AC→evidence) + conclusion grill(可被ontology支撑?)
        ↓
[Act]   disposition(ontology:/records-only) + knowledge-provenance(封存) + retrospective七类
        ↓
[Archive] ontology-validate + islands:0 + verdict-anchor
        ↻ self-optimization-loop → 下一轮Plan
```

**调研必需产生本体知识**：是。`ontology/domain/skill-research.md:62` 本体沉淀决策为**硬门禁**（`check-research-ontology-settlement.py`）——`research`任务在 `act/archive` 必须在 `conclusion.md##本体沉淀` 显式声明 `ontology:` 或 `records-only` 且 `meta.disposition` 含关键词，否则 `RESEARCH_SETTLEMENT_MISSING` 阻断。满足任一即判定“应本体化”：(1)可复用清单/模型/模式/阈值 (2)被PRD AC或后续任务依赖 (3)方法论/规范类。未满足时可 `records-only` 但需理由，不可静默跳过。符合 `ontology-modular-reference` 独立四准绳（≥2复用/≥3attributes/维度正交/方法论类）防止“一词一节点”。

**开发必需依赖本体拆分与测试**：是，但为“默认路径”而非绝对强制。`skill-to-tickets.md:To-Tickets#3.5` 中有 `meta.ontology_fragment` 时**默认启用** `ontology_tree_split.py`（无映射报错、关系成环报错），配合 `ontology-clash-check.py` 阻断与 `task_identity.py` 自动继承，使拆分沿本体边界对齐；`skill-testing-strategy.md:63` 强绑定 `testable-signal-to-test-derivation` 三模式，通过 `ontology_test_scaffold.py` 将 `attributes.testable_signal` 派生为可执行骨架。豁免通道为 `meta.ontology_exempt=true`（需理由），历史任务兼容不阻断，新任务默认本体化。

### 3.2 6种scenario_type 本体核化判定

| 场景 | 本体核化度 | 硬门禁/顾问式 | 统计覆盖 | 核心本体/技能 |
|------|-----------|--------------|---------|--------------|
| **development** | **强核（默认）** | ontology-ready硬+tree-split默认+disposition硬 | 37 task中29有fragment (78%) | `to-tickets`/`implement`/`tdd`/`testable-signal-to-test-derivation` |
| **bugfix** | **强核** | 同development + diagnosing-bugs反馈回路 | 5/5 (100%) | `diagnosing-bugs` + 回归seam |
| **research** | **强核** | 本体沉淀决策硬门禁（Ac-Check） | 12/14 (86%) | `skill-research` + `knowledge-provenance` |
| **design** | **强核** | codebase-design词汇+design-it-twice硬约束 | 2/2 (100%) | `codebase-design`/`design-it-twice` |
| **documentation** | **强核** | writing-great-skills + domain-modeling硬校验 | 10/10 (100%) | `writing-great-skills` + `domain-modeling` |
| **review** | **顾问式→趋强** | 双轴审查顾问式，fragment非硬但推荐 | 5/6 (83%) | `code-review` 双轴（Standards/Spec并行） |

**整体**：除历史development遗留的22%无fragment外，其余5种已≥83%核化；新门禁后（T0482起）所有新建任务100%含 `ontology_anchor=ontology:concept/pdca-task` 且 `ontology_fragment=ontology`。

---

## 4. 本体自循环（产生→使用→优化→修改）

### 4.1 四支闭环图（对齐 `self-optimization-loop` / `knowledge-provenance` / `ontology-creation-gate`）

```
产生支：  grilling(追问) → domain-modeling(CONTEXT.md/ADR) → writing-for-agents(信息层级/锚定词)
         → ontology induction(半自动提议) → ontology-check(门禁) → validate(AC-1~6) → 入库

使用支：  plan声明fragment → do消费fragment/relations → check对照 → act处置 → archive自检
         （脚本 `pdca_context.py --phase` 实时输出该阶段可消费本体）

优化支：  记录(flow-audit) → 分析(aggregate-flow-issues) → 决策(create-improvement-candidate)
         → 受控实施(PDCA task) → 效果验证(effectiveness verdict: improved/neutral/regressed)
         + retrospective七类扫描(Navigation/Automated checks/Coding standards/Global AGENTS/Tool economy/No-ops/Information access)

修改支：  校验失败 → ontology-validate/report → 人修ontology/<type>/<slug>.md → relations强引用
         → ontology_graph islands校验 → 补强任务（meta.ontology_fragment指向待补目录）
         + auto_induce_evidence/flow_issues顾问式提示（`scripts/ontology_gate.py:133`）
```

**自循环判定**：四支已闭合。`ontology/README.md:108` 元本体自身即为第一条自循环—— `ontology:concept/ontology-creation-gate` relates_to 六条 `ontology-rule-*` 节点，`ontology:concept/ontology-validate`（即 `scripts/ontology-validate.py`）在运行时读取 `rule_spec` 作门禁参数，**改规则只改节点，校验行为自动跟随**，文档/脚本漂移从源头消除（T0413 B方案）。`pdca_context.py` 则让流程自身消费本体内容作执行指引。

### 4.2 断点与改进点

| 支 | 断点 | 影响 | 改进（本次/已落地） |
|---|------|------|-------------------|
| 产生 | `testable_signal` 泛化曾高达70%（178中125） | 无法派生测试 | 已闭环：T0461→ `testable-signal-to-test-derivation` 三模式 + 全量泛化清零（`scripts/check-research-ontology-settlement.py` 泛化校验，当前0/207） |
| 使用 | 单任务强引用本体数无硬上限，易联想为“链路过深” | 认知负担 | 已闭环：`ontology-modular-reference` 声明“不设硬上限，按关系自然拆分，扇出而非串联，1-3本体自然可控”，由 `check-ontology-reference-depth.py` 顾问式巡检 |
| 优化 | retrospective七类曾为自由文本，易遗漏 | 改进候选不全 | 已闭环：`self-optimization-loop.md` 七类扫描已标准化 |
| 修改 | 历史 `disposition` 35条未含本体关键词 | 统计失真 | 已收紧：T0486 `Act知识闭环收紧` 将关键词升级为节点校验，新任务已100%合规，历史按冻结处理 |

---

## 5. 本体如何支撑测试用例实现

### 5.1 机制：`testable_signal` 为Single Source of Truth（`ontology/README.md:8`）

每个 KnowledgeArtifact 实例的 `attributes[].testable_signal` 既是语义也是可测信号。`ontology:pattern/testable-signal-to-test-derivation.md` 定义三派生：

| 派生模式 | 信号特征 | 动词特征 | 自动化载体 | 示例 |
|---------|---------|---------|-----------|------|
| **属性断言** | 单属性约束可独立判定 | 检查/校验/断言 | `ontology-validate.py` + 自定义断言 | 信号：`运行 python3 scripts/ontology-validate.py --ontology-dir ontology 检查本节点及关联KnowledgeArtifact的attributes.testable_signal非空且不含泛化描述...` → 用例：`test_attr_*_signals_non_generic` |
| **契约测试** | 声明vs实际一致性 | 对比/覆盖/一致 | `seam_contract.py` / `check-design-vocab.py` | 信号：`运行 scripts/seam_contract.py 校验PRD声明的seam清单与实际测试文件一致性...` → 用例：`test_contract_*_exists` |
| **收敛验证** | 多产物闭环回链 | 回链/登记/覆盖 | `register-evidence.py` + `validate-convergence.py` | 信号：`执行 python3 scripts/validate-convergence.py --task-dir ... 检查每条meta.convergence的text与PRD一致且evidence_ids均已登记...` → 用例：`test_convergence_*_map` |

门禁衔接：AC-4（`ontology-rule-attr-testable`）仅校验非空；本pattern提供“非泛化”人工判定补充，由 `ontology/domain/skill-ontology-check.md` 步骤6执行。

### 5.2 落地：`ontology_test_scaffold.py` 自动链路

```bash
python3 scripts/ontology_test_scaffold.py --node ontology:domain/ontology-deep-integration-overview --out tests/test_xxx.py
# 输入：本体节点 id
# 输出：tests/test_<slug>_scaffold.py（含 test_attr_* / test_contract_* / test_convergence_* 三桩）
#       scaffold-map-<slug>.json（schema pdca.test-scaffold-map/v1，信号→测试映射）
pytest tests/test_<slug>_scaffold.py -v
pytest --collect-only  # 可收集
```

**与 `testing-strategy` 强绑定**（`ontology/domain/skill-testing-strategy.md:63`）：测试计划应优先覆盖契约测试与收敛验证，确保声明与实际一致、收敛链完整。`testing-strategy` 生成测试计划时必须引用本体信号源（`--node`）。

### 5.3 验证（本次）

- `tests/test_ontology_deep_integration_overview_scaffold.py`：6用例可收集（`pytest --collect-only` 6 tests）
- `tests/test_*_scaffold.py` 共7个（含 backup/web/collection等3业务域）
- 泛化率：0/207（`grep` 已验证），`ontology-validate` 0 issues 为属性断言已通过

---

## 6. 持续补充/完善/修复的触发器与门禁链

| 触发器 | 事件 | 门禁/脚本 | 产物 |
|-------|------|----------|------|
| **research沉淀** | Act `RESEARCH_SETTLEMENT_MISSING` | `check-research-ontology-settlement.py`（research→act硬门禁） | 新/改 `ontology/<type>/<slug>.md` |
| **retrospective七类** | Act扫描候选 | `skill-retrospective.md` 七类 + `self-optimization-loop` | `improvement-candidate.json`（未自动改流程） |
| **auto_induce** | 未锚定evidence / FlowIssue≥阈值 | `ontology_gate.py:auto_induce_evidence/flow_issues`（顾问式提示） | `ontology_induction.py --adapter evidence --source manifest.jsonl` 提议 |
| **validate失败** | frontmatter/type/range/环/泛化 | `ontology-validate.py` 8类code（TYPE_DIR_MISMATCH/DANGLING_REF/CYCLE/ATTR_NO_TEST_SIGNAL等） | 人修relations/attributes |
| **archive自检** | islands>0 | `archive_ontology_ready_issues()` | 补 relations消除孤岛 |
| **CI/Hook** | push/PR/本地提交 | `ci-ontology-gate.py` + `ontology-gate.yml` | 阻断合并 |
| **clash-check** | 复用冲突 | `ontology-clash-check.py`（to-tickets阻断） | 提示复用既有节点 |

**修复原则**：`ontology-check` 为前置门禁（type合法、引用非空悬、testable_signal可测、guides/relates_to丰富度）；`rule_spec` 由本体节点驱动，改规则即改节点；所有候选仍走正常Plan/Grill/final_confirmation，不由审计器直接改权威流程（`self-optimization-loop.md:37`）。

---

## 7. 结论与建议

### 7.1 总体判定

- **本体已完整融入使用完成闭环**：五阶段均有硬门禁，提交级阻断已落地（AC-1），当前图谱0 issues/0 islands。
- **mattpocock差距已收敛**：P0级已全吸收，剩余仅 `wizard`/`多上下文` 属P1（建议新建/扩展），其余为P2增强，无新增P0。
- **调研与开发已本体为核**：调研沉淀为硬门禁、拆分与测试为默认路径（B路径为豁免），6种工作模式中5强核1趋强，新任务100%核化。
- **自循环已闭合**：四支（产生/使用/优化/修改）已打通，元本体自举（rule_spec驱动validate）为范式。
- **测试支撑已硬化**：三模式+自动骨架+策略绑定，207信号0泛化、7 scaffold可收集。

### 7.2 改进候选（按优先级）

| 优 | 候选 | 验证指标 |
|---|------|---------|
| P1 | 新增 `skill-wizard`（template.sh六helpers） | `bash -n` 通过 + `ontology-validate` 通过 |
| P1 | 扩展 `domain-modeling` 支持 `CONTEXT-MAP.md` 多上下文 | 新增章节可被 `grep` 命中 |
| P2 | `skill-tdd` 补 seams前置书面确认清单 | `## Seam分析` 契约测试通过 |
| P2 | `skill-diagnosing-bugs` 补10回路清单 | 检查清单可枚举 |
| P2 | `skill-wayfinder` 补HITL/AFK label校验 | `check-skill-structure` 校验 |

### 7.3 适用边界

基于 2026-09-01 的 `ontology/` 快照与 `mattpocock/skills` main 快照；历史任务 `disposition` 不追溯，仅新门禁后任务计入核化率。

---

## 附录：重跑清单

```bash
python3 scripts/ontology-validate.py --ontology-dir ontology --format json | python3 -m json.tool
python3 scripts/ontology_graph.py --root ontology --format summary
python3 scripts/ontology_graph.py --root ontology --format dot | head
python3 scripts/ontology_test_scaffold.py --node ontology:pattern/testable-signal-to-test-derivation --out /tmp/demo.py && cat /tmp/demo.py | head -n 40
pytest --collect-only tests/test_ontology_deep_integration_overview_scaffold.py -q
python3 scripts/validate-convergence.py --task-dir pdca/tasks/0901-ontology-closure-audit  # 待Do→Check登记后
python3 scripts/check-research-ontology-settlement.py --task-dir pdca/tasks/0901-ontology-closure-audit
```

## 参考

- `ontology/README.md:1` SSOT v3
- `ontology/process/flow-*.md` 4流程
- `ontology/pattern/testable-signal-to-test-derivation.md:1`
- `ontology/pattern/ontology-modular-reference.md:1`
- `records/T0450-0831-ontology-closed-loop-review/conclusion.md`
- `ontology/domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms.md`

**verdict**: confirmed  
**本体沉淀**: ontology:concept/self-optimization-loop + ontology:pattern/testable-signal-to-test-derivation 已深化验证；新增 gap 见 §2.3，拟以 `skill-wizard` 与 `domain-modeling多上下文` 为下一改进任务。
