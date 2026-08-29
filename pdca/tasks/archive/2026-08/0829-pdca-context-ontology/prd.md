# PRD — T0409 让 PDCA 执行指引层实时消费 PDCA 元本体知识

## 背景
T0405 让 `ontology_reason.py` 在**控制规则层**直接读取 PDCA 元本体驱动转换/准入/证据识别。但：
1. **执行指引层仍是静态 flow SKILL 文本**，agent 执行时不实时查阅 `pdca-*.md` 的**知识内容**；
2. **PDCA 元本体内容稀疏**——节点仅有 frontmatter（一句话 summary + relations），正文为空，直接消费只能拿到"一句话"，深化效果有限。

本任务分两步：**先补全元本体正文知识**，再让执行层实时消费它。

## 目标
1. **补内容**：充实 `pdca-*` 节点正文（阶段定义/目的/进出条件/关键活动/对应 flow 文件；门禁理由、verdict 含义、证据含义、AC 含义），使元本体成为有知识含量的资产；`ontology-validate` 仍通过。
2. **接消费**：新增 `scripts/pdca-context.py` 按 `--phase` 读取并输出该阶段知识（定义 + 准入 + 合法后继 + 关联概念正文），注入 `transition-phase` 与 flow SKILL 入口，使执行指引层直接消费 PDCA 元本体知识。

## 范围
- 充实节点：`ontology/entity/phase-{plan,do,check,act,archive}.md`、`ontology/concept/pdca-gate.md`、`pdca-gate-do.md`、`pdca-ontology-ready.md`、`pdca-verdict.md`、`pdca-evidence.md`、`pdca-acceptance-criterion.md`、`pdca-task.md`（正文补充，不动 frontmatter 的 id/type/relations，避免破坏 reasoner）。
- 新增 `scripts/pdca-context.py`（复用 `ontology_reason`）。
- 修改 `scripts/transition-phase.py` 仅追加"转换成功后打印指引"，不改门禁逻辑。
- 修改 `flows/flow-plan/do/check/act/SKILL.md` 入口注入指令。
- 新增 `tests/test_pdca_context.py`。
- 同步 `docs/ONTOLOGY_GUIDE.md`。

## 非目标
- 不改 `ontology_reason.py` 推理逻辑（仅调用）。
- 不改 `task.schema.json` / `ontology-validate` 规则 / 关卡判定。

## 验收标准
- [ ] AC-1：PDCA 元本体正文已充实——`phase-{plan,do,check,act,archive}` 各含定义/目的/进出条件/关键活动/对应 flow 文件；`pdca-gate`/`pdca-gate-do`/`pdca-ontology-ready`/`pdca-verdict`/`pdca-evidence`/`pdca-acceptance-criterion` 含理由/含义；`ontology-validate` 仍通过。
- [ ] AC-2：`scripts/pdca-context.py` 接受 `--phase`，输出该阶段（a）定义（来自 `phase-<p>.md` 正文）、（b）准入条件（`ontology_reason.admission_conditions`）、（c）合法后继（`ontology_reason.transition_targets`）、（d）关联概念知识（`pdca-gate-<p>` 及其 `relates_to` 节点正文，如门禁理由/verdict 含义）；元本体缺失时回退硬编码提示而不崩溃。
- [ ] AC-3：`scripts/transition-phase.py` 转换成功后打印 `pdca-context --phase <to>` 指引（仅输出，不改门禁逻辑）；不影响既有转换语义。
- [ ] AC-4：`flows/flow-plan/do/check/act/SKILL.md` 入口增加"运行 `python3 scripts/pdca-context.py --phase <本阶段>` 读取 PDCA 元本体给出的本阶段定义/准入/合法后继作为执行指引"的指令。
- [ ] AC-5：`tests/test_pdca_context.py` 断言五个 phase 输出非空且含阶段标识与关键正文片段，并与 `ontology_reason` 的准入/后继结果一致；全量 `pytest` 通过。
- [ ] AC-6：`resolve-ai-friendliness-route.py --verify-document` 通过；`docs/ONTOLOGY_GUIDE.md` 增加"PDCA 流程现实时消费元本体知识"章节，说明补内容与接入点、回退策略。

## 风险与缓解
- 风险：充实正文时误改 frontmatter 的 `id/type/relations`，破坏 reasoner。
  缓解：仅追加 `# 标题` 之下的正文；CI 前跑 `ontology-validate` 与既有 `ontology_reason` 测试确保无回归。
- 风险：`transition-phase.py` 改动引入回归。
  缓解：仅追加打印；门禁逻辑不动；pytest 覆盖。
- 风险：元本体缺失导致 pdca-context 报错阻断流程。
  缓解：与 `ontology_reason` 一致做无元本体回退，绝不抛异常中断转换。
