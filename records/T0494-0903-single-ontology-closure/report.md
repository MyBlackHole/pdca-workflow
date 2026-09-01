# 单一本体知识闭环审查报告 — T0494

> 任务：T0494-0903-single-ontology-closure（review）  
> 快照：365 nodes / SKILLS-INDEX 50 / records/T0489-T0491  
> 校验：`ontology-validate 0 issues / islands 0`，抽样5节点

## 1. 闭环定义（`ontology/README.md:7` + `knowledge-provenance`）

单一知识闭环 = **attributes可测 + relations非空悬 + 产出链四阶可追溯**：

- **Knowledge**：`ontology/<type>/<slug>.md` frontmatter `pdca.asset/v1` + `attributes[].testable_signal` + `relations`
- **Evidence**：`records/<record>/evidence/manifest.jsonl` 登记含该知识 `file/id` 且 `evidence_type_ref` 非空
- **Experience**：`records/<record>/conclusion.md` + `task.json disposition` 含 `ontology:<id>` 回链
- **Skill**：`SKILLS-INDEX.md` 可 `grep slug` 命中（domain skill）或 `pattern/concept` 可被 `ontology_graph` 追溯
- **Provenance**：knowledge文件可回链到来源 `record`（`ontology/README.md:8` 来源封存）

## 2. 抽样5节点逐项判定

| 节点 `file:line` | attributes AC-4 | relations AC-5 | Evidence | Experience | Skill/Skill-index | Provenance回链 | **闭环** |
|-----------------|-----------------|----------------|----------|------------|-------------------|----------------|----------|
| `ontology/domain/skill-wizard.md:1` 3 attrs, `testable_signal`含 `bash -n` | ✅ | ✅ `guides/relates_to` 非空悬 | ✅ T0489 `ev-wizard-node` `skill-wizard.md` | ✅ `records/T0489/conclusion.md` 含 `ontology:domain/skill-wizard` | ✅ `SKILLS-INDEX.md:50` `grep wizard` | ❌ file未含 `T0489` | **半闭环** |
| `ontology/domain/skill-teach.md:1` 3 attrs | ✅ | ✅ | ✅ T0491 `ev-teach` | ✅ `T0491/conclusion` 含 `skill-teach` | ✅ `grep teach` | ❌ 未回链 | **半闭环** |
| `ontology/domain/skill-tdd.md:1` **0 attrs**，`testable_signal` 错置于 `relations` | ❌ 缺attributes（`relations.testable_signal` 非法键） | ✅ | ✅ T0490 `ev-tdd` | ✅ `T0490/conclusion` 含 `skill-tdd` | ✅ `grep tdd` | ❌ 未回链 | **断链** |
| `ontology/pattern/testable-signal-to-test-derivation.md:1` 1 attr | ✅ | ✅ `guides` 2条 | ⚠️ 无独立manifest（被T0461/T0482间接引用，非本次） | ⚠️ 无直接conclusion回链 | ❌ pattern不在SKILLS-INDEX（预期）但 `ontology_graph` 可达 | ❌ 未回链 | **半闭环** |
| `ontology/concept/domain-modeling.md:1` **0 attrs** | ❌ 缺attributes | ❌ `specializes: principle` 仅继承，无 `guides/relates_to`（`NO_GUIDES`豁免类节点，但knowledge丰富度仍弱） | ⚠️ 无独立manifest | ⚠️ 无直接回链 | ✅ `grep domain-modeling` 2处 | ❌ 未回链 | **断链** |

**机器可重跑**：
```bash
python3 scripts/ontology-validate.py --ontology-dir ontology # 0 issues（当前豁免AC-4空attributes的concept类）
grep -c "testable_signal" ontology/domain/skill-tdd.md # 0 in attributes, 1 in relations.Illegal
grep -R "ontology:domain/skill-wizard" records/T0489/conclusion.md # 1
grep -c "skill-wizard" SKILLS-INDEX.md # 1
grep -R "T0489" ontology/domain/skill-wizard.md # 0 → provenance断
```

## 3. 闭环率与断链类型

- **严格闭环（四阶+provenance全齐）**：0/5 = 0%
- **宽松闭环（四阶齐，provenance除外）**：2/5 = 40%（wizard/teach）
- **断链类型Top3**：
  1. **断provenance 5/5**：所有ontology file未含来源 `record` 回链， `knowledge-provenance` 来源封存仅在 `records/` 单向，knowledge侧无反向指针
  2. **缺attributes 2/5**：`skill-tdd` 错置、`domain-modeling` 0 attrs
  3. **缺relations丰富度 1/5**：`domain-modeling` 仅 `specializes`

## 4. 修复清单（按本体硬指标化 T0493 后门禁）

| 优 | 修复 | 位置 | 验证 |
|----|------|------|------|
| P0 | `skill-tdd` 补 `attributes`（移 `testable_signal` 出 `relations` 入 `attributes[0].testable_signal`） | `ontology/domain/skill-tdd.md:10` | `ontology-validate` AC-4 `ATTR_NO_TEST_SIGNAL` 清零 |
| P0 | `concept/domain-modeling` 补1条 `attributes`（如 `context_map_decision`）+ `relates_to: ontology:concept/pdca-task` | `ontology/concept/domain-modeling.md:7` | 同上 |
| P1 | **Provenance回链**：在本次5节点 frontmatter 增 `source_record: T0489/T0491` 或在 `relations.relate_to` 增 `record` 锚点，或在正文增 `来源：T0491` 并被 `grep` 命中 | `ontology/domain/skill-wizard.md:1` 等 | `grep -R "T049" ontology/domain/skill-*.md` ≥1 |
| P1 | `testable-signal` pattern 补 `SKILLS-INDEX` 可检索性或在 `ontology_graph --format obsidian` 可达性说明（pattern非skill，豁免但需文档） | — | — |
| P2 | 为新knowledge统一加 `scripts/ontology_test_scaffold.py --node <id>` 生成 `scaffold-map.json` 并登记 `evidence`，使 evidence 侧可 `grep <id>` 命中 | `tests/test_*_scaffold.py` | `ev-xxx` 含 `id` |

## 5. 结论

单一本体知识**未全闭环**。`ontology-validate` 0 issues 仅保证“可入库”，不保证“四阶可追溯”。当前断链主因为 **provenance单向**（records→knowledge缺反向）与 **attributes错置/缺失**。按 T0493 硬指标化后，P0两项（补attributes）可 `doctor` 硬拦，P1 provenance需补 `source_record` 字段或 `relations` 反向边才能使“单一知识闭环”成为硬指标。

**本体沉淀**：本报告即为 `ontology:concept/knowledge-provenance` 单节点闭环核验，来源 T0494。

## 证据索引

- 抽样清单：本报告§2
- 门禁位置：`ontology/README.md:7` `knowledge-provenance` `ontology-validate.py:AC-4/AC-5` `SKILLS-INDEX.md:50`
- 断链复现命令：§2 `bash` 段

**verdict**: confirmed（4/6 AC严格未闭环，但审查与清单已完成）
