---
schema: pdca.asset/v1
id: ontology:concept/auto-induce-evidence
type: concept
layer: Knowledge
status: active
summary: evidence→ontology 自动反哺：Act 阶段扫描未锚定 evidence 并经 induction 生成本体候选
relations:
  specializes:
  - ontology:concept/pdca-continuous-improvement
  relates_to:
  - ontology:concept/pdca-evidence
  - ontology:concept/self-optimization-loop
  - ontology:concept/knowledge-provenance
---

# evidence→ontology 自动反哺（auto-induce-evidence）

Act 阶段扫描 `records/<record>/evidence/manifest.jsonl`，对未锚定到 `pdca-evidence` 子类型的知识型 evidence（`pattern`/`principle`/`pitfall`/`fact`/`decision`/`concept`/`entity`/`process`）提示可反哺本体，调用 `ontology_induction.py --adapter evidence` 生成候选，经 HITL 审查后写入 `ontology/`。

- **触发**：`ontology_gate.auto_induce_evidence(task, root)` 在 `phase ∈ {act, archive}` 且 manifest 存在时执行，顾问式不阻断。
- **输入**：`evidence/manifest.jsonl` 每条 entry 的 `kind` / `evidence_type_ref` / `criteria`。
- **输出**：`AUTO_INDUCE_CANDIDATE` Issue，携带可执行指引 `python3 scripts/ontology_induction.py --adapter evidence --source <manifest> --out print`。
- **HITL**：候选仅打印 frontmatter，不直接写入 `ontology/`；须经 `ontology-check` + `ontology-validate.py` 后落盘。
- **幂等**：同一 evidence 多次扫描产生同一 candidate id，重复运行结果一致（AC-4）。

## 决策背景
- 背景：本体自循环完整度约 70%，Act 知识沉淀依赖人工判断，evidence 与本体缺口无自动提示。
- 决策：新增 EvidenceAdapter 与 Act 阶段顾问式检查，闭合 `evidence → candidate → ontology` 环路。

## 来源
- `T0456-0831-ontology-auto-induce`
