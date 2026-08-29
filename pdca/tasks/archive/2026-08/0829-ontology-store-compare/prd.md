# PRD：本体存放写法调研比较与方案选型（T0406）

## 背景
用户提出一套"基于 Markdown 的本体草拟工作法"（ONTOLOGY_GUIDE 提案）：以 `type: Class/Individual` + `superClass` 定义身份、正文 `[[wikilink]]`+谓语表达关系、`_meta.yaml` 声明"文件夹不参与本体层级"，目标是"先人后机、脚本一键升华到 OWL/RDF"。

该提案与仓库现有 **SSOT v3**（`pdca.asset/v1` frontmatter + 受控词汇 `domain/entity/concept/process/role/pattern/principle/pitfall/fact/decision` + YAML `relations:` 块 + `ontology-validate` 校验 + 目录即真理 `type==目录名`）存在直接冲突，且会破坏刚建好的 PDCA 元本体（T0405）与 T0402 迁移资产（record identity / redirect 桩）。

经 Grill 收敛，本任务目标为：**在不改动 SSOT v3 与现有节点的前提下，对两套写法做调研比较，产出推荐方案与可选 ONTOLOGY_GUIDE 草案**。

## 目标
- 客观比较两套本体写法的优劣（机器可校验性、人类可读性、OWL/RDF 升级路径、迁移成本、工具生态）。
- 用原型脚本实际验证"一键转 OWL/TTL"在两种写法下的可行性与完整度差异。
- 给出明确推荐（兼容吸收 / 直接替换 / 维持现状）并说明理由与风险。
- 若推荐兼容吸收，产出一份可落 `ontology/ONTOLOGY_GUIDE.md` 的草案（基于现有 `pdca.asset/v1`，仅做可选增强）。

## 范围
- **包含**：静态规范梳理、真实样本标注、原型转换脚本、对比报告、ONTOLOGY_GUIDE 草案、证据登记。
- **排除（明确不动）**：不修订 `task.schema.json` / `ontology-validate` / `transition-phase.py` / `ontology_reason.py` / `ontology_gate.py`；不修改任何现有 ontology 节点；不强制采用 ONTOLOGY_GUIDE 草案。

## 非目标
- 不在此任务内实施 SSOT v3 的任何代码或节点变更（如需，另立任务/ADR）。

## 验收标准
- [ ] AC-1: 产出比较分析报告，覆盖两套写法在 ≥5 个维度（机器可校验性、人类可读性、OWL/RDF 升级路径、迁移成本、工具生态/可视化）的对比，并附现有真实节点样本证据。
- [ ] AC-2: 原型转换脚本能对各选 2–3 个真实样本分别按两套写法转一次 OWL/TTL，输出映射完整度与脆弱度对比（哪些关系/属性可无损映射、哪些丢失）。
- [ ] AC-3: 给出明确推荐方案（兼容吸收 / 直接替换 / 维持），并说明理由、风险与适用边界。
- [ ] AC-4: 若推荐为兼容吸收，产出 `ONTOLOGY_GUIDE.md` 草案（基于 `pdca.asset/v1` + `relations`，可选增补 `superClass/domain/tags`、允许正文 `[[wikilink]]` 作人类可读增强、`_meta.yaml` 声明语义权威=frontmatter+relations）；草案存放于任务目录，标注 DRAFT，不强制采用。
- [ ] AC-5: 报告与草案明确声明"不修订 SSOT v3、不改现有代码/节点"，仅作推荐与可选指南。
- [ ] AC-6: 在 `records/T0406-0829-ontology-store-compare/` 登记证据（报告、原型输出、指南草案）并写 convergence map，供 Check 阶段确认。

## 风险
- 原型转换脚本为一次性验证工具，不纳入长期维护；其输出仅用于佐证比较，不作为验收通过证据。
- 比较结论若倾向"兼容吸收"，草案与现有 `ontology/README.md`（SSOT v3 语义主干）可能有表述重叠，需在草案中显式说明二者关系。
