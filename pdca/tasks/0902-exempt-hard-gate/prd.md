# 豁免硬指标化：exempt白名单与records-only强校验

## 背景

T0492审计：输入豁免7/79(8.9%)、输出豁免1/79，均为历史；新8任务已双100%硬指标。需将 `ontology_exempt` 从开放豁免收紧为自举白名单+理由强校验，把 `records-only` 收紧为理由长度+证据非空的硬校验，使本体成为无例外的硬性指标。

## 目标

- schema新增 `ontology_exempt_reason`，exempt时必填≥20字符
- `ontology_gate.py` 白名单：exempt仅本体自举（关联 `ontology:concept/ontology-creation-gate`）可申，否则硬 `ONTOLOGY_FRAGMENT_MISSING`
- `pdca_core.py` records-only 理由≥20字符校验
- 历史7 exempt补理由，doctor清零

## 范围

- 输入：`schemas/task.schema.json` `scripts/ontology_gate.py` `scripts/pdca_core.py` `scripts/pdca-doctor.py`
- 输出：3脚本+1 schema改动，validate/ci/doctor全绿
- 不做：不删豁免字段，不追溯改历史phase

## 功能需求

1. schema：`meta.ontology_exempt_reason` string minLength20，`if: exempt==true then required`
2. gate：exempt时校验 reason含 `ontology` 且长度≥20，否则报 `ONTOLOGY_EXEMPT_REASON_MISSING`
3. core：`records-only` reason <20报 `DISPOSITION_RECORDS_ONLY_EMPTY`
4. 历史补齐：为7任务补 reason

## 非功能需求

- 门禁零回退：新任务无豁免仍 `fragment=ontology` 通过；有豁免缺理由被拒

## 验收标准

- [ ] AC-1 schema hard：exempt无reason被 `doctor --json` 报 `ONTOLOGY_EXEMPT_REASON_MISSING`
- [ ] AC-2 gate hard：exempt理由<20或不含ontology被 `ontology_gate` 拒
- [ ] AC-3 core hard：records-only短理由被 `DISPOSITION_RECORDS_ONLY_EMPTY`
- [ ] AC-4 历史补齐：7任务补理由后 `doctor` 7→0
- [ ] AC-5 全绿：`ontology-validate 0 issues, islands:0, ci-gate GATE OK`
- [ ] AC-6 收敛 valid:true

## 关联本体节点

```
ontology:concept/ontology-creation-gate
ontology:concept/ontology-validate
ontology:concept/pdca-ontology-ready
```

## 拆分映射

- schema+gate -> ontology:concept/ontology-creation-gate
- core -> ontology:concept/pdca-task
