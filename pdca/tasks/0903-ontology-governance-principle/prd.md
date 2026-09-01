# 新增准则：本体知识治理本体产生与使用及科学方法论控AI

## 背景

用户新增准则：**本体知识来控制本体知识的产生与使用**——PDCA流程基于PDCA本体知识，调研给予调研方法论产生本体，调研产出本体表由“本体论的本体”要求表达细节；并以科学方法论控制AI产生可验证、可审查等过程。当前虽有 `ontology-creation-gate` `hybrid-methodology` 等，但未显式沉淀为“本体治理本体”的顶层原则，需新增 principle 节点使后续所有本体产出均可被该原则硬校验。

## 目标

- 新增 `ontology/principle/ontology-governs-ontology.md`（`type: principle`，`guides: DomainEntity/Process`），将五条治理句转化为可测 `attributes`
- 使 `ontology-ready` `research Topdown` `PDCA flow` `testable_signal` 均可追溯至该原则

## 范围

- 输入：用户五句准则 + 现有 `ontology-creation-gate` `hybrid-methodology` `research-topdown` `pdca-ontology-ready`
- 输出：1 principle 节点 + 全绿校验
- 不做：不改业务实体结构，不增业务本体

## 功能需求

1. principle 5 attrs：本体控本体产生 / 本体控本体使用 / PDCA基于PDCA本体 / 调研基于调研方法论 / 调研产出本体受本体论本体细节要求
2. 科学方法论控AI：AI产出必须可验证（validate）、可审查（review）、可追溯（provenance）、可复现（scaffold）
3. `guides` 指向 `DomainEntity`/`Process` 使 AC-6 通过

## 非功能需求

- `ontology-validate 0 issues, islands:0`，`grep -R "本体治理" ontology/principle/ontology-governs-ontology.md` 可命中

## 验收标准

- [ ] AC-1 准则已沉淀：`ontology/principle/ontology-governs-ontology.md` 存在且 `validate` 通过且 `guides` 合法
- [ ] AC-2 五条治理可测：5 attrs `testable_signal` 非空且可 `scaffold`
- [ ] AC-3 可追溯：`hybrid-methodology` 等可经 `relates_to` 追至本原则
- [ ] AC-4 全绿：`islands:0` 且 `scaffold` 可产
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:principle/ontology-governs-ontology
ontology:concept/ontology-creation-gate
ontology:domain/ontology-hybrid-methodology
ontology:concept/pdca-ontology-ready
```

## 拆分映射

- 准则沉淀 -> ontology:principle/ontology-governs-ontology
